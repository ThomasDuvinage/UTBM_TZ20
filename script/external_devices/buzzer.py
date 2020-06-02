#!/usr/bin/env python
import RPi.GPIO as GPIO
import time

class Buzzer():
    def __init__(self):
        self.buzzerPin = 22
        self.enabled = True
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.buzzerPin, GPIO.OUT)

    def setEnable(self, _newState):
        self.enabled = _newState

    def isEnabled(self):
        return self.enabled

    def play(self,tones):
        if self.enabled:
            p = GPIO.PWM(self.buzzerPin, 440)
            for t in tones:
                p.ChangeFrequency(t[0])
                p.start(0.5)
                time.sleep(float(t[1])/1000)
                p.stop()
                time.sleep(float(t[2])/1000)
                
    def error(self):
        tonesList = [   #[frequency,duration,pause]
            [300,100,50],
            [200,300,0]
            ]
        self.play(tonesList)
    def success(self):
        tonesList = [   #[frequency,duration,pause]
            [200,50,50],
            [400,50,50],
            [600,200,0]
            ]
        self.play(tonesList)
    def disable(self):
        tonesList = [   #[frequency,duration,pause]
            [600,50,50],
            [400,50,50],
            [200,200,0]
            ]
        self.play(tonesList)
    def click(self):
        tonesList = [   #[frequency,duration,pause]
            [500,30,50]
            ]
        self.play(tonesList)
    def warn(self):
        tonesList = [   #[frequency,duration,pause]
            [500,50,50],
            [500,50,50],
            [500,50,50]
               ]
        self.play(tonesList)
    def start(self):
        tonesList = [   #[frequency,duration,pause]
            [100,200,50],
            [500,200,50],
            [700,300,50]
               ]
        self.play(tonesList)
    def shutDown(self):
        tonesList = [   #[frequency,duration,pause]
            [700,200,50],
            [500,200,50],
            [100,300,50]
               ]
        self.play(tonesList)
    
    def buzzerEnable(self):
        tonesList = [   #[frequency,duration,pause]
            [100,50,50],
            [500,200,50]
               ]
        self.play(tonesList)
    def buzzerDisable(self):
        tonesList = [   #[frequency,duration,pause]
            [500,50,50],
            [100,200,50]
               ]
        self.play(tonesList)

if __name__ == '__main__':
    try:
        #try all melodies
        buzzer = Buzzer()
        buzzer.error()
        buzzer.success()
        buzzer.warn()
        buzzer.start()
        buzzer.shutDown()
        buzzer.buzzerEnable()
        buzzer.buzzerDisable()
    except:
        pass