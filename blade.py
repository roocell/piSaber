# this will contain the blade animations
# every function call will cancel the previous task (if it exists)
# then create another task for the new animation
# this will allow us to circumvent the previous animation with a new one
import timer
import sys
from logger import log as log
import asyncio
import time
import random

green =     (0,   255, 0)
red =       (255, 0,   0)
blue =      (0,   98,  255)
yellow =    (255, 221, 0)
black =     (0,   0,   0)
purple =    (238, 0,   255)
orange =    (255, 100,0)
white   =   (255, 255, 255)
brightwhite   =   (255, 255, 255)
indigo =    (29, 0, 51)
violet =    (155,38,182)

BLADE_IDLE = 0
BLADE_OFF = 1
BLADE_ON = 2
BLADE_CRASH = 3

# brightness is just a factor of colour
def set_brightness(colour, brightness):
    # find largest value and scale up to 255
    scale = max(colour)/255 # this is 100% brightness
    scale /= brightness
    return tuple(int(c/scale) for c in colour)

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b) # we have neopixel.GRB


# NeoFire
# https://github.com/RoboUlbricht/arduinoslovakia/blob/master/neopixel/neopixel_fire01/neopixel_fire01.ino
def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))

def NeoFire_Draw(pixels):
    pixels.fill((0,0,0))
    for i in range(len(pixels)):
        fire_color = ( 80,  35,  00)
        NeoFire_AddColor(pixels, i, fire_color)
        r = randoma(80);
        diff_color = pixels.fill( r, r/2, r/2)
        NeoFire_SubstractColor(i, diff_color)
        pixels.show()

def NeoFire_AddColor(pixels, position, color):
    blended_color = NeoFire_Blend(pixels[position], color)
    pixels[position] = blended_color

def NeoFire_SubstractColor(pixels, position, color):
    blended_color = NeoFire_Substract(pixels[position], color)
    pixels[position] = blended_color

def NeoFire_Substract(color1, color2):
    r1 = (color1[0] >> 16)
    g1 = (color1[1] >>  8)
    b1 = (color1[2] >>  0)

    r2 = (color2[0] >> 16)
    g2 = (color2[1] >>  8)
    b2 = (color2[2] >>  0)

    r = r1 - r2
    g = g1 - g2
    b = b1 - b2
    if r < 0: r = 0
    if g < 0: g = 0
    if b < 0: b = 0

    return (r, g, b)

def NeoFire_Blend(color1, color2):
    r1 = (color1[0] >> 16)
    g1 = (color1[1] >>  8)
    b1 = (color1[2] >>  0)

    r2 = (color2[0] >> 16)
    g2 = (color2[1] >>  8)
    b2 = (color2[2] >>  0)
    return (constrain(r1+r2, 0, 255), constrain(g1+g2, 0, 255), constrain(b1+b2, 0, 255))

class Blade:
    def __init__(self, pixels, colour):
        self.pixels = pixels
        self.num_pixels = len(pixels)
        log.debug("created blade with {} pixels with colour {}".format(self.num_pixels, colour))
        self.task = False
        self.colour = colour
        self.state = BLADE_OFF
        self.onoffdelay = 0.01

        #self.pixels.fill((155, 155, 155))
        #self.pixels.show()

    def get_state(self):
        return self.state

    def clear(self):
        self.pixels.fill((0, 0, 0)) # off
        self.pixels.show()

    # when lightsabers hit
    async def crash(self):
        try:
            # entire blade to 100% brightness
            # grab previous values
            for j in range(2): # flash a couple of times
                for i in range(self.num_pixels):
                    #self.pixels[i] = set_brightness(self.pixels[i], 1.0)
                    self.pixels[i] = brightwhite
                self.pixels.show()
                await asyncio.sleep(0.1) # maintain for a bit
                self.pixels.fill((0,0,0))
                self.pixels.show()
                await asyncio.sleep(0.03) # maintain for a bit

            # 100% brightness in middle and extend outwards            
            # middle = int(self.num_pixels/2)
            # lastp = lastdp = middle
            # for i in range(middle,self.num_pixels):
            #     if lastp != middle:
            #         # make previous pixels darker
            #          self.pixels[lastp] = set_brightness(self.pixels[i], 0.1)
            #          self.pixels[lastdp] = set_brightness(self.pixels[i], 0.1)
            #     downp = self.num_pixels-i
            #     if downp < 0: downp = 0
            #     self.pixels[i] = set_brightness(self.pixels[i], 1.0)
            #     self.pixels[downp] = set_brightness(self.pixels[i], 1.0)                
            #     self.pixels.show()
            #     lastp = i
            #     lastdp = downp
            #     await asyncio.sleep(0.001)

            # return to idle
            self.task = asyncio.create_task(self.idle())
        except Exception as e: log.error(">>>>Error>>>> {} ".format(e))


    async def idle_pulse(self):
        log.debug("blade idle")
        try:
            # this is the idling animation
            # it loops forever until interrupted by another animation
            # keep pixel values, but cycle through the brightness
            # of them to create an illusion that it's alive
            while True:
                for i in range(self.num_pixels):
                    self.pixels[i] = set_brightness(blue, 0.8)
                    if i > 0: prevp = i-1
                    else:     prevp = self.num_pixels-1
                    self.pixels[prevp] = set_brightness(self.colour, 0.2)
                    self.pixels.show()
                    await asyncio.sleep(self.onoffdelay/self.num_pixels)
        except Exception as e: log.error(">>>>Error>>>> {} ".format(e))

    async def idle_breath(self):
        log.debug("blade breath")
        try:
            while True:
                # go from 100% brightness to 50%
                for b in range(6,2,-1):
                    for i in range(self.num_pixels):
                        self.pixels[i] = set_brightness(self.colour, b/10)
                    self.pixels.show()
                    await asyncio.sleep(0.1)
                # go from 50% brightness to 100%
                for b in range(2,6,1):
                    for i in range(self.num_pixels):
                        self.pixels[i] = set_brightness(self.colour, b/10)
                    self.pixels.show()
                    await asyncio.sleep(0.1)
        # this error spits out if the task is cancelled
        except Exception as e: log.error(">>>>Error>>>> {} ".format(e))

    async def idle_rainbow_cycle(self):
        try:
            while True:
                for j in reversed(range(255)):
                    for i in range(self.num_pixels):
                        pixel_index = (i * 256 // self.num_pixels) + j
                        self.pixels[i] = wheel(pixel_index & 255)
                    self.pixels.show()
                    await asyncio.sleep(0.001)
        except Exception as e: log.error(">>>>Error>>>> {} ".format(e))

    async def idle_flame_old(self):
        try:
            # start at yellow and slowly reduce green
            # to get to red
            r = 255
            g = 221
            b = 0
            flame = []
            for i in range(self.num_pixels):
                flame.append((r, g, b))
            while True:
                for j in reversed(range(255)):
                    for i in range(self.num_pixels):
                        self.pixels[i] = flame[i]
                    self.pixels.show()
                await asyncio.sleep(0.01)
                # shift flame values

        except Exception as e: log.error(">>>>ib Error>>>> {} ".format(e))

    async def idle_flame(self):
        try:
            await NeoFire_Draw(self.pixels)
        except Exception as e: log.error(">>>>ib Error>>>> {} ".format(e))

    async def idle(self):
        await self.idle_rainbow_cycle()

    async def shutdown(self):
        log.debug("blade shutdown")
        # retract lights
        for i in range(self.num_pixels):
            self.pixels[self.num_pixels-i-1] = (0, 0, 0) # off
            self.pixels.show()
            await asyncio.sleep(self.onoffdelay)

    async def startup(self):
        log.debug("blade startup")
        # make sure they're off first
        self.clear()
        # light one at a time
        for i in range(self.num_pixels):
            self.pixels[i] = self.colour
            self.pixels.show()
            await asyncio.sleep(self.onoffdelay)
        self.task = asyncio.create_task(self.idle())

    async def animate(self, option):
        log.debug("blade animate {}".format(option))
        if self.task:
            self.task.cancel()
        if option == BLADE_ON:
            task_coroutine = self.startup
            self.state = BLADE_ON
        elif option == BLADE_OFF:
            task_coroutine = self.shutdown
            self.state = BLADE_OFF
        elif option == BLADE_CRASH and self.state == BLADE_ON:
            task_coroutine = self.crash
            # will go back to idle after
        else:
            task_coroutine = self.idle
        self.task = asyncio.create_task(task_coroutine())

    ###### EARLY PROTOTYPES ######

    def green_startup():
        # light one at a time
        for i in range(appd.num_pixels):
            pixels[i] = green
            pixels.show()
            time.sleep(0.02)

    def white_startup():
        # light one at a time
        for i in range(appd.num_pixels):
            pixels[i] =white
            pixels.show()
            time.sleep(0.02)

    def snake():
        pixels.fill(black)
        # pixels[5] = blue
        # pixels[6] = green
        # pixels[7] = blue
        # pixels[12] = green
        # pixels[13] = blue
        # pixels[14] = green
        # pixels[15] = blue
        # pixels[16] = green
        # pixels[17] = blue
        for i in range(appd.num_pixels):
            if i%2 == 0: # i is an even number
                pixels[i] = green
            else:
                # i is an odd number
                pixels[i] = blue
        pixels.show()

    def rainbow_blade():
        # Red, orange, yellow, green, blue, indigo, violet
        rainbow = [red, orange, yellow, green, blue, indigo, violet]
        for i in range(appd.num_pixels):
            r = rainbow[int(i/7)%7]
            pixels[i] = r
        pixels.show()    

