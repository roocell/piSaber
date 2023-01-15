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
import audio

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
        # can't using GPIO12 (which is our PWM sound) or GPIO18 (which requires sound off to work)
        self.pixel_pin = board.D21
        self.audiopath = "/home/roocell/p/audio/"
        self.mainloopcnt = 0
        self.debug_button = 26 # GPIO26
        self.external_button = 1 # GPIO1
        self.last_button_value = True # False = pressed
        self.button_timer_short = False
        self.button_timer_long = False
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
async def debug_button_event_async(pin):
    log.debug("debug button in asyncio")

def debug_button_event(pin):
    # GPIO event is not on mainthread so we have to store the main event loop in appd
    # and then use it here
    # pulled down in HW
    # - False = button pushed
    # - True = button released
    buttonReleased = GPIO.input(pin)
    if buttonReleased:
        t = "released"
    else:
        t = "pressed"
    log.debug("Button {} was {}".format(pin, t))
    # https://www.joeltok.com/blog/2020-10/python-asyncio-create-task-fails-silently
    # any syntax error inside our coroutine will fail silently.
    # we have to explicitly raise any exceptions here
    # call run_coroutine_threadsafe when going from non-async to async
    #asyncio.run_coroutine_threadsafe(debug_button_event_async(appd.debug_button), appd.loop)

def external_button_event(pin):
    buttonReleased = GPIO.input(pin)
    if buttonReleased:
        t = "released"
    else:
        t = "pressed"
    log.debug("ext Button {} was {}".format(pin, t))

def external_button_is_pressed():
    return GPIO.input(appd.external_button) == False
        
############### MOTION ###########
async def hit_detected():
    log.debug("hit_detected")
    if appd.blade.get_state() == blade.BLADE_ON:
        await appd.audio.play_hit()
        await appd.blade.animate(blade.BLADE_CRASH)

async def swing_detected():
    log.debug("swing_detected")
    if appd.blade.get_state() == blade.BLADE_ON:
        await appd.audio.play_swing()

######################## MAIN ##########################
async def button_long_timer_callback(repeat, timeout):
    print("long press")
    try:
        if appd.blade.get_state() == blade.BLADE_OFF:
            await appd.audio.play_on()
            await appd.blade.animate(blade.BLADE_ON)
        else:
            await appd.audio.play_off()
            await appd.blade.animate(blade.BLADE_OFF)
    except Exception as e: log.error(">>>>Error>>>> {} ".format(e))    

async def button_short_timer_callback(repeat, timeout):
    try:
        # if the button is still pressed, then do nothing
        # the user may be going for a longer press
        if external_button_is_pressed():
            return
        # short press - cycle through idle modes
        print("short press")
        if appd.button_timer_long:
            appd.button_timer_long.cancel()
        # don't do this if the blade is off
        if appd.blade.get_state() == blade.BLADE_OFF:
            return
        await appd.blade.idle_cyclefunc()
    except Exception as e: log.error(">>>>Error>>>> {} ".format(e))    

async def startup_animation(repeat, timeout):
        #await appd.audio.play_startup()
        pixels[5] = white
        pixels.show()
        time.sleep(0.5)
        pixels[5] = black
        pixels[25] = white
        pixels.show()
        time.sleep(0.5)
        pixels[25] = black
        pixels[45] = white
        pixels.show()
        time.sleep(0.5)
        pixels.fill((0, 0, 0)) # start off
        pixels.show()

async def mainloop_timer(repeat, timeout):
    try: 
        # mostly for debugging things
        #log.debug("mainloop")
        
        # appd.mainloopcnt += 1
        # if appd.mainloopcnt % 5 == 0:
        #     button_event(appd.button)

        # check_for_cycle = False
        button_val = GPIO.input(appd.external_button)
        #print(button_val)

        if button_val == False and appd.last_button_value == True:
            # falling edge (pressed)
            print("button pressed")
            appd.button_timer_short = timer.Timer(0.5, button_short_timer_callback, False)
            appd.button_timer_long = timer.Timer(2.0, button_long_timer_callback, False)
        elif button_val == True and appd.last_button_value == False:
            # rising edge (released)
            print("button released")
        appd.last_button_value = button_val

        timer.Timer(0.1, mainloop_timer, False)
    except Exception as e: log.error(">>>>Error>>>> {} ".format(e))

if __name__ == '__main__':
    log.debug("Summoning the force...")
    # set up neopixels
    ORDER = neopixel.GRB
    pixels = neopixel.NeoPixel(
        appd.pixel_pin, appd.num_pixels, brightness=1.0, auto_write=False, pixel_order=ORDER
    )

    # set up our internal/debug button.
    GPIO.setwarnings(True)
    GPIO.setup(appd.debug_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(appd.debug_button, GPIO.BOTH, callback=debug_button_event, bouncetime=100)

    # set up our external button.
    GPIO.setwarnings(True)
    GPIO.setup(appd.external_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(appd.external_button, GPIO.BOTH, callback=external_button_event, bouncetime=100)

    timer.Timer(1, mainloop_timer, True)
    timer.Timer(0.1, startup_animation, False)

    try:
        appd.motion = motion.Motion(swing_detected, hit_detected)
    except Exception as e:
        # if the motion box isn't connected (or broken) we'll get here
        log.error(">>>>Motion Module Error>>>> {} ".format(e))
        #appd.audio.play_sound(audio.buzzer)

    appd.blade = blade.Blade(pixels,blue)
    appd.audio = audio.Audio()

    # run the event loop
    appd.loop = asyncio.get_event_loop()
    appd.loop.run_forever()
    appd.loop.close()

    # cleanup
    GPIO.cleanup()
