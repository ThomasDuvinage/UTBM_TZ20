from RPi import GPIO
from time import sleep


class Encoder():
    def __init__(self):
        # you have to change the pinout depending on your needs
        self.clk = 27
        self.dt = 23
        self.sw = 12

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.sw, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        self.counter = 0
        self.clkLastState = GPIO.input(self.clk)

    def getCount(self):
        return self.counter

    def setCount(self, _newCount):
        self.counter = _newCount

    def updateCount(self):
        self.clkState = GPIO.input(self.clk)
        self.dtState = GPIO.input(self.dt)
        if self.clkState != self.clkLastState:
            if self.dtState != self.clkState:
                self.counter += 5
            else:
                self.counter -= 5

            self.clkLastState = self.clkState

            return True
        else:
            return False
        # sleep(0.01)

    def isPair(self):
        if(self.counter % 2 == 0):
            return True
        else:
            return False

    def isClicked(self):
        if(GPIO.input(self.sw) == GPIO.LOW):
            return True
        else:
            return False


if __name__ == '__main__':
    try:
        encoder = Encoder()

        while True:
            if(encoder.updateCount()):
                print(encoder.getCount())
    except:
        pass
