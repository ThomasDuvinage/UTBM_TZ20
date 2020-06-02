# UTBM TZ20 Project

Welcome to the Github repository of our project !  
It consists in designing, building and programming a full portable console allowing the University of Technology of Belfort-Montbeliard (France) staff to control students attendance at some mandatory events.  
This project involves Raspberry Pi programming through Python, 3D printing, and electronics.
This repository contains all documents related to the project that is currently under construction.

<img src="img/box.jpg" width="500px">

## Useful links : ##

| Description                                             | URL                                                                                                            | We used it for :                                                                                                 |
|---------------------------------------------------------|----------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------|
| RC522 wiring guide                                      | [Click here](https://pimylifeup.com/raspberry-pi-rfid-rc522/)                                                  | Wiring RC522 module to the Raspberry Pi. For programming, refer to the line below                                |
| RC522 python class                                      | [Click here](https://github.com/danjperron/MFRC522-python)                                                     | Programming the Raspberry Pi for controlling the RC522 module, especially to read 7 bytes UIDs                   |
| Git handling from bash terminal                         | [Click here](https://medium.com/@panjeh/makefile-git-add-commit-push-github-all-in-one-command-9dcf76220f48 )  | Remind us how to handle a git repo from bash terminal                                                            |
| Change I2C pins on Raspberry Pi                         | [Click here](https://raspberrypi.stackexchange.com/questions/88149/change-i2c-pins-on-raspberry-pi)            | Opening a second I2C channel on the Raspberry Pi                                                                 |
| Python class for I2C enabled LCD screens                | [Click here](https://www.raspberrypi-spy.co.uk/2015/05/using-an-i2c-enabled-lcd-screen-with-the-raspberry-pi/) | Controlling the 16x2 I2C driven LCD screen through Python                                                        |
| Fan controlling from Raspberry Pi                       | [Click here](https://howchoo.com/g/ote2mjkzzta/control-raspberry-pi-fan-temperature-python)                    | Wiring and controlling a 5v fan to cool down Raspberry Pi CPU                                                    |
| Guide to run python script at Raspi startup             | [Click here](https://www.dexterindustries.com/howto/run-a-program-on-your-raspberry-pi-at-startup/#systemd)    | Creating a systemd service to run a Python script that reads CPU temp and controls the fan through an hysteresis |
| Guide for using a DS1302 RTC Module with a Raspberry Pi | [Click here](https://github.com/sourceperl/rpi.rtc)                                                            | Using an RTC DS1302 module to ensure a non-volatile time management                                              |
| Tutorial about using a config.ini file with Python      | [Click here](https://pymotw.com/2/ConfigParser/)                                                               | Storing user settings as non-volatile variables                                                                  |
| Forum about dismounting USB drive from Python           | [Click here](https://www.raspberrypi.org/forums/viewtopic.php?t=198250)                                        | Safe ejecting USB keys after importations and exportations

## Hardware ##
### 3D printing ###

### Electronics ###

## Installation ##
### By burning .img to SD card (recommended) ###

### By cloning this repository ###
Please follow the instructions below to proceed software installation :
1. Make sure wiring is correct (see section *Electronics* above)
2. Download and flash Raspbian or Minibian (command-line only) to an empty SD card (see [here](https://www.raspberrypi.org/documentation/installation/installing-images/))
3. Make sure your default user is named "pi" by opening a terminal (Ctrl + Alt + T) and typing
```
whoami
```
4. Clone this repository to /home/pi :
```
git clone https://github.com/totordudu/UTBM_TZ20.git
```
5. Give all permissions to install script :
```
sudo chmod 777 install.py
```
6. Run install.py:
```
cd /home/pi/UTBM_TZ20/
python install.py
```
7. Check that *scripts/main.py* has *-rwxrwxrwx* permissions :
```
ls -l /home/pi/UTBM_TZ20/scripts/main.py
```
8. Enable SPI, I2C, remote GPIO
```sudo raspi-config
Interfacing options 
```
9. modify the SPI connection 
```
sudo nano /boot/config.txt
```
Add at the end 
```
[all]
#dtoverlay=vc4-fkms-v3d
dtoverlay=i2c-gpio,i2c_gpio_sda=17,i2c_gpio_scl=18
```

Then the script main.py should run by entering : ```~/UTBM/script $ python main.py```
