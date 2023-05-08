import pyaudio
import numpy as np
import time
from collections import deque
from pydub import AudioSegment

FORMAT = pyaudio.paInt16
CHANNELS = 1
SILENCE_THRESHOLD = 2500
SILENCE_DURATION = 2.5
BUFFER_DURATION = 1  # 1 segundo de buffer antes de grabar

pending_quest = False


def get_default_device_info():
    audio = pyaudio.PyAudio()
    device_index = audio.get_default_input_device_info()["index"]
    device_info = audio.get_device_info_by_index(device_index)
    audio.terminate()
    return device_info


device_info = get_default_device_info()

RATE = int(device_info["defaultSampleRate"])
CHUNK = 4096


def is_silent(audio_data, threshold):
    return np.mean(np.abs(audio_data)) < threshold


def record_audio():
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True, frames_per_buffer=CHUNK)
    frames = []
    pre_buffer = deque(maxlen=int(BUFFER_DURATION * RATE / CHUNK))

    print("Escuchando...")
    silence_start_time = None
    recording = False
    speech_started = False

    while True:
        data = stream.read(CHUNK)
        audio_data = np.frombuffer(data, dtype=np.int16)

        if is_silent(audio_data, SILENCE_THRESHOLD):
            if recording:
                if silence_start_time is None:
                    silence_start_time = time.time()
                elif time.time() - silence_start_time > SILENCE_DURATION:
                    break
            else:
                pre_buffer.append(data)
                continue
        else:
            if not recording:
                recording = True
                speech_started = True
                print("Grabando...")
                frames.extend(pre_buffer)
            silence_start_time = None

        if speech_started:
            frames.append(data)

    stream.stop_stream()
    stream.close()
    audio.terminate()

    return b"".join(frames)


def save_audio(audio_data, output_file):
    audio_segment = AudioSegment(
        data=audio_data, sample_width=2, channels=1, frame_rate=RATE)
    audio_segment.export(output_file, format="mp3")


if __name__ == "__main__":

    while True:
        try:
            # record audio
            audio_data = record_audio()
            save_audio(audio_data, "audio.mp3")

        except KeyboardInterrupt:
            print("Terminando el programa.")
            break
        except Exception as e:
            print("Ocurrió un error:", e)
