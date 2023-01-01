#!/usr/bin/env python
import time
import board
import neopixel
import RPi.GPIO as GPIO
import os

green =     (0,   255, 0)
red =       (255, 0,   0)
blue =      (0,   98,  255)
yellow =    (255, 221, 0)
black =     (0,   0,   0)
purple =    (238, 0,   255)

num_pixels = 61
pixel_pin = board.D12
ORDER = neopixel.GRB
pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=ORDER
)
pixels.fill((0, 0, 0)) # start off
pixels.show()

path = "/home/roocell/p/audio/"


def button_event(channel):
    print("Button was pushed!", channel)
    if GPIO.input(channel) == True:
        blue_startup()
    else:
        shutdown()

button = 18 # GPIO18
GPIO.setwarnings(True) # Ignore warning for now
GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(button, GPIO.BOTH, callback=button_event, bouncetime=100)

print("Summoning the force...")

def shutdown():
    # retract lights
    for i in range(num_pixels):
        pixels[num_pixels-i-1] = black
        pixels.show()
        time.sleep(0.01)

def blue_startup():
    # light one at a time
    for i in range(num_pixels):
        pixels[i] = blue
        pixels.show()
        time.sleep(0.01)


while True: # Run forever
    if GPIO.input(button) == False:
        os.system("aplay sounds/ON.wav")
    time.sleep(1)
