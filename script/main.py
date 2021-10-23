#! /usr/bin/python
'''
 ___      ___ ________  ___       _______   ________   _________  ___  ________   ________  ________     
|\  \    /  /|\   __  \|\  \     |\  ___ \ |\   ___  \|\___   ___\\  \|\   ___  \|\   ____\|\   __  \    
\ \  \  /  / | \  \|\  \ \  \    \ \   __/|\ \  \\ \  \|___ \  \_\ \  \ \  \\ \  \ \  \___|\ \  \|\  \   
 \ \  \/  / / \ \   __  \ \  \    \ \  \_|/_\ \  \\ \  \   \ \  \ \ \  \ \  \\ \  \ \  \____\ \   __  \  
  \ \    / /   \ \  \ \  \ \  \____\ \  \_|\ \ \  \\ \  \   \ \  \ \ \  \ \  \\ \  \ \  ___  \ \  \|\  \ 
   \ \__/ /     \ \__\ \__\ \_______\ \_______\ \__\\ \__\   \ \__\ \ \__\ \__\\ \__\ \_______\ \_______\
    \|__|/       \|__|\|__|\|_______|\|_______|\|__| \|__|    \|__|  \|__|\|__| \|__|\|_______|\|_______|
                                                                                                         
                                                                                                         
                                                                                                         
 _________  ________  _________  ________  ________  ________  ___  ___  ________  ___  ___              
|\___   ___\\   __  \|\___   ___\\   __  \|\   __  \|\   ___ \|\  \|\  \|\   ___ \|\  \|\  \             
\|___ \  \_\ \  \|\  \|___ \  \_\ \  \|\  \ \  \|\  \ \  \_|\ \ \  \\\  \ \  \_|\ \ \  \\\  \            
     \ \  \ \ \  \\\  \   \ \  \ \ \  \\\  \ \   _  _\ \  \ \\ \ \  \\\  \ \  \ \\ \ \  \\\  \           
      \ \  \ \ \  \\\  \   \ \  \ \ \  \\\  \ \  \\  \\ \  \_\\ \ \  \\\  \ \  \_\\ \ \  \\\  \          
       \ \__\ \ \_______\   \ \__\ \ \_______\ \__\\ _\\ \_______\ \_______\ \_______\ \_______\         
        \|__|  \|_______|    \|__|  \|_______|\|__|\|__|\|_______|\|_______|\|_______|\|_______|         
                                                                                                         

Created on March 2020 by valentin.mercy[at]utbm[dot]fr for UTBM TZ20 project : https://github.com/totordudu/UTBM_TZ20
Edited by valentin.mercy[at]utbm[dot]fr and thomas.duvinage[at]utbm[dot]fr

'''
from external_devices.lcd_lib import *
from external_devices.buzzer import *
from external_devices.rgb_led import *
from external_devices.rotary_encoder import *
from external_devices.pyRPiRTC import *
import treelib
from RPi import GPIO
from external_devices.MFRC522 import *
import datetime
import subprocess
import os
import requests
from FilesFunctions import *
from ConfigParser import SafeConfigParser
import signal
import sys
""" import pyudev
import psutil """
import re
import urllib2
import FilesFunctions.structureConfig as structConfig

GPIO.setwarnings(False)

#INITIALIZATION OF INTERNAL OBJECTS
led = Led()
buzz = Buzzer()
encoder = Encoder()

acceptUTBMCardsOnly = True #if True, the program will only accept UTBM-like cards (7 bytes UID beginning by 805 and ending by 04), both for admin and students
enableStart = False
ScrollSpeed = 65 #in percents
IntervalMulti = datetime.timedelta(0)

ConfigFileName = "/home/pi/UTBM_TZ20/script/mainconfig.ini"
IsInterruptionIntentional = False
FileDatetimeFormat = "%d-%m-%Y-%H-%M-%S"
ConnectionTestUID = "805A42AA825904"
ForceLevel = []
version = 0 #date of last git pull

#INITIALIZATION OF VARIABLES AND EXTERNAL OBJECTS
continue_reading = True
admin_uid = "805A42AA825904"
mylcd = lcd()
mylcd.lcd_clear()
MIFAREReader = MFRC522()
rtc = DS1302(clk_pin=13, data_pin=19, ce_pin=26) #To use RTC : lecture : datetime = rtc.read_datetime(), ecriture : rtc.write_datetime(dt_write)

#FUNCTIONS ABOUT ADMIN AUTHENTIFICATION AND CARD SCANNING
def RecordAdmin(): #Records the administrator. The administrator will be the only one that can stop scanning procedure and delete controls (individually and all at once)
    led.setColor("m",led)
    mylcd.lcd_clear()
    mylcd.lcd_display_string(" SCANNEZ CARTE",1)
    mylcd.lcd_display_string(" ADMINISTRATEUR",2)
    uid = WaitForCard(False)
    while not CheckUIDFormat(uid):
        buzz.error()
        YesNoBackScreen('BADGE INCOHERENT',"r",['OK'],'OK')
        led.setColor("m",led)
        mylcd.lcd_clear()
        mylcd.lcd_display_string(" SCANNEZ CARTE",1)
        mylcd.lcd_display_string(" ADMINISTRATEUR",2)
        uid = WaitForCard(False)
    buzz.success()
    return uid

def CheckUIDFormat(UID): #Checks if a card UID corresponds to a UTBM card
    if acceptUTBMCardsOnly:
        if len(UID)==14 and UID[0:2]=="80" and UID[12:14]=="04":
            return True
        else:
            return False
    else:
        return True

def CheckAdmin(): #Authentificates the administrator before allowing access to sensible functions
    led.setColor("m",led)
    mylcd.lcd_clear()
    mylcd.lcd_display_string(" SCANNEZ CARTE",1)
    mylcd.lcd_display_string("ADMIN.     >RET<",2)
    Attempt = WaitForCard(True)
    while(Attempt!=admin_uid):
        if(Attempt==-1):    #function has been interrupted by encoder click (user request back level)
            return False
        buzz.error()
        YesNoBackScreen('MAUVAISE CARTE',"r",['OK'],'OK')
        led.setColor("m",led)
        mylcd.lcd_clear()
        mylcd.lcd_display_string(" SCANNEZ CARTE",1)
        mylcd.lcd_display_string("ADMIN.     >RET<",2)
        Attempt = WaitForCard(True)
        if not CheckUIDFormat(Attempt):
            buzz.error()
            YesNoBackScreen('BADGE INCOHERENT',"r",['OK'],'OK')
    buzz.success()
    return True            

#Following 3 variables are used to simulate fake cards for development purposes
FoolUIDs = False #must be False if user has not registered his MAC addresses in dict below

MAC_addresses = {
    'b8:27:eb:b5:93:fd':'val', #developper 1
    'b8:27:eb:e4:ef:1e':'tom' #developper 2
}

fakeUIDs = {
    'val':
    {
    '805A42AA825904' : "805A42AA825904",#admin one must map to itself
    '805CB8BAA55D04' : "80556170911404",
    '805CB8BAA4F704' : "80557144006904",
    '805CB8BAA4BE04' : "80583632928104",
    '805CB8BAA4FB04' : "80561351520504",
    '805CB8BAA4AA04' : "80522816482504",
    '805CB8BAA49D04' : "80543190596804",
    '805CB8BAA56104' : "80550722390004",
    '805CB8BAA4E104' : "80525133961304",
    '805CB8BAA4A204' : "80557514066004",
    '815CB8BAA42204' : "80546189531104"
    },
    'tom':
    {
    '805A42AA825904' : "805A42AA825904", #admin one must map to itself
    '805CB8BAA4AE04' : "80556170911404",
    '805CB8BAA48B04' : "80557144006904",
    '815CB8BAA40504' : "80583632928104",
    '805CB8BAA57004' : "80561351520504",
    '805CB8BAA57404' : "80522816482504",
    '805CB8BAA58404' : "80543190596804",
    '805CB8BAA48704' : "80550722390004",
    '805CB8BAA4E504' : "80525133961304",
    '815CB8BAA41204' : "80557514066004",
    '815CB8BAA40E04' : "80546189531104"
    }
    }

def uidToString(uid): #Formats a scanned UID to a clean string
    mystring = ""
    for i in uid:
        mystring = format(i, '02X') + mystring
    return mystring

def WaitForCard(allowClick,timeout=-1): #Waits for RC-522 to scan a new card with timeout
    end = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
    while continue_reading:
        if allowClick and encoder.isClicked():
            AntiRebound()
            return -1
        if timeout>0 and datetime.datetime.now()>=end:
            return -1
        # Scan for cards
        (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

        # If a card is found
        if status == MIFAREReader.MI_OK:
            print ("Card detected")

            # Get the UID of the card
            (status, uid) = MIFAREReader.MFRC522_SelectTagSN()
            # If we have the UID, continue
            if status == MIFAREReader.MI_OK:
                print("Card read UID: %s" % uidToString(uid))
                if FoolUIDs:
                    try:
                        return fakeUIDs[MAC_addresses[getMAC('eth0')]][uidToString(uid)]
                    except KeyError:
                        print("Can't fool UID because of unknown MAC or unregistered fake Card")
                        return uidToString(uid)
                else:
                    return uidToString(uid)
            else:
                print("Authentication error")

#FUNCTIONS ABOUT DISPLAY AND NAVIGATION
def CenterOnScreen(string,width): #Centers given string
    nb_spaces = (width-len(string))/2
    newString = " "*nb_spaces+string+" "*(width-(nb_spaces+len(string)))
    return newString

def YesNoBackScreen(line_1,led_state,options_list,defaultOption): #Interface that present options to user. options_list array contains 3 characters strings in the following order : yes, no, back
    #implementer avec AUTOSCROLL
    led.setColor(led_state,led)
    mylcd.lcd_clear()
    #mylcd.lcd_display_string(CenterOnScreen(line_1,16),1)
    NbOptions = len(options_list)
    pos=0
    if(options_list.count(defaultOption)==1):
        pos = options_list.index(defaultOption)
    if(NbOptions==0):
        print("ERROR NO OPTION ON YESNOBACK SCREEN")
        return -1
    else:
        while not encoder.isClicked():
            optionStrings = []
            for opt in options_list:
                if options_list.index(opt)==pos:
                    optionStrings.append(CenterOnScreen(">"+opt+"<",5))
                else:
                    optionStrings.append(CenterOnScreen(opt,5))
            separator = ""
            line_2=CenterOnScreen(separator.join(optionStrings),16)
            mylcd.lcd_display_string(line_2,2)
            encoder.updateCount()
            old_count = encoder.getCount()
            while not encoder.updateCount():
                if FSAutoScroll(line_1,1):
                    break
            encoder.updateCount()
            new_count = encoder.getCount()
            if new_count>old_count and pos<(NbOptions-1):
                pos+=1
            elif(new_count<old_count and pos>0):
                pos-=1
        AntiRebound()
        return options_list[pos]    #return final choice after encoder click

def FSAutoScroll(String,line): #Full Screen AutoScroll, has nothing to see with AutoScroll function below
    j=0
    while(not encoder.isClicked() and not encoder.updateCount()):
        mylcd.lcd_display_string(CenterOnScreen(String[j:j+16],16),line)
        if(len(String)-j<=16):
            j=0
        else:
            j+=1
        if(EncWatchPause(1-float(ScrollSpeed)/100)):
            return True
    if encoder.isClicked():
        AntiRebound()
    return True

def holdScreen(Strings,ledState,sec,ForbidInterruption): #Multi Line Autoscroll : holds autoscroll during a certain amount of time. Can't be interrupted while autoscrolling, but only between two autoscroll steps
    mylcd.lcd_clear()
    setLedState(ledState)
    deb = datetime.datetime.now()
    while(datetime.datetime.now()<deb+datetime.timedelta(seconds=sec)):
        for i in range (1,3):
            mylcd.lcd_display_string(CenterOnScreen(Strings[i-1],16),i)
        for i in range(1,3):
            j=0
            while ForbidInterruption:
                mylcd.lcd_display_string(CenterOnScreen(Strings[i-1][j:j+16],16),i)
                if(len(Strings[i-1])-j<16):
                    break
                else:
                    j+=1
                time.sleep(1-float(ScrollSpeed)/100)
            while not ForbidInterruption and datetime.datetime.now()<deb+datetime.timedelta(seconds=sec):
                mylcd.lcd_display_string(CenterOnScreen(Strings[i-1][j:j+16],16),i)
                if(len(Strings[i-1])-j<16):
                    break
                else:
                    j+=1
                time.sleep(1-float(ScrollSpeed)/100)

def AutoScroll(CenterString,CurrentPosition,nbElements): #Used to handle screen-size overshoot
    j=0
    while(not encoder.isClicked() and not encoder.updateCount()):
        if(CurrentPosition==0): #left extremity
            mylcd.lcd_display_string("  "+CenterString[j:j+12]+" "*(12-len(CenterString[j:j+12]))+" >",2)
        elif(CurrentPosition==nbElements-1): #right extremity
            mylcd.lcd_display_string("< "+CenterString[j:j+12]+" "*(12-len(CenterString[j:j+12]))+"  ",2)
        else: #between
            mylcd.lcd_display_string("< "+CenterString[j:j+12]+" "*(12-len(CenterString[j:j+12]))+" >",2)
        if(len(CenterString)-j<=12):
            j=0
        else:
            j+=1
        if(EncWatchPause(1-float(ScrollSpeed)/100)):
            return True
    if encoder.isClicked():
        AntiRebound()
    return True

def NavigateLevel(parentIdentifier,defaultIdentifier): #Let user navigate in a level of menu tree
    parentData = menuTree[parentIdentifier].data
    subMenuIdentifiers = menuTree.is_branch(parentIdentifier)
    TotalData = []
    pos = 0
    for identifier in subMenuIdentifiers:
        TotalData.append(menuTree[identifier].data)
        if identifier==defaultIdentifier:
            pos=subMenuIdentifiers.index(identifier)
    if(parentIdentifier!="main"):
        TotalData.append([CenterOnScreen("RETOUR",16),"","c"])
    mylcd.lcd_clear()
    mylcd.lcd_display_string(CenterOnScreen(parentData[1],16),1)
    while(not encoder.isClicked()):
        led.setColor(TotalData[pos][2],led)
        encoder.updateCount()
        old_count = encoder.getCount()
        AutoScroll(TotalData[pos][0],pos,len(TotalData))
        while(not encoder.updateCount() and not encoder.isClicked()):
            pass
        encoder.updateCount()
        new_count = encoder.getCount()
        if(new_count>old_count and pos<(len(TotalData)-1)):
            pos+=1
        elif(new_count<old_count and pos>0):
            pos-=1
    AntiRebound()
    if(TotalData[pos][0]==CenterOnScreen("RETOUR",16)): #bring user back
        SelectionParent = ""
        for key in menuTree[parentIdentifier]._predecessor:
            SelectionParent = menuTree[parentIdentifier]._predecessor[key]
        print("BACK REQUEST to ",SelectionParent)
        return SelectionParent
    else:
        return subMenuIdentifiers[pos]

def NavigateInArray(line_1,array,defaultIndex,allowBack,led_color): #Same as function above, but detached from menu tree
    if len(array) == 0:
        print("Can't navigate in empty array")
        return False
    if defaultIndex >= len(array):
        print("defaultIndex out of array")
        return False
    if allowBack:
        array.append(CenterOnScreen("RETOUR",16))
    pos = defaultIndex
    mylcd.lcd_clear()
    mylcd.lcd_display_string(CenterOnScreen(line_1,16),1)
    setLedState(led_color)
    while(not encoder.isClicked()):
        encoder.updateCount()
        old_count = encoder.getCount()
        AutoScroll(array[pos],pos,len(array))
        while(not encoder.updateCount() and not encoder.isClicked()):
            pass
        encoder.updateCount()
        new_count = encoder.getCount()
        if(new_count>old_count and pos<(len(array)-1)):
            pos+=1
        elif(new_count<old_count and pos>0):
            pos-=1
    AntiRebound()
    if allowBack and pos == len(array)-1:
        return False
    return array[pos]

def Menu(firstParentIdentifier,defaultIdentifier): #Recursive function to navigate inside main menu
    global ForceLevel
    global menuTree
    functions_needing_menu_update = ["show_attendance_controls","control_delete"]
    while True:
        print("NAVIGATION INSIDE ",firstParentIdentifier)
        SelectionIdentifier = NavigateLevel(firstParentIdentifier,defaultIdentifier)
        if SelectionIdentifier in functions_needing_menu_update:
            update_menu()
        print("Selected identifier : ",SelectionIdentifier)
        SelectionData = menuTree[SelectionIdentifier].data
        if(SelectionData[1]==""): #terminal level, we run requested action. Must implement data handling
            if "control_" in SelectionIdentifier:
                functionToCall = "control_"+SelectionIdentifier.split("_",2)[2]
                argToPass = SelectionIdentifier.split("_",2)[1]
                globals()[functionToCall](argToPass)
            else:
                globals()[SelectionIdentifier]() #run function whose name corresponds to SelectionIdentifier
            SelectionParent = ""
            for key in menuTree[SelectionIdentifier]._predecessor:
                SelectionParent = menuTree[SelectionIdentifier]._predecessor[key]
            if ForceLevel:
                firstParentIdentifier=ForceLevel[0]
                defaultIdentifier=ForceLevel[1]
                ForceLevel=[]
            else:
                firstParentIdentifier=SelectionParent
                defaultIdentifier=SelectionIdentifier
        else:
            #NavigateLevel(SelectionIdentifier,0)
            firstParentIdentifier=SelectionIdentifier
            defaultIdentifier=0

#FUNCTIONS ABOUT EXTERNAL DEVICES
def EncWatchPause(sec): #Waits for action on encoder, with a timeout
    deb = datetime.datetime.now()
    while(datetime.datetime.now()<deb+datetime.timedelta(seconds=sec)):
        if(encoder.isClicked() or encoder.updateCount()):
            return True
        time.sleep(0.001)

def setLedState(state): #Set let state (same as led.setColor but allows led shutdown)
    if state=="o":
        led.shutDown()
    else:
        led.setColor(state,led)

def AntiRebound(): #Avoid encoder button rebounds
    buzz.click()
    while encoder.isClicked():
        pass

def getUSBPath(): #Returns USB key mounting point
    key = USBKey()
    key.findUSBPath()
    return key.getPath()

def rtc_set_time(dt_to_write): #Set Real Time Clock module time
    try:
        rtc.write_datetime(dt_to_write)
        # check update is good
        dt_read = rtc.read_datetime()
        if -2 < (dt_to_write - dt_read).total_seconds() < +2:
            print("datetime successfully update on RTC module : ", dt_to_write.strftime('%Y-%m-%dT%H:%M:%SZ'))
            return True
        else:
            print("error while updating datetime to RTC, difference is too high")
            return False
    except ValueError:
        print("error while updating datetime to RTC, check wiring")
    finally:
        rtc.close()

def rtc_get_time(): #Read Real Time Clock module time
    try:
        dt = rtc.read_datetime()
        print("rtc time readed : ", dt.strftime(FileDatetimeFormat))
        return dt
    except ValueError:
        print("error with RTC chip, check wiring")
    finally:
        rtc.close()

def checkInternet(): #Checks internet connection using Google server
    url='http://www.google.com/'
    timeout=5
    try:
        _ = requests.get(url, timeout=timeout)
        return True
    except requests.ConnectionError:
        print ("checkInternet failed : no Internet Connection")
    return False

def dismount_USB(mountpoint): #Allows user to safely remove USB key from Raspberry
    #ASK USER IF REQUEST DISMOUNT AND SHOW HIM USB KEY NAME
    buzz.warn()
    chx = YesNoBackScreen("EJECTER CLE USB "+mountpoint.split("/")[-1]+" ?",'y',['OUI', 'NON'],'NON')
    if(chx=='OUI'):
        os.system('sudo umount "'+mountpoint+'"')
        holdScreen(["DEMONTAGE CLE EN","COURS PATIENTEZ"],'y',1,True)
        buzz.success()
        print ("USB Dismounted")
        holdScreen(['RETIREZ CLE EN','TOUTE SECURITE'],'g',2,True)

#AUXILIARY FUNCTIONS
def setDigit(line_1,line_2_pattern,digit_position,default,limit): #Interface that allows user to set a digit value with a certain pattern
    mylcd.lcd_clear()
    mylcd.lcd_display_string(line_1,1)
    mylcd.lcd_display_string(line_2_pattern,2)
    pos = default
    while not encoder.isClicked():
        encoder.updateCount()
        old_count = encoder.getCount()
        while(not encoder.updateCount() and not encoder.isClicked()):
            if(datetime.datetime.now().second%2==0):    #allows to blink pattern (perdiod of 2 seconds)
                mylcd.lcd_display_string(line_2_pattern[0:digit_position]+str(pos)+" "*(15-digit_position),2)
            else:
                mylcd.lcd_display_string(line_2_pattern[0:digit_position]+str(pos)+line_2_pattern[digit_position+1:16],2)
            if EncWatchPause(0.8):
                break
        encoder.updateCount()
        new_count = encoder.getCount()
        if(new_count>old_count and pos<limit):
            pos+=1
        elif(new_count<old_count and pos>0):
            pos-=1
    AntiRebound()
    return pos

def Digit(nb,rank): #Extracts a digit from number
    nb/=10**rank
    return nb%10

def Number(digits): #Constructs a number from digits
    nb=0
    i=0
    for dig in digits:
        power = len(digits)-i-1
        nb+=dig*10**power
        i+=1
    return nb

def setNumberEns(line_1,data,default): #Interface used to navigate set a value with units and subunits (like hour,minutes,seconds). Data must be an array like [[inf,sup,unit],[],...,[]], and default an array like [number, unit]
    res = default
    while True:
        inf = 0
        sup = 0
        for sub_data in data: #search extrema in data
            if sub_data[2]==res[1]:
                inf = sub_data[0]
                sup = sub_data[1]
        max_len = len(str(sup))
        center_pattern = ">"+" "*max_len+" "+res[1]+"<"
        pattern = CenterOnScreen(center_pattern,16)
        positions = [pattern.index(">")+1,pattern.index(">")+max_len]
        res[0] = setNumber(line_1,pattern,positions,[inf,sup],1,res[0],True)
        for sub_data in data: #search extrema in data by unit
            if sub_data[2]==res[1]:
                #unit found
                if res[0] == sub_data[1]: #sup is reached, if possible we go one level higher
                    try:
                        res[0]=data[data.index(sub_data)+1][0]
                        res[1]=data[data.index(sub_data)+1][2]
                    except IndexError:
                        print ("max level reached, can't go higher")
                    break
                elif res[0] == sub_data[0]: #inf is reached, if possible we go one level lower
                    if data.index(sub_data) > 0:
                        res[0]=data[data.index(sub_data)-1][1]-1
                        res[1]=data[data.index(sub_data)-1][2]
                    else:
                        print ("min level reached, can't go lower")
                    break
                else:
                    return res

def setNumber(line_1,line_2_pattern,positions,extrema,step,default,ExitIfExtremaReached=False): #Interface to set a number
    inf = extrema[0]
    sup = extrema[1]
    if default<inf or default>sup:
        return
    else:
        pos = default
        mylcd.lcd_clear()
        mylcd.lcd_display_string(CenterOnScreen(line_1,16),1)
        while not encoder.isClicked():
            pattern = line_2_pattern[0:positions[0]]+str(pos).zfill(len(str(extrema[1])))+line_2_pattern[positions[1]+1:16]
            mylcd.lcd_display_string(pattern,2)
            encoder.updateCount()
            old_count = encoder.getCount()
            while(not encoder.updateCount() and not encoder.isClicked()):
                pass
            encoder.updateCount()
            new_count = encoder.getCount()
            if(new_count>old_count):
                if pos<=(sup-step):
                    pos+=step
                if ExitIfExtremaReached and pos==sup:
                    return sup
            elif(new_count<old_count):
                if ExitIfExtremaReached and pos==inf:
                    return inf
                if pos>=(inf+step):
                    pos-=step
        AntiRebound()
        return pos

def createDatePattern(Base,ExistingDigits): #Creates a date pattern to display while entering digits
    s = Base
    for digit in ExistingDigits:
        if digit[1]!=(-1):
            s = s[:digit[0]] + str(digit[1]) + s[digit[0] + 1:]
    return s

def getMAC(interface='eth0'): #Get Raspberry MAC adress and therefore allows the university IT staff to put it in their network whitelist. To call : print getMAC('eth0')
    # Return the MAC address of the specified interface
    try:
        str = open('/sys/class/net/%s/address' %interface).read()
    except:
        str = "ERROR"
    return str[0:17]

def check_DSI_file(absolute_path): #Checks validity of students list
    pass

def parse_time(time_str): #Parses time from mainconfig.ini file
    regex = re.compile(r'((?P<days>\d+?)d)?((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?')
    parts = regex.match(time_str)
    if not parts:
        return
    parts = parts.groupdict()
    time_params = {}
    for (name, param) in parts.iteritems():
        if param:
            time_params[name] = int(param)
    return datetime.timedelta(**time_params)

def timedeltaToStr(TD): #Turns a timedelta object to a string
    days = TD.days
    hours = TD.seconds/3600
    minutes = (TD.seconds/60)%60
    return str(days).zfill(2)+"d"+str(hours).zfill(2)+"h"+str(minutes).zfill(2)+"m"

def listDirectory(parentDir,list_folders,list_files,only_csv): #Lists directory content with specific restrictions. Prefer absolute path over relative ones for parentDir
    if only_csv and not list_files:
        print ("Incoherent parameters")
        return
    res = []
    for r,d,f in os.walk(parentDir):
        if list_folders:
            for directory in d:
                res.append(directory)
        if list_files:
            for file in f:
                if not only_csv or file.endswith(".csv"):
                    res.append(file)
        break #prevents from deeper search (we stop at level 1)
    return res

#FUNCTIONS ABOUT TERMINAL ACTIONS RAISED WHILE NAVIGATING IN MENU
def load_students(): #Allows administrator to load the list of students
    list_array = listDirectory('/home/pi/UTBM_TZ20/files/DSI_lists/',False,True,True)
    if len(list_array)!=0:
        list_array = sortDatetimeArray(list_array,FileDatetimeFormat,True)
        dt_current = isDateTime(list_array[0],FileDatetimeFormat) #we consider that as an earliest imported file from the same function (thanks to code below), it has the right name and content structures
        if not dt_current:
            print( "Error in old DSI_file")
            return
        buzz.warn()
        replace = YesNoBackScreen("ECRASER FICHIER IMPORTE LE "+dt_current.strftime("%d/%m/%Y A %H:%M:%S")+" ?",'y',['OUI', 'RET'],'OUI')
        if replace=='RET':
            return
    holdScreen(["INSEREZ CLE USB",">RETOUR<"],'y',0.5,True)
    USBMountPoint = getUSBPath()
    while not USBMountPoint and not encoder.isClicked():
        USBMountPoint = getUSBPath()
    if encoder.isClicked():
        AntiRebound()
        return
    buzz.success()
    print ("PATH TO USB KEY : ",USBMountPoint)
    csv_files = listDirectory(USBMountPoint,False,True,True)
    fileToCopy = USBMountPoint+"/" #copy USB root absolute path
    err_filename = "ERREURS_"
    if len(csv_files)==0:
        buzz.error()
        holdScreen(["AUCUN FICHIER CSV TROUVE","SUR LA CLE USB"],'r',1,True)
        dismount_USB(USBMountPoint)
        return
    elif len(csv_files)==1:
        fileToCopy += csv_files[0] #add the only csv file found
        err_filename+=csv_files[0]
    else:
        choice = NavigateInArray("CHOISIR FICHIER",csv_files,0,True,'y')
        if choice:
            fileToCopy+=choice
            err_filename+=choice
        else:
            dismount_USB(USBMountPoint)
            return
    fichier = Files(fileToCopy)
    check_format = fichier.checkDSIFileStructure()
    print ("CHECKING FILE ",fileToCopy," TO MATCH DSI_file FORMAT : result = ", check_format)
    if not check_format:
        err_filename = err_filename.replace(".csv",".log")
        buzz.error()
        holdScreen(["ERREUR DE STRUCTURE DU FICHIER","VOIR "+err_filename.replace(' ','_')+" SUR CLE USB"],'r',1,True)
    else:
        now = rtc_get_time().strftime(FileDatetimeFormat)
        to_delete = listDirectory('/home/pi/UTBM_TZ20/files/DSI_lists',False,True,True)
        if fichier.ImportDSIFile(now):
            for filename in to_delete:
                target = Files()
                target.deleteFile('/home/pi/UTBM_TZ20/files/DSI_lists/'+filename)
            buzz.success()
            holdScreen(["LISTE ETUDIANTS IMPORTEE","AVEC SUCCES"],'g',1,True)
        else:
            buzz.error()
            holdScreen(["ERREUR LORS DE L'IMPORTATION","DE LA LISTE DES ETUDIANTS"],'r',1,True)
    dismount_USB(USBMountPoint)

def set_bip(): #Toggle buzzer
    if buzz.enabled:
        defaultChoice = "NON"
    else:
        defaultChoice = "OUI"
    Choice = YesNoBackScreen("BIP SONORE","m",['OUI','NON','RET'],defaultChoice)
    if Choice=='OUI':
        buzz.setEnable(True)
        led.setColor("g",led)
        buzz.success()
    elif Choice=='NON':
        buzz.setEnable(False)
        led.setColor("y",led)
        time.sleep(0.2)
    update_config()

def set_datetime(): #Change date and time, either manually or automatially if connected to internet
    choice = YesNoBackScreen("CHOISIR MODE REGLAGE","m",["AUT","MAN","RET"],"AUT")
    if choice=="AUT":
        isInternet = checkInternet()
        if isInternet:
            holdScreen(["CONNEXION INTERNET OK","MaJ DATE & HEURE..."],"y",1,True)
            rtc_set_time(datetime.datetime.now())
            buzz.success()
            holdScreen(["DATE & HEURE","MISES A JOUR AVEC SUCCES"],"g",1,True)
        else:
            buzz.error()
            holdScreen(["PAS DE CONNEXION INTERNET","VEUILLEZ CONNECTER ETHERNET OU METTRE A JOUR MANUELLEMENT"],"r",1,True)
    
    elif choice=="MAN":
        holdScreen(["INDIQUEZ DATE ET HEURE","AU FORMAT 24H"],"y",1,True)
        setLedState("m")
        DateTime = rtc_get_time()
        DateTimeTuple = DateTime.timetuple()
        DateNumbers = []
        for i in range(0,3):
            DateNumbers.append(DateTimeTuple[2-i])
        DateDigits = [[6,Digit(DateNumbers[0],1),3],[7,Digit(DateNumbers[0],0),9],[9,Digit(DateNumbers[1],1),1],[10,Digit(DateNumbers[1],0),9],[12,Digit(DateNumbers[2],3),2],[13,Digit(DateNumbers[2],2),9],[14,Digit(DateNumbers[2],1),9],[15,Digit(DateNumbers[2],0),9]] #field position on screen, value, limit
        newDigits = [[6,-1],[7,-1],[9,-1],[10,-1],[12,-1],[13,-1],[14,-1],[15,-1]]
        for dig in DateDigits:
            pattern = createDatePattern("Date: JJ/MM/AAAA",newDigits)
            newDig = setDigit("MaJ DATE & HEURE",pattern,dig[0],dig[1],dig[2])
            newDigits[DateDigits.index(dig)][1] = newDig
            dig[1] = newDig
        
        try:
            DateAttempt = datetime.date(Number([DateDigits[4][1],DateDigits[5][1],DateDigits[6][1],DateDigits[7][1]]),Number([DateDigits[2][1],DateDigits[3][1]]),Number([DateDigits[0][1],DateDigits[1][1]]))
        except ValueError:
            setLedState("r")
            buzz.error()
            holdScreen(["ERREUR DATE INCOHERENTE","VEUILLEZ RECOMMENCER"],"r",1,True)
            return

        DateTime = rtc_get_time()
        DateTimeTuple = DateTime.timetuple()
        TimeNumbers = []
        for i in range(3,6):
            TimeNumbers.append(DateTimeTuple[i])
        TimeDigits = [[8,Digit(TimeNumbers[0],1),2],[9,Digit(TimeNumbers[0],0),9],[11,Digit(TimeNumbers[1],1),5],[12,Digit(TimeNumbers[1],0),9],[14,Digit(TimeNumbers[2],1),5],[15,Digit(TimeNumbers[2],0),9]]    
        newDigits = [[8,-1],[9,-1],[11,-1],[12,-1],[14,-1],[15,-1]]
        for dig in TimeDigits:
            pattern = createDatePattern("Heure : HH:MM:SS",newDigits)
            newDig = setDigit("MaJ DATE & HEURE",pattern,dig[0],dig[1],dig[2])
            newDigits[TimeDigits.index(dig)][1] = newDig
            dig[1] = newDig
        
        try:
            TimeAttempt = datetime.time(Number([TimeDigits[0][1],TimeDigits[1][1]]),Number([TimeDigits[2][1],TimeDigits[3][1]]),Number([TimeDigits[4][1],TimeDigits[5][1]]))
        except ValueError:
            setLedState("r")
            buzz.error()
            holdScreen(["ERREUR HEURE INCOHERENTE","VEUILLEZ RECOMMENCER"],"r",1,True)
            return
        
        final_dt = datetime.datetime.combine(DateAttempt,TimeAttempt)
        rtc_set_time(final_dt)


        buzz.success()
        holdScreen(["DATE ET HEURE ENREGISTREES","AVEC SUCCES :"],"g",1,True)
        currentDT = rtc_get_time()
        mylcd.lcd_display_string("Date: "+currentDT.strftime("%d/%m/%Y"), 1)
        for i in range(0,3):
            mylcd.lcd_display_string("Heure : "+currentDT.strftime("%H:%M:%S"), 2)
            time.sleep(1)
            currentDT = currentDT+datetime.timedelta(seconds=1)
    
def scanning(DT = None): #Launches the scanning procedure
    #TODO: reload previous number of scans to initialize on resume
    if not CheckAdmin():
        return
    else:
        print ("OK FOR SCANNING STUDENTS")
        if DT==None:
            now = rtc_get_time()
            UID_list = Files("/home/pi/UTBM_TZ20/files/UID_inputs/"+now.strftime(FileDatetimeFormat)+".csv")
        else:
            UID_list = Files("/home/pi/UTBM_TZ20/files/UID_inputs/"+DT+".csv")
        nb_scans = 0
        nb_err = 0
        nb_rescans = 0
        while True:
            setLedState("y")
            mylcd.lcd_clear()
            mylcd.lcd_display_string(" >SCANNEZ  SVP<",1)
            mylcd.lcd_display_string(">Nb scans : "+str(nb_scans),2)
            uid = WaitForCard(False)
            if uid == admin_uid:
                count = 3   #we use this to prevent admin from accidentally stopping scanning procedure
                while(WaitForCard(False,1)==admin_uid) and count>0:
                    holdScreen(["MAINTENEZ "+str(count)+" SEC","POUR QUITTER"],"m",0.5,True)
                    setLedState("o")
                    time.sleep(0.5)
                    count-=1
                if count==0:
                    break
            else:
                if not CheckUIDFormat(uid):
                    buzz.error()
                    holdScreen(["BADGE INCOHERENT","REESSAYEZ..."],"r",2,True)
                    print ("WRONG UID FORMAT")
                    led.setColor("m",led)
                    nb_err+=1
                else:
                    if UID_list.addStudentToFile(uid,rtc_get_time()):
                        buzz.success()
                        holdScreen([">SCAN OK<","SUIVANT..."],"g",1,True)
                        print ("SCAN N ",nb_scans," SAVED - UID = ",uid)
                        nb_scans+=1
                    else:
                        buzz.error()
                        holdScreen([">ERREUR SCAN<","CARTE DEJA SCANNEE"],"r",3,True)
                        print ("SCAN N ",nb_scans," FAILED - UID ",uid," ALREADY EXISTS IN LIST")
                        nb_rescans+=1
        nb_tot = nb_scans+nb_err+nb_rescans
        buzz.warn()
        result = str(nb_tot)+" SCANS dont "+str(nb_scans)+" SUCCES, "+str(nb_err)+" ERREUR(S) et "+str(nb_rescans)+" TENTATIVE(S) DE RESCAN"
        YesNoBackScreen("SCAN TERMINE : "+result,"g",["OK"],"OK")

def shutdown(): #Shutdown raspberry with confirmation asking
    global IsInterruptionIntentional
    rep = YesNoBackScreen("CONFIRMER EXTINCTION ?","r",["OUI","RET"],"RET")
    if(rep=="OUI"):
        buzz.shutDown()
        IsInterruptionIntentional = True
        mylcd.lcd_clear()
        mylcd.lcd_display_string("SYSTEME ETEINT",1)
        mylcd.lcd_display_string("BTN D POUR DEMARR",2)
        mylcd.backlight(0)
        setLedState("o")
        print ("SHUTDOWN REQUESTED")
        GPIO.cleanup()
        subprocess.call("sudo shutdown now", shell=True)

def restart(): #Reboot raspberry with confirmation asking
    global IsInterruptionIntentional
    rep = YesNoBackScreen("CONFIRMER REDEMARRAGE ?","r",["OUI","RET"],"RET")
    if(rep=="OUI"):
        buzz.shutDown()
        IsInterruptionIntentional = True
        mylcd.lcd_clear()
        mylcd.lcd_display_string("REDEMARRAGE EN",1)
        mylcd.lcd_display_string("COURS PATIENTEZ",2)
        mylcd.backlight(0)
        setLedState("o")
        print ("REBOOT REQUESTED")
        GPIO.cleanup()
        subprocess.call("sudo reboot now", shell=True)

def show_attendance_controls(): #Shows all attendance controls
    update_menu()

def delete_attendance_controls(): #Deletes all attendance controls
    if not CheckAdmin():
        return
    ControlList = listDirectory("/home/pi/UTBM_TZ20/files/UID_inputs",False,True,True)
    nb_ctrls = len(ControlList)
    buzz.warn()
    if nb_ctrls<=0:
        holdScreen(["AUCUN CONTROLE TROUVE","SUR LE BOITIER"],'y',2,True)
        return
    if YesNoBackScreen(str(nb_ctrls)+" CONTROLE(S) TROUVE(S), CONFIRMER SUPPRESSION ?",'r',["OUI", "RET"],"RET") == "RET":
        return
    root = "/home/pi/UTBM_TZ20/files/"
    sections = ["UID_inputs","API_outputs","Final_extractions"]
    for section in sections:
        os.system("rm -rf "+root+section+"/*")
    update_menu()
    buzz.success()
    YesNoBackScreen("SUPPRESSION REUSSIE",'g',['OK'],'OK')

def forbid_wrong_cards(): #Let user set if wrong cards (i.e. cards that are not respecting UTBM format)
    global acceptUTBMCardsOnly
    print("acceptUTBMCardsOnly is currently set to ",acceptUTBMCardsOnly)
    buzz.warn()
    holdScreen(["CONSEIL : GARDER RESTRICTION ACTIVE","SAUF POUR UTILISATION HORS UTBM"],"y",1,True)
    choice = YesNoBackScreen("ACCEPTER CARTES UTBM UNIQUEMENT","y",['OUI','NON','RET'],'OUI')
    if choice=='OUI':
        acceptUTBMCardsOnly=True
    elif choice=='NON':
        acceptUTBMCardsOnly=False
    print("acceptUTBMCardsOnly is currently now to ",acceptUTBMCardsOnly)
    update_config()

def set_interval(): #Let user set the interval of starting time in which two attendance controles are considered to be similar
    global IntervalMulti
    unit_translation = {
        "jours":"days",
        "heures":"hours",
        "mins":"minutes"
    }
    units_on_screen = {v: k for k, v in unit_translation.iteritems()}
    IM_str = timedeltaToStr(IntervalMulti)
    positionsInString = [[0,2,"days"],[3,5,"hours"],[6,8,"minutes"]]
    default = []
    for pos in positionsInString:
        nb = int(IM_str[pos[0]:pos[1]])
        if nb != 0:
            default = [nb,units_on_screen[pos[2]]]
    data = [[1,60,units_on_screen["minutes"]],[1,24,units_on_screen["hours"]],[1,10,units_on_screen["days"]]]
    res = setNumberEns("INTERVALLE MULTI",data,default)
    args = [0,0,0]
    units = ["days","hours","minutes"]
    for i in range(3):
        if res[1]==units_on_screen[units[i]]:
            args[i] = res[0]
    
    TD = datetime.timedelta(days=args[0],hours=args[1],minutes=args[2])
    print("WILL SET INTERVAL TO ",TD)
    IntervalMulti = TD
    update_config()

def set_scroll_speed(): #Let user set a scrolling speed for LCD
    global ScrollSpeed
    ScrollSpeed = setNumber("VITESSE DEFIL","     >   %<     ",[6,8],[0,100],5,ScrollSpeed)
    update_config()

def show_MAC(): #Show MAC adress of Raspberry Pi
    address = getMAC('eth0')
    if(address=="ERROR"):
        print("error while determining MAC address")
        buzz.error()
        holdScreen(["ERREUR ADRESSE","MAC INTROUVABLE"],"r",4,False)
    else:
        YesNoBackScreen("Adresse MAC : "+address,"m",['OK'],"OK")

def update_system(): #Updates sotfware by performing a git pull
    if not checkInternet():
        buzz.error()
        holdScreen(["PAS DE CONNEXION INTERNET","VEUILLEZ CONNECTER ETHERNET"],"r",1,True)
        return
    holdScreen(["RECHERCHE MaJ","EN COURS..."],'y',1,True)
    check_version = subprocess.check_output(['git','pull'],cwd="/home/pi/UTBM_TZ20")
    if check_version == 'Already up to date.\n' or check_version == 'D\xc3\xa9j\xc3\xa0 \xc3\xa0 jour.\n': #English and french returns
        buzz.warn()
        holdScreen(["SYSTEME DEJA","A JOUR"],'y',1,True)
    else:
        buzz.success()
        holdScreen(["SYSTEME MIS","A JOUR"],'g',1,True)
        version = get_version()
        version_str = version.strftime("%d/%m/%y %H:%M")
        holdScreen(["Nouvelle version",version_str],'y',3,True)
        buzz.warn()
        holdScreen(["REDEMERRAGE OBLIGATOIRE","POUR APPLIQUER LES MODIFICATIONS"],'y',1,True)
        if(YesNoBackScreen("REDEMARRER MAINTENANT ?",'y',['OUI','NON'],'OUI')=='OUI'):
            restart()

def get_version(): #Returns the date of last git pull
    date_str = subprocess.check_output(['git','log','-n','1','--pretty=format:%ad'],cwd="/home/pi/UTBM_TZ20")
    arr = date_str.split(' ')
    new_str = ' '.join(arr[:-1])
    return datetime.datetime.strptime(new_str,"%c")

""" def control_resume(datetime):
    scanning(datetime) #TODO: reload number of scans to display on screen while scanning and after scan finished
 """

def control_extract(DT): #Performs attendance control extraction
    DSI_files=listDirectory("/home/pi/UTBM_TZ20/files/DSI_lists/",False,True,True)
    DSI_files=sortDatetimeArray(DSI_files,FileDatetimeFormat,True)
    if not DSI_files:
        buzz.error()
        YesNoBackScreen("LISTE ETUDIANTS ABSENTE",'r',["OK"],"OK")
        return
    holdScreen(["INSEREZ CLE USB",">RETOUR<"],'y',0.5,True)
    USBMountPoint = getUSBPath()
    while not USBMountPoint and not encoder.isClicked():
        USBMountPoint = getUSBPath()
    if encoder.isClicked():
        AntiRebound()
        return
    buzz.success()
    print ("PATH TO USB KEY : ",USBMountPoint)
    if YesNoBackScreen("CONNECTEZ ETHERNET",'m',['RET','OK'],'OK')=="RET":
        dismount_USB(USBMountPoint)
        return
    holdScreen(["CONNEXION A LA","DSI UTBM ..."],'y',1,True)
    url = structConfig.structure["API_url"]
    try:
        print('url : ',url)
        response = urllib2.urlopen(url+ConnectionTestUID).read().decode('utf-8')
    except Exception as e:
        print ("Error while connecting to API : ",e)
        buzz.error()
        YesNoBackScreen("ECHEC CONNEXION DSI UTBM",'r',["OK"],"OK")
        dismount_USB(USBMountPoint)
        return
    buzz.success()
    holdScreen(["CONNEXION DSI UTBM","ETABLIE AVEC SUCCES"],'g',1,True)
    mode = NavigateInArray("CHOISIR MODE",["Boitier unique","Boitiers multiples"],0,True,'y')
    holdScreen(["EXTRACT. LISTES","EN COURS ..."],'m',1,True)
    file = Files(structConfig.structure["UID_inputs"]+DT+".csv")
    DSI_absolute = structConfig.structure["DSI_lists"]+DSI_files[0]
    print("Absolute path to DSI_file : ",DSI_absolute)
    file.compareDsiFilesToFileCreation(DSI_absolute,datetime.datetime.strptime(DT,FileDatetimeFormat))
    if not mode:
        dismount_USB(USBMountPoint)
        return
    elif mode == "Boitiers multiples":
        test = Files()
        previous_extraction = test.foundSameEventFile(USBMountPoint,datetime.datetime.strptime(DT,FileDatetimeFormat),IntervalMulti)
        if not previous_extraction:
            buzz.error()
            holdScreen(["AUCUNE EXTRACTION VALIDE","TROUVEE SUR CLE USB"],'r',1,True)
            dismount_USB(USBMountPoint)
            return
        buzz.success()
        holdScreen(["EXTRACTION SIMILAIRE","TROUVEE SUR CLE USB"],'g',1,True)
        if YesNoBackScreen("FUSIONNER ?",'y',['OUI','NON'],"OUI")=="OUI":
            print("Merging files on USB Key")
            holdScreen(["FUSION LISTES","EN COURS ..."],'m',1,True)
            file.addToUSBKEY(USBMountPoint,datetime.datetime.strptime(DT,FileDatetimeFormat),IntervalMulti)
            buzz.success()
            holdScreen(["FUSION REUSSIE","FICHIERS SUR CLE USB"],'g',1,True)

    elif mode == "Boitier unique":
        if not file.exportFileToUSB(USBMountPoint,DSI_absolute):
            buzz.error()
            holdScreen(["ERREUR EXPORTATION","FICHIERS CONTROLE"],'r',1,True)
            dismount_USB(USBMountPoint)
            return
        buzz.success()
        holdScreen(["EXPORTATION REUSSIE","FICHIERS SUR CLE USB"],'g',1,True)
    dismount_USB(USBMountPoint)

def prefix(base, pref): #Prefix a string
    return pref+" : "+base

def control_results(datetime): #Shows results of attendance control on LCD. Available only if extraction was performed before
    Report = Files('/home/pi/UTBM_TZ20/files/Final_extractions/'+datetime+'/report.csv')
    if not Report.exist():
        buzz.error()
        holdScreen(["EXTRACTION MANQUANTE","FAIRE EXTRACTION PUIS RECOMMENCER"],'r',1,True)
        return
    Results = Report.ParseReport()
    Results = Results[0]
    print("Control results : ",Results)
    if not Results:
        buzz.error()
        holdScreen(["ERREUR LECTURE","FICHIER REPORT"],'r',3,True)
    prefixs = ["Nb Scans","Nb Attendus","Nb Abs (%)","Nb Pres (%)","Nb Faux-Pres (%)","Duree","Erreurs API"]
    ret = []
    for res in Results:
        ret.append(prefix(res,prefixs[Results.index(res)]))
    NavigateInArray("RESULTATS CTRL",ret,0,True,'b')

def control_delete(datetime): #Deletes targetted attendance control
    global ForceLevel
    if not CheckAdmin():
        return
    buzz.warn()
    holdScreen(["ATTENTION CETTE OPERATION","EST IRREVERSIBLE"],'y',1,True)
    if YesNoBackScreen("CONFIRMER SUPPRESSION ?",'r',["OUI", "RET"],"RET")=="RET":
        return False
    print ("I WILL delete control with datetime ",datetime)
    absolute_root = "/home/pi/UTBM_TZ20/files/"
    to_delete=["API_outputs/"+datetime+".csv","Final_extractions/"+datetime,"UID_inputs/"+datetime+".csv"]
    nb_deletions = 0
    for file in to_delete:
        file=absolute_root+file
        ToDel = Files("")
        if ToDel.deleteFile(file):
            nb_deletions+=1
    print ("DELETED ",nb_deletions," files and folders (only parents are counted)")
    buzz.success()
    holdScreen(["CONTROLE SUPPRIME","AVEC SUCCES"],'g',1,True)
    ForceLevel=["main","show_attendance_controls"]
    return True

#FUNCTIONS TO CREATE MENU TREE AND UPDATE IT
def create_menu(): #Initializes main menu tree
    menu = treelib.Tree()
    menu.create_node(identifier='main',data=["","MENU PRINCIPAL",""]) #[led_color (o for off), menu_title]
    menu.root = 'main'
    menu.create_node(identifier='param',parent='main',data=["Parametrage","MENU PARAMETRAGE","w"])
    menu.create_node(identifier='scanning',parent='main',data=["Lancer scans","","g"])
    menu.create_node(identifier='show_attendance_controls',parent='main',data=["Voir controles","LISTE CONTROLES","w"])
    menu.create_node(identifier='delete_attendance_controls',parent='main',data=["Supprimer tous les controles","","r"])
    menu.create_node(identifier='restart',parent='main',data=["Redemarrer","","r"])
    menu.create_node(identifier='shutdown',parent='main',data=["Eteindre","","r"])
    menu.create_node(identifier='load_students',parent='param',data=["Charger liste etudiants","","c"])
    menu.create_node(identifier='set_datetime',parent='param',data=["Date & heure","","c"])
    menu.create_node(identifier='set_bip',parent='param',data=["Bip sonore","","c"])
    menu.create_node(identifier='set_scroll_speed',parent='param',data=["Vitesse defilement ecran","","c"])
    menu.create_node(identifier='forbid_wrong_cards',parent='param',data=["Interdire fausses cartes","","c"])
    menu.create_node(identifier='set_interval',parent='param',data=["Intervalle mode multiple","","c"])
    menu.create_node(identifier='show_MAC',parent='param',data=["Voir adresse MAC Ethernet","","c"])
    menu.create_node(identifier='update_system',parent='param',data=["Mise a jour logicielle","","g"])
    return menu

menuTree = create_menu()

def isDateTime(string, format): #Checks existence and validity of a datetime
    try:  #check filename integrity as having the right datetime format
        dt = datetime.datetime.strptime(string,format)
        return dt
    except ValueError:
        return False

def sortDatetimeArray(array,format,desc): #Sort an array of datetime strings
    newArray = []
    newDTArray = []
    for dtstr in array:
        if not isDateTime(dtstr.replace(".csv",''),format):
            print ("Error with unformatted filename ",dtstr," in folder files/UID_inputs/")
            return False
        newDTArray.append(datetime.datetime.strptime(dtstr.replace(".csv",''),format))
    newDTArray.sort(reverse=desc)
    for DT in newDTArray:
        newArray.append(DT.strftime(format))
    return newArray

def update_menu(): #Creates as many nodes and subnodes as there are files found in ../files/UID_inputs
    global menuTree
    childs = menuTree.is_branch('show_attendance_controls')
    nd = menuTree.get_node('show_attendance_controls')
    while not nd.is_leaf(): #fixes a bug of treelib remove_node function
        childs = menuTree.is_branch('show_attendance_controls')
        for id in childs:
            print ("Removed ",menuTree.remove_node(id)," nodes in total")
    UID_inputs = listDirectory("/home/pi/UTBM_TZ20/files/UID_inputs/",False,True,True)
    print (len(UID_inputs)," files have been found in UID_inputs : ",UID_inputs)
    UID_inputs = sortDatetimeArray(UID_inputs,FileDatetimeFormat,True)   #Descending sort
    for control in UID_inputs:
        dtstr = control.replace(".csv",'')
        dt = isDateTime(dtstr,FileDatetimeFormat)
        if(dt):
            dtOnScreen = dt.strftime("%d/%m/%y %H:%M")
            ctrl_ident = "control_"+dtstr
            try:
                menuTree.create_node(identifier=ctrl_ident,parent='show_attendance_controls',data=[dtOnScreen,"MENU CONTROLES",'c'])
            except treelib.exceptions.DuplicatedNodeIdError:
                print ("Node with identifier ",ctrl_ident, " already exists, so can't be created")
            """ newIdent = ctrl_ident+"_resume"
            try:
                menuTree.create_node(identifier=newIdent,parent=ctrl_ident,data=["Reprendre scans","",'y'])
            except treelib.exceptions.DuplicatedNodeIdError:
                print ("Node with identifier ",newIdent, " already exists, so can't be created") """
            newIdent = ctrl_ident+"_extract"
            try:
                menuTree.create_node(identifier=newIdent,parent=ctrl_ident,data=["Extraire fichiers","",'g'])
            except treelib.exceptions.DuplicatedNodeIdError:
                print ("Node with identifier ",newIdent, " already exists, so can't be created")
            newIdent = ctrl_ident+"_results"
            try:
                menuTree.create_node(identifier=newIdent,parent=ctrl_ident,data=["Voir resultats","",'c'])
            except treelib.exceptions.DuplicatedNodeIdError:
                print ("Node with identifier ",newIdent, " already exists, so can't be created")
            newIdent = ctrl_ident+"_delete"
            try:
                menuTree.create_node(identifier=newIdent,parent=ctrl_ident,data=["Supprimer controle","",'r'])
            except treelib.exceptions.DuplicatedNodeIdError:
                print ("Node with identifier ",newIdent, " already exists, so can't be created")

def sigterm_handler(_signo, _stack_frame): #HANDLER FUNCTION FOR SIGTERM SIGNAL
    print('Sigterm Interrupted')
    led.shutDown()
    if not IsInterruptionIntentional:
        mylcd.lcd_clear()
        mylcd.lcd_display_string("EXTINCTION",1)
        mylcd.lcd_display_string("BATTERIE FAIBLE",2)
    mylcd.backlight(0)
    GPIO.cleanup()
    sys.exit(0)
signal.signal(signal.SIGTERM, sigterm_handler) #associates SIGTERM signal with its handler

#FUNCTIONS ABOUT CONFIG FILE
def check_config(): #Checks validity of mainconfig.ini
    a = parser.read(ConfigFileName)
    if len(a)==0:
        print ("Config file named ",ConfigFileName," was not found")
        return False
    if not parser.has_section('settings'):
        print ("No settings section in config file")
        return False
    for expectedOption in ['acceptUTBMCardsOnly','buzzEnabled','ScrollSpeed','IntervalMulti']:
        if not parser.has_option('settings',expectedOption):
            print ("Option ",expectedOption," was not found in settings section of config file")
            return False
    return True

def StrToBool(string):
    if string=='True':
        return True
    else:
        return False

parser = SafeConfigParser()

def read_config(): #Parse and read mainconfig.ini
    global acceptUTBMCardsOnly
    global ScrollSpeed
    global IntervalMulti
    parser.read(ConfigFileName)
    if not check_config():
        print ("error while reading config file")
        return
    acceptUTBMCardsOnly = StrToBool(parser.get('settings','acceptUTBMCardsOnly'))
    ScrollSpeed = int(parser.get('settings','ScrollSpeed'))
    buzz.setEnable(StrToBool(parser.get('settings','buzzEnabled')))
    IntervalMulti = parse_time(str(parser.get('settings','IntervalMulti')))

def update_config(): #Updates mainconfig.ini
    if not check_config():
        print ("error while updating config file")
        return
    parser.set('settings', 'acceptUTBMCardsOnly', str(acceptUTBMCardsOnly))
    parser.set('settings', 'buzzEnabled', str(buzz.isEnabled()))
    parser.set('settings', 'ScrollSpeed', str(ScrollSpeed))
    parser.set('settings', 'IntervalMulti', timedeltaToStr(IntervalMulti))
    with open(ConfigFileName, 'w') as configfile:
        parser.write(configfile)
    print ("config file named ",ConfigFileName, " has been updated")

read_config()

#STARTUP FUNCTION
def start(): #Start sequence
    global version
    global admin_uid
    #blink lcd backlight 2 times, starting from low
    for i in range(0,3):
        mylcd.backlight(0)
        time.sleep(0.05)
        mylcd.backlight(1)
        buzz.play([[700,5,0]])
        time.sleep(0.05)
    
    time.sleep(0.5)
    buzz.start()
    led.setColor("g",led)
    mylcd.lcd_display_string(" CONTROLEUR DE", 1)
    mylcd.lcd_display_string(" PRESENCE UTBM", 2)

    time.sleep(2)

    led.setColor("y",led)
    mylcd.lcd_clear()
    mylcd.lcd_display_string("PROJET TZ20 2020", 1)
    mylcd.lcd_display_string("Tduvinage Vmercy", 2)

    isInternet = checkInternet()
    if isInternet:
        rtc_set_time(datetime.datetime.now())
        print ("INTERNET CONNEXION IS OK, DATETIME UPDATED")
    else:
        print ("Warning : no internet connexion, can't update datetime to RTC")
      
    time.sleep(2)
    currentDT = rtc_get_time()
    mylcd.lcd_clear()
    mylcd.lcd_display_string("Date :  "+currentDT.strftime("%d/%m/%y"), 1)
    for i in range(0,3):
        mylcd.lcd_display_string("Heure : "+currentDT.strftime("%H:%M:%S"), 2)
        time.sleep(1)
        currentDT = currentDT+datetime.timedelta(seconds=1)
    version = get_version()
    version_str = version.strftime("%d/%m/%y %H:%M")
    print ("RUNNING VERSION : ",version_str)
    holdScreen(["Derniere MaJ :",version_str],'y',3,True)
    admin_uid = RecordAdmin()

def main():
    print ("--------------------------------NEW SESSION")
    now = rtc_get_time()
    print ("MAIN PROGRAM started at : ",now.strftime('%d-%m-%y - %H:%M:%S'))
    if enableStart:
        start()
    else:
        isInternet = checkInternet()
        if isInternet:
            rtc_set_time(datetime.datetime.now())
            print ("INTERNET CONNEXION IS OK, DATETIME UPDATED")
        else:
            print ("Warning : no internet connexion, can't update datetime to RTC")
    print ("admin_uid is now set to "+admin_uid)
    mylcd.backlight(1)
    led.shutDown()
    mylcd.lcd_clear()
    Menu('main','param')
    led.shutDown()
    mylcd.backlight(0)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Keyboard Interrupted')
        led.shutDown()
        mylcd.lcd_clear()
        mylcd.lcd_display_string("INTERRUPTION",1)
        mylcd.lcd_display_string("PAR CLAVIER",2)
    finally:
        mylcd.backlight(0)
        GPIO.cleanup()
