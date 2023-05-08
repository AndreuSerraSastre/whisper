# install dependencies
# pip install PyAudio
# pip install numpy
# pip install pydub
# pip install openai-whisper
# (En el powershell como admin: Set-ExecutionPolicy Bypass -Scope Process -Force; `iex((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1')))
# choco install ffmpeg
# pip install gTTS

import pyaudio
import numpy as np
import time
from collections import deque
from pydub import AudioSegment
import whisper
from pydub import AudioSegment
from pydub.playback import play
from gtts import gTTS
import random
import string

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


def play_text(text):
    name = "text_to_speech.mp3"
    myobj = gTTS(text=text, lang='es', slow=False)
    myobj.save(name)
    sound = AudioSegment.from_file(name, format="mp3")
    play(sound)


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


def audio_to_text():
    print("Transcribiendo el audio...")
    result = model.transcribe("audio.mp3", verbose=True,
                              temperature=(
                                  0.0, 0.2, 0.4, 0.6, 0.8, 1.0),
                              compression_ratio_threshold=2.4,
                              logprob_threshold=-1.0,
                              no_speech_threshold=0.6,
                              condition_on_previous_text=True,
                              initial_prompt=None,
                              word_timestamps=False,
                              prepend_punctuations="\"'“¿([{-",
                              append_punctuations="\"'.。,，!！?？:：”)]}、",
                              language="es",  # Indica el idioma en español
                              )
    return result["text"]


def process_response(text):
    words = clean_text(text).split()
    if (words[0].lower() == "nada"):
        return "Okey"
    return "No entendí tu pregunta"


def clean_text(text):
    punctuation = string.punctuation + "¡¿"
    text_cleaned = text.translate(str.maketrans("", "", punctuation))
    return text_cleaned.lower()


def get_text_after_robot(text):
    words = clean_text(text).split()
    try:
        robot_index = words.index("robot")
        text_after_robot = " ".join(words[robot_index + 1:])
        return text_after_robot
    except ValueError:
        return ""


def do_it(text):
    global pending_quest
    greetings = ["Hola", "¿Si?", "Dime", "¿Qué quieres?",
                 "¿Necesitas algo?", "¿En qué puedo ayudarte?"]

    # Eliminar signos de puntuación
    words = clean_text(text).lower().split()

    say_robot = False
    result = ""

    # Extraer la pregunta del usuario
    question = get_text_after_robot(text)
    print("question:", question, len(question))

    # Buscar palabras clave en el texto
    if "robot" in words:
        if len(question) == 0:
            result = random.choice(greetings)
            say_robot = True
            pending_quest = True
        else:
            result = process_response(text)
            say_robot = True
            pending_quest = False
    elif pending_quest:
        result = process_response(text)
        pending_quest = False
        say_robot = True

    if say_robot:
        print("Respuesta: ", result)
    return result, say_robot


if __name__ == "__main__":
    model = whisper.load_model("tiny")

    while True:
        try:
            # record audio
            audio_data = record_audio()
            save_audio(audio_data, "audio.mp3")

            # audio to text
            text = audio_to_text()
            print("Transcripción:", text)

            # audio to action
            result, do = do_it(text)

            if (do):
                # text to audio
                play_text(result)

        except KeyboardInterrupt:
            print("Terminando el programa.")
            break
        except Exception as e:
            print("Ocurrió un error:", e)
