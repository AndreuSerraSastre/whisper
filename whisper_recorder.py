import os


def play_sound(filename):
    os.system(f'aplay {filename}')


if __name__ == "__main__":

    while True:
        try:
            play_sound('audio.mp3')
        except KeyboardInterrupt:
            print("Terminando el programa.")
            break
        except Exception as e:
            print("Ocurrió un error:", e)
