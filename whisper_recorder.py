from pydub import AudioSegment
from pydub.playback import play


def play_text():
    name = "audio.mp3"
    sound = AudioSegment.from_file(name, format="mp3")
    play(sound)


if __name__ == "__main__":

    while True:
        try:
            play_text()

        except KeyboardInterrupt:
            print("Terminando el programa.")
            break
        except Exception as e:
            print("Ocurrió un error:", e)
