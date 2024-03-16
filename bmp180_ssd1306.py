# uP libraries 
from time import time,sleep, gmtime
from os import stat

# Peripheral Drivers
from machine import Pin, SoftI2C, Timer
import bmp180A
from bh1750 import BH1750
from ssd1306 import SSD1306_I2C

# Subroutines
import FSRconnect
import HTTPResponse

# set up the bh1750 and its reading function
i2c2 = SoftI2C(sda = Pin(2), scl = Pin(3), freq = 1000000)
bh1750 = BH1750(0x23, i2c2)

def bh1750Read():
    bh1750.measurement
    Reading={"SensorID":2,"ReadingPoint":time(),"ReadingValue":(bh1750.measurement,),"ReadingType":("Illumination",)}
    return Reading

# Set up the BMP180 and its reading function
i2c0 = SoftI2C(sda = Pin(0), scl = Pin(1), freq = 1000000)
bmp = bmp180A.BMP180(i2c0)
bmp.oversample = 2

def bmp180Read():
    Reading={"SensorID":1,"ReadingPoint":time(),"ReadingValue":(bmp.temperature,bmp.pressure),"ReadingType":("Temperature","Pressure")}
    return Reading

# Set up the display and its show function
i2c1 = SoftI2C(sda = Pin(26), scl = Pin(27), freq = 1000000) #i2c detains
WIDTH = 128 
HEIGHT = 64
display = SSD1306_I2C(WIDTH,HEIGHT,i2c1)

def ssd1306Display(ReadingsList):
    Updated = f'{gmtime(ReadingsList[0].get('ReadingPoint',None))[3]:02}'+":"+f'{gmtime(ReadingsList[0].get('ReadingPoint',None))[4]:02}'+":"+f'{gmtime(ReadingsList[0].get('ReadingPoint',None))[5]:02}'
    display.fill(0)
    display.text(f"Update: {Updated}",0,00)
    display.text(f"Temp:   {ReadingsList[0].get('ReadingValue',[None,None])[0]:.1f} C",0,20)
    display.text(f"Pres: {ReadingsList[0].get('ReadingValue',[None,None])[1]:.1f} kPa",0,35)
    display.text(f"Illum:{ReadingsList[1].get('ReadingValue',[None,None])[0]:.1f} ",0,50)
    display.show()
 
# Set up the log file and its write function
datafile="/savedata.txt"
with open(datafile, 'a') as f:
    pass

def logData(ReadingsList):
    if(stat(datafile)[6] < 200000):
        try:
            with open(datafile, 'a') as f:
                f.write(str(ReadingsList))
                f.write('\n')
                print("File Written")
        except:
                print("Error! Could not save")
                
# set up the log write timer
def logFileTimerTrue(timer):
    global logFileTimerFlag
    logFileTimerFlag = True

logFileTimerFlag=False
logInterval = 60000 #milliseconds
logTimer = Timer()
logTimer.init(mode = Timer.PERIODIC, callback = logFileTimerTrue, period = logInterval)

connection = False
lastReadingsValues = None

SensorList=[bmp180Read,bh1750Read]

while True:
    ReadingsList=[]
    ReadingsValues=[]
    for sensors in SensorList:
        SensorReading=sensors()
        ReadingsList.append(SensorReading)
        ReadingsValues.append(SensorReading.get("ReadingValue"))
    print(ReadingsList)
    ssd1306Display(ReadingsList)
    if logFileTimerFlag == True and ReadingsValues != lastReadingsValues:
        logData(ReadingsList)
        logFileTimerFlag = False
        lastReadingsValues = ReadingsValues

    if connection is not False:
        try:
            cl, addr = connection.accept()
            cl.settimeout(3.0)
            request = cl.recv(1024)
            response=HTTPResponse.HTTPParse(request, cl, ReadingsList, datafile)
            
        except OSError as e:
            try:
                cl.close()
            except:
                print(e)
    else:
    # Tries to connect to FSR - if not connection is False
        connection = FSRconnect.connect()

    sleep(1)
