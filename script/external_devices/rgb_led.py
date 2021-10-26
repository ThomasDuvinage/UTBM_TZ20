#!/usr/bin/env python
import RPi.GPIO as GPIO
import time

# define colors by using dictonnary (R,G,B)
colorPanel = {}
colorPanel['r'] = (1, 0, 0)
colorPanel['g'] = (0, 1, 0)
colorPanel['b'] = (0, 0, 1)
colorPanel['c'] = (0, 1, 1)
colorPanel['m'] = (1, 0, 1)
colorPanel['y'] = (1, 1, 0)
colorPanel['w'] = (1, 1, 1)

"""
    This class represents the Led 
"""


class Led():
    # Constructor
    def __init__(self):
        self.r = 21
        self.g = 16
        self.b = 20

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.r, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(self.g, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(self.b, GPIO.OUT, initial=GPIO.HIGH)

    @staticmethod
    def setColor(self, color):
        """
            This method is used to set the color of the led by passing in argument an array of color state
        """
        if color in colorPanel:
            GPIO.output(self.r, 1-colorPanel[color][0])
            GPIO.output(self.g, 1-colorPanel[color][1])
            GPIO.output(self.b, 1-colorPanel[color][2])

    # Shutdown method is used to switch off the led
    def shutDown(self):
        GPIO.output(self.r, 1)
        GPIO.output(self.g, 1)
        GPIO.output(self.b, 1)


if __name__ == '__main__':
    try:
        led = Led()
        time.sleep(2)
        led.setColor(colorPanel['m'])
        time.sleep(2)

        led.shutDown()
    except:
        pass
