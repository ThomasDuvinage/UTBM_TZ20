#!/usr/bin/env python
from time import sleep
import os
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

R9 = 10000 #in ohms (see schematic)
R10 = 6800 #in ohms

VoltageThreshold = 4.8 #TODO: determine it empirically

n = 1024 #Resolution MCP3001
#numeros de pins
SPICLK = 19
SPIMISO = 13 #DOUT
SPICS = 26
# definition de l interface SPI
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)

def MCPread(clockpin, misopin, cspin):
	GPIO.setup(clockpin, GPIO.OUT)
    GPIO.setup(cspin, GPIO.OUT)
    GPIO.setup(misopin, GPIO.IN)
    GPIO.output(clockpin, False)  # CLK low
    GPIO.output(cspin, False)   # /CS low
    adcvalue = 0
    for i in range(13):
        GPIO.output(clockpin, True)
        GPIO.output(clockpin, False)
        adcvalue <<= 1
        if(GPIO.input(misopin)):
            adcvalue |= 0x001
    GPIO.output(cspin, True)    # /CS high
    adcvalue &= 0x3ff
    return adcvalue

def getVoltage(value):
	output_Voltage = float(value)/n*3.3 #Voltage obtained between R9 and R10 in voltage divider
	BatteryVoltage = output_Voltage*(1+float(R9)/R10) #voltage divider formula
	return BatteryVoltage

def mean(array):
	sum=0
	for i in array:
		sum+=i
	return sum/len(array)

while True:
    print "****READING BATTERY VOLTAGE*****"
    readArray = []
    for i in range(10):
		readArray.append(getVoltage(readadc(SPICLK, SPIMISO, SPICS)))
		sleep(0.1)
	Voltage = mean(readArray)
	print("Battery voltage : ",Voltage)
    if(Voltage<=VoltageThreshold):
		os.system("sudo systemctl stop main.service")
		os.system("sudo shutdown now")
    sleep(1)

