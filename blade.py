# this will contain the blade animations
# every function call will cancel the previous task (if it exists)
# then create another task for the new animation
# this will allow us to circumvent the previous animation with a new one
import timer
import sys
from logger import log as log
import asyncio
import time

BLADE_IDLE = 0
BLADE_OFF = 1
BLADE_ON = 2

# brightness is just a factor of colour
def set_brightness(colour, brightness):
    return tuple(int(brightness*c) for c in colour)

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

    async def idle(self):
        log.debug("blade idle")
        try:
            # this is the idling animation
            # it loops forever until interrupted by another animation
            # keep pixel values, but cycle through the brightness
            # of them to create an illusion that it's alive
            while True:
                for i in range(self.num_pixels):
                    self.pixels[i] = set_brightness(self.colour, 0.8)
                    if i > 0:
                        self.pixels[i-1] = set_brightness(self.colour, 0.2)
                    self.pixels.show()
                    await asyncio.sleep(self.onoffdelay/self.num_pixels)
        except Exception as e: log.error(">>>>Error>>>> {} ".format(e))

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

