# use pygame to play wav files
# pip3 install pygame
# pip3 install pyalsaaudio
# sudo apt-get install libsdl2-mixer-2.0-0

import pygame
import alsaaudio
import asyncio
from logger import log as log
import random

sounds = {}
sounds["on"] = "ON.wav"
sounds["off"] = "OFF.wav"

path = "/home/pi/piSaber/sounds/"
on = path + "ON.wav"
off = path + "OFF.wav"
hum = path + "HUM.wav"
there_is_no_try = path + "there-is-no-try.wav"
darkside = path + "vader.wav"

short_swings = [
     path + "SWS1.wav",
     path + "SWS2.wav",
     path + "SWS3.wav",
     path + "SWS4.wav",
     path + "SWS5.wav"
]
long_swings = [
     path + "SWL1.wav",
     path + "SWL2.wav",
     path + "SWL3.wav",
     path + "SWL4.wav"
]

hits = [
     path + "SK1.wav",
     path + "SK2.wav",
     path + "SK3.wav",
     path + "SK4.wav",
     path + "SK5.wav",
     path + "SK6.wav",
     path + "SK7.wav",
     path + "SK8.wav",
     path + "scream.wav"
]

class Audio:
    def __init__(self):
        scanCards = alsaaudio.cards()
        log.debug("cards: {}".format(scanCards))
        for card in scanCards:
            scanMixers = alsaaudio.mixers(scanCards.index(card))
            log.debug("mixers: {}".format(scanMixers))

        m = alsaaudio.Mixer('Headphone')
        m.setvolume(90) # range seems to be non-linear

        # increase buffer to avoid underruns
        # but this also slows it down
        pygame.mixer.init(buffer=2048)

        pygame.mixer.music.load(hum)
        pygame.mixer.music.play(-1)
        pygame.mixer.music.pause()

        # load sounds files at startup to make it 
        # faster to play
        self.short_swings = []
        for s in short_swings:
            self.short_swings.append(pygame.mixer.Sound(s))

    async def play_on(self):
        pygame.mixer.Sound(on).play()
    async def play_off(self):
        pygame.mixer.Sound(off).play()

    async def play_hit(self):        
        pygame.mixer.Sound(hits[random.randrange(0, len(hits))]).play()

    async def play_longswing(self):        
        pygame.mixer.Sound(short_swings[random.randrange(0, len(short_swings))]).play()

    async def play_shortswing(self):        
        self.short_swings[random.randrange(0, len(short_swings))].play()
    
    async def play_swing(self):        
        await self.play_shortswing()

    async def play_startup(self):
       #pygame.mixer.Sound(there_is_no_try).play()
       pygame.mixer.Sound(darkside).play()

    async def start_hum(self):
       pygame.mixer.music.unpause()
    async def stop_hum(self):
       pygame.mixer.music.pause()


if __name__ == '__main__':
    pygame.mixer.init()
    sound = pygame.mixer.Sound('/home/pi/piSaber/sounds/ON.wav')
    playing = sound.play()
    while playing.get_busy():
        pygame.time.delay(100)
