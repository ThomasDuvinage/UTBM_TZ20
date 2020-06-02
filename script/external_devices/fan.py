from RPi import GPIO
import time
import sys
import signal

fan = 24

hysteresis = [43,54]

GPIO.setmode(GPIO.BCM)
GPIO.setup(fan, GPIO.OUT)
GPIO.output(fan,1)

def sigterm_handler(_signo, _stack_frame): #HANDLER FUNCTION FOR SIGTERM SIGNAL
    print('Fan interrupted by Sigterm')
    GPIO.cleanup()
    sys.exit(0)

signal.signal(signal.SIGTERM, sigterm_handler) #associates SIGTERM signal with its handler

while(True):
    # Read CPU temperature
    cpuTempFile = open("/sys/class/thermal/thermal_zone0/temp", "r")
    cpuTemp = float(cpuTempFile.read()) / 1000
    cpuTempFile.close()

    if cpuTemp>hysteresis[1]:
        GPIO.output(fan,1)
    
    if cpuTemp<hysteresis[0]:
        GPIO.output(fan,0)

    time.sleep(1)
