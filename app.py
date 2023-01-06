#!/usr/bin/env python
import time
import timer
import board
import neopixel
import RPi.GPIO as GPIO
import os
import asyncio
from logger import log as log
import signal
import motion
import blade

### DEFINES ############################
green =     (0,   255, 0)
red =       (255, 0,   0)
blue =      (0,   98,  255)
yellow =    (255, 221, 0)
black =     (0,   0,   0)
purple =    (238, 0,   255)
orange =    (255, 100,0)
white   =   (255, 255, 255)
indigo =    (29, 0, 51)
violet =    (155,38,182)

############ GLOBAL APPDATA ##################
class app_data:
    def __init__(self):
        self.num_pixels = 61
        self.pixel_pin = board.D12
        self.audiopath = "/home/roocell/p/audio/"
        self.mainloopcnt = 0
        self.button = 26 # GPIO26
appd = app_data()

###########################################
### catch a break signal to turn off blade
def sig_handler(signum, frame):
    log.debug("Ctrl-C was pressed")
    pixels.fill((0, 0, 0)) # start off
    pixels.show()
    time.sleep(0.5)
    exit()
signal.signal(signal.SIGINT, sig_handler)

### BUTTON #############################
async def button_event_async(pin):
    # https://www.joeltok.com/blog/2020-10/python-asyncio-create-task-fails-silently
    # any syntax error inside our coroutine will fail silently.
    # we have to explicitly raise any exceptions here
    try:
        if appd.blade.get_state() == blade.BLADE_OFF:
            await appd.blade.animate(blade.BLADE_ON)
        else:
            await appd.blade.animate(blade.BLADE_OFF)
    except Exception as e: log.error(">>>>Error>>>> {} ".format(e))

def button_event(pin):
    # GPIO event is not on mainthread so we have to store the main event loop in appd
    # and then use it here
    # pulled down in HW
    # - False = button pushed
    # - True = button released
    buttonReleased = GPIO.input(pin)
    if buttonReleased:
        t = "released"
    else:
        t = "pushed"
    log.debug("Button {} was {}".format(pin, t))
    if buttonReleased == False:
        asyncio.run_coroutine_threadsafe(button_event_async(pin), appd.loop)

############### MOTION ###########
async def motion_detected(repeat, timeout):
    log.debug("motion_detected")


######################## MAIN ##########################
async def mainloop_timer(repeat, timeout):
    # mostly for debugging things
    #log.debug("mainloop")
    
    # appd.mainloopcnt += 1
    # if appd.mainloopcnt % 5 == 0:
    #     button_event(appd.button)

    timer.Timer(1, mainloop_timer, False)

if __name__ == '__main__':
    log.debug("Summoning the force...")
    # set up neopixels
    ORDER = neopixel.GRB
    pixels = neopixel.NeoPixel(
        appd.pixel_pin, appd.num_pixels, brightness=1.0, auto_write=False, pixel_order=ORDER
    )
    pixels.fill((0, 0, 0)) # start off
    pixels.show()

    # set up our button.
    GPIO.setwarnings(True) # Ignore warning for now
    GPIO.setup(appd.button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(appd.button, GPIO.BOTH, callback=button_event, bouncetime=100)

    timer.Timer(1, mainloop_timer, True)

    try:
        appd.motion = motion.Motion(motion_detected)
    except Exception as e:
        # if the motion box isn't connected (or broken) we'll get here
        log.error(">>>>Motion Module Error>>>> {} ".format(e))
        #appd.audio.play_sound(audio.buzzer)

    appd.blade = blade.Blade(pixels, blue)

    # run the event loop
    appd.loop = asyncio.get_event_loop()
    appd.loop.run_forever()
    appd.loop.close()

    # cleanup
    GPIO.cleanup()
