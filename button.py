import RPi.GPIO as GPIO
from logger import log as log
import time

def button_event(pin):
    log.debug(GPIO.input(pin))

GPIO.setmode(GPIO.BCM)

# set up our button.
button = 14 # GPIO14
GPIO.setwarnings(True)
GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(button, GPIO.BOTH, callback=button_event, bouncetime=100)

while True:
    log.debug("mainloop")
    time.sleep(1)
