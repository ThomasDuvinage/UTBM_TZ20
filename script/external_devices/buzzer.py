#!/usr/bin/env python
import RPi.GPIO as GPIO
import time

"""
    This Class represents the Buzzer 
"""
class Buzzer():
    """
        Constructor
    """
    def __init__(self):
        self.buzzerPin = 22 #pin connected to the rpi
        self.enabled = True #is working or not 
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.buzzerPin, GPIO.OUT)

    """
        This method is used to change the state of the buzzer 

        Argument : newState
    """
    def setEnable(self, _newState):
        self.enabled = _newState

    """
        This method is used to get the of the buzzer
    """
    def isEnabled(self):
        return self.enabled

    """
        This method is used to play a specified tone
    """
    def play(self,tones):
        if self.enabled:
            p = GPIO.PWM(self.buzzerPin, 440)
            for t in tones:
                p.ChangeFrequency(t[0])
                p.start(0.5)
                time.sleep(float(t[1])/1000)
                p.stop()
                time.sleep(float(t[2])/1000)

    """
        Play error tone
    """     
    def error(self):
        tonesList = [   #[frequency,duration,pause]
            [300,100,50],
            [200,300,0]
            ]
        self.play(tonesList)

    """
        Play success tone
    """    
    def success(self):
        tonesList = [   #[frequency,duration,pause]
            [200,50,50],
            [400,50,50],
            [600,200,0]
            ]
        self.play(tonesList)

    """
        Play disable tone
    """    
    def disable(self):
        tonesList = [   #[frequency,duration,pause]
            [600,50,50],
            [400,50,50],
            [200,200,0]
            ]
        self.play(tonesList)

    """
        Play click tone
    """    
    def click(self):
        tonesList = [   #[frequency,duration,pause]
            [500,30,50]
            ]
        self.play(tonesList)

    """
        Play warn tone
    """    
    def warn(self):
        tonesList = [   #[frequency,duration,pause]
            [500,50,50],
            [500,50,50],
            [500,50,50]
               ]
        self.play(tonesList)

    """
        Play start tone
    """    
    def start(self):
        tonesList = [   #[frequency,duration,pause]
            [100,200,50],
            [500,200,50],
            [700,300,50]
               ]
        self.play(tonesList)

    """
        Play shutdown tone
    """    
    def shutDown(self):
        tonesList = [   #[frequency,duration,pause]
            [700,200,50],
            [500,200,50],
            [100,300,50]
               ]
        self.play(tonesList)
    
    """
        play enable tone
    """    
    def buzzerEnable(self):
        tonesList = [   #[frequency,duration,pause]
            [100,50,50],
            [500,200,50]
               ]
        self.play(tonesList)

    """
        play disable tone
    """    
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