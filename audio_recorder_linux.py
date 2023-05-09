import pyaudio
import wave

# Configuración
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
DURATION = 5  # Duración de la grabación en segundos
FILE_NAME = "audio.wav"

# Inicializar PyAudio
audio = pyaudio.PyAudio()

# Configurar el flujo de grabación
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)

print("Grabando...")

frames = []

# Grabar datos
for i in range(0, int(RATE / CHUNK * DURATION)):
    data = stream.read(CHUNK)
    frames.append(data)

print("Grabación terminada.")

# Detener el flujo y cerrar PyAudio
stream.stop_stream()
stream.close()
audio.terminate()

# Guardar la grabación en un archivo .wav
waveFile = wave.open(FILE_NAME, 'wb')
waveFile.setnchannels(CHANNELS)
waveFile.setsampwidth(audio.get_sample_size(FORMAT))
waveFile.setframerate(RATE)
waveFile.writeframes(b''.join(frames))
waveFile.close()

print(f"Archivo de audio guardado como {FILE_NAME}")
