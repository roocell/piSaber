# use pygame to play wav files
# pip3 install pygame
# pip3 install pyalsaaudio
# sudo apt-get install libsdl2-mixer-2.0-0

import pygame
import alsaaudio
import asyncio
from logger import log as log

sounds = {}
sounds["on"] = "ON.wav"
sounds["off"] = "OFF.wav"

path = "/home/pi/piSaber/sounds/"
on = path + "ON.wav"
off = path + "OFF.wav"


class Audio:
    def __init__(self):
        scanCards = alsaaudio.cards()
        log.debug("cards: {}".format(scanCards))
        for card in scanCards:
            scanMixers = alsaaudio.mixers(scanCards.index(card))
            log.debug("mixers: {}".format(scanMixers))

        m = alsaaudio.Mixer('Headphone')
        m.setvolume(90) # range seems to be non-linear

        pygame.mixer.init()

    async def play_on(self):
        pygame.mixer.Sound(on).play()
    async def play_off(self):
        pygame.mixer.Sound(off).play()

if __name__ == '__main__':
    pygame.mixer.init()
    sound = pygame.mixer.Sound('/home/pi/piSaber/sounds/ON.wav')
    playing = sound.play()
    while playing.get_busy():
        pygame.time.delay(100)