#!/usr/bin/env python
import RPi.GPIO as GPIO

#define colors
colorPanel = {}
colorPanel['r']=(1,0,0)
colorPanel['g']=(0,1,0)
colorPanel['b']=(0,0,1)
colorPanel['c']=(0,1,1)
colorPanel['m']=(1,0,1)
colorPanel['y']=(1,1,0)
colorPanel['w']=(1,1,1)

class Led():
    def __init__(self):
        self.r = 21
        self.g = 20
        self.b = 16

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.r, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(self.g, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(self.b, GPIO.OUT, initial=GPIO.HIGH)

    @staticmethod
    def setColor(color, self):
        if color in colorPanel:
            GPIO.output(self.r,1-colorPanel[color][0])
            GPIO.output(self.g,1-colorPanel[color][1])
            GPIO.output(self.b,1-colorPanel[color][2])
    
    def shutDown(self):
            GPIO.output(self.r,1)
            GPIO.output(self.g,1)
            GPIO.output(self.b,1)

if __name__ == '__main__':
    try:
        led = Led()
        led.shutDown()
    except:
        pass