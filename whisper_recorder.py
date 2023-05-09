import pygame
import time


def play_sound(file):
    pygame.mixer.init()
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        time.sleep(1)


if __name__ == "__main__":

    while True:
        try:
            sound_file = 'audio.mp3'
            play_sound(sound_file)
        except KeyboardInterrupt:
            print("Terminando el programa.")
            break
        except Exception as e:
            print("Ocurrió un error:", e)
