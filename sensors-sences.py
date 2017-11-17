
# coding: utf-8

# In[1]:

import time
import grovepi

# LCD
import decimal
# from grovepi import *
import drivers.grove_rgb_lcd #import *
import drivers.grove_oled #import *

# Auxilary packages
import random as rd


# In[16]:

noiseTreshold = 700
distanceTreshold0 = 10
distanceTreshold1 = 400

# Connected devices

Devices = {
    'sound_sensor': 0,
    'led_red': 4,
    'led_green': 3,
    'dht_sensor': 7,
    'ultrasonic_ranger': 8
}

LatestReadings = {
    'humidity': 0.0,
    'temperature': 0.0,
    'sound': 0.0,
    'distance': 0.0
}

sentences_sound = [
        "I've heard a noise!", 
        "Who's there?", 
        'I can hear you!',
        'Clap-clap!'
        ]
sentences_distance0 = [
        'This is my eye.', 
        'Hey! This is quite close emough!', 
        'This is an ultrasonic sensor',
        'Proximity alert!'
        ]
sentences_distance1 = [
        'I can see you!', 
        'Who is there?', 
        'Someone is standing in front of me.',
        'Hello?'
        ]


# In[1]:

grovepi.pinMode(Devices['led_red'],"OUTPUT")
grovepi.pinMode(Devices['led_green'],"OUTPUT")


# In[12]:

# INPUT devices

def FtoC( tempf ):
    return round((tempf - 32) / 1.8, 2)

def read_dht():
    try:
        return grovepi.dht(Devices['dht_sensor'], 0)
    except:
        return [-1,-1]

def read_ultrasonic():
    try:
        return grovepi.ultrasonicRead(Devices['ultrasonic_ranger'])
    except:
        return -1

def read_sound():
        try:
            return grovepi.analogRead(Devices['sound_sensor'])
        except:
            return -1
    
def updateLatestReadings(ht,s,d):
    LatestReadings.update({
        'humidity': ht[0],
        'temperature': ht[1],
        'sound': s,
        'distance': d})
    
def readSensors():    
    try:
        distance = read_ultrasonic()
        sound = read_sound()
        ht = read_dht()
    except IOError:
        print("Error")

    updateLatestReadings(ht,sound,distance) 

print(LatestReadings)
readSensors()
print(LatestReadings)


# In[30]:

# OUTPUT devices
class LCD:                
    def __init__(self):
        self.dpR, self.dpG, self.dpB = 100, 100, 100
        self.dpText = ''
        self.busy = False
        self.sinktank = []
        
    class Message:
        def __init__(self, text, duration, colour):
            self.text = text
            self.duration = duration
            self.colour = colour
    
    def reset(self):
        drivers.grove_rgb_lcd.setRGB(0,0,0)
        drivers.grove_rgb_lcd.setText('')    
        
    def updateColour(self):
        drivers.grove_rgb_lcd.setRGB(self.dpR, self.dpG, self.dpB)     
        
    def updateColourVar(self,r,g,b):
        self.dpR, self.dpG, self.dpB = r, g, b
        self.updateColour()
        
    def defaultColour(self):
        self.dpR, self.dpG, self.dpB = 100,100,100  
        self.updateColour()
    
    def updateText(self,):
        drivers.grove_rgb_lcd.setText(self.dpText)
        
    def updateTextVar(self, text=''):
        self.dpText = text
        self.updateText()
        
    def newMessage(self, text, duration=1.0, colour=[10,10,10]):
        self.sinktank.append(self.Message(text,duration,colour))
        
    def popMessage(self, message):
        drivers.grove_rgb_lcd.setRGB(message.colour[0], message.colour[1], message.colour[2])
        drivers.grove_rgb_lcd.setText(message.text)
        try:
            self.sinktank.pop(0)
        except:
            print('Error: Message: List is already empty')
        time.sleep(message.duration)
    
    def processfunction(self):
        while True:
            if len(self.sinktank) > 0:
                if not self.busy:
                    self.busy = True
                    self.popMessage(self.sinktank[0])
                    self.busy = False
                    self.updateColour()
                    self.updateText()
            else:
                break

def resetLEDs():      
    grovepi.analogWrite(Devices['led_red'],0)
    grovepi.analogWrite(Devices['led_green'],0)    


# In[31]:

lcd = LCD()

resetLEDs()
lcd.reset()

lcd.defaultColour()


# In[32]:

lcd.newMessage('hello0', duration=1.0, colour=[10,200,200])
lcd.newMessage('hello1', duration=1.0, colour=[10,200,100])
lcd.newMessage('hello2', duration=1.0, colour=[200,100,10])

lcd.sinktank


# In[34]:

lcd.processfunction()


# In[11]:

def mainEvent():    
    
    try:
        while True:
            lcdTriggered = False

            # timebreak
            time.sleep(0.1)

            # reading from sensors and changing LEDS accordingly        
            # -sound
            sound = grovepi.analogRead(Devices['sound_sensor'])
            grovepi.analogWrite(Devices['led_green'],sound)

            # -distance
            distance = grovepi.ultrasonicRead(Devices['ultrasonic_ranger'])
            if distance < distanceTreshold0:
                grovepi.analogWrite(Devices['led_red'],1000)
            else:            
                grovepi.analogWrite(Devices['led_red'],0)

            # -humidity & temperature
            [temp, hum] = grovepi.dht(Devices['dht_sensor'], 0)


            # write to CSV                
            #print('%d         ' % s, end='\r', flush=True)


            # message on LCD ?

            if sound > noiseTreshold:             
                lcd.newMessage(sentences_sound[rd.randint(0,len(sentences_sound)-1)], duration=2.0, colour=[10,10,200])
                lcdTriggered = True

            if distance < distanceTreshold0:
                lcd.newMessage(sentences_distance[rd.randint(0,len(sentences_distance0)-1)], duration=2.0, colour=[10,200,10])
                lcdTriggered = True
            elif distance < distanceTreshold1:
                lcd.newMessage(sentences_distance[rd.randint(0,len(sentences_distance1)-1)], duration=2.0, colour=[10,200,10])
                lcdTriggered = True


            if lcdTriggered:
                lcdTriggered = False
                grovepi.analogWrite(Devices['led_red'],1000)
                grovepi.analogWrite(Devices['led_green'],1000)

                lcd.processfunction()        
                resetLEDs()  
                
    except (KeyboardInterrupt, SystemExit):
        resetLEDs()
        lcd.reset()
        break
            

mainEvent()


# In[40]:

resetLEDs()

lcd.dpText = ''
lcd.updateText()


# In[1]:

import numpy as np
import time

cycle = 1.0 - 0.001307

def prototype():    
    while True:
        try:
        
    #         lcdTriggered = False

            # timebreak
    #         time.sleep(cycle)
            timestamp = time.time()

            # reading from sensors and changing LEDS accordingly        
            # -sound
            sound = np.random.randint(1023)

            # -distance
            distance = np.random.randint(520)

            # -humidity & temperature
            [temp, hum] = [np.random.randint(80), np.random.randint(100)]



            # write to CSV    
            print("%f, %d, %d, %d, %d\r" % (timestamp,distance,hum,sound,temp))#, end='\r', flush=True)
    #         print('%d         ' % sound, end='\r', flush=True)

            # sync
            time.sleep(cycle - ((time.time() - timestamp) % cycle))

        except (KeyboardInterrupt, SystemExit):
            print('Invoke reset command here')
            break


prototype()


# In[58]:

import time

period = 1.0
starttime = time.time()
while True:
    print("%f" % time.time())
    


# In[75]:

from datetime import datetime
from pytz import timezone

fmt = "%Y-%m-%d %H:%M:%S %Z%z"
now_time = datetime.now(timezone('UTC'))
print(now_time.strftime(fmt))


# In[81]:

time.time()


# In[76]:

import sched, time

period = 1.0
s = sched.scheduler(time.time, time.sleep)

def do_something(sc): 
    print("%f" % time.time())
    s.enter(period, 100, do_something, (sc,))

s.enter(period, 100, do_something, (s,))
s.run()  


# In[102]:

from threading import Timer

class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


print("starting...")
rt = RepeatedTimer(7, prototype) # it auto-starts, no need of rt.start()

https://stackoverflow.com/questions/474528/what-is-the-best-way-to-repeatedly-execute-a-function-every-x-seconds-in-python

#Just lock your time loop to the system clock. Easy.

import time
starttime=time.time()
while True:
  print "tick"
  time.sleep(60.0 - ((time.time() - starttime) % 60.0))
  
#Use the sched module, which implements a general purpose event scheduler.

import sched, time
s = sched.scheduler(time.time, time.sleep)
def do_something(sc): 
    print "Doing stuff..."
    # do your stuff
    s.enter(60, 1, do_something, (sc,))

s.enter(60, 1, do_something, (s,))
s.run()  
# In[57]:

# from grovepi import *
# from grove_oled import *


#Start and initialize the OLED
oled_init()
oled_clearDisplay()
oled_setNormalDisplay()
oled_setVerticalMode()
time.sleep(.1)

while True:
    try:
        [ temp,hum ] = dht(dht_sensor,1)		#Get the temperature and Humidity from the DHT sensor
        string = "temp ="+ str(temp)+ "C\thumidity ="+ str(hum)+"%"
        print(string, end='\r', flush=True)
        t = str(temp)
        h = str(hum)

        oled_setTextXY(0,1)			#Print "WEATHER" at line 1
        oled_putString("WEATHER")

        oled_setTextXY(2,0)			#Print "TEMP" and the temperature in line 3
        oled_putString("Temp:")
        oled_putString(t+'C')

        oled_setTextXY(3,0)			#Print "HUM :" and the humidity in line 4
        oled_putString("Hum :")
        oled_putString(h+"%")
    except (IOError,TypeError) as e:
        print("Error", end='\r', flush=True)



# In[228]:

import decimal
from grovepi import *
from drivers.grove_rgb_lcd import *


dht_sensor_port = 7     # Connect the DHt sensor to port 7
lastTemp = 0.1          # initialize a floating point temp variable
lastHum = 0.1           # initialize a floating Point humidity variable
tooLow = 62.0           # Lower limit in fahrenheit
justRight = 68.0        # Perfect Temp in fahrenheit
tooHigh = 74.0          # Temp Too high


# Function Definitions
def CtoF( tempc ):
   "This converts celcius to fahrenheit"
   tempf = round((tempc * 1.8) + 32, 2);
   return tempf;

def FtoC( tempf ):
   "This converts fahrenheit to celcius"
   tempc = round((tempf - 32) / 1.8, 2)
   return tempc;

def calcColorAdj(variance):     # Calc the adjustment value of the background color
    "Because there is 6 degrees mapping to 255 values, 42.5 is the factor for 12 degree spread"
    factor = 42.5;
    adj = abs(int(factor * variance));
    if adj > 255:
        adj = 255;
    return adj;

def calcBG(ftemp):
    "This calculates the color value for the background"
    variance = ftemp - justRight;   # Calculate the variance
    adj = calcColorAdj(variance);   # Scale it to 8 bit int
    bgList = [0,0,0]               # initialize the color array
    if(variance < 0):
        bgR = 0;                    # too cold, no red
        bgB = adj;                  # green and blue slide equally with adj
        bgG = 255 - adj;
        
    elif(variance == 0):             # perfect, all on green
        bgR = 0;
        bgB = 0;
        bgG = 255;
        
    elif(variance > 0):             #too hot - no blue
        bgB = 0;
        bgR = adj;                  # Red and Green slide equally with Adj
        bgG = 255 - adj;
        
    bgList = [bgR,bgG,bgB]          #build list of color values to return
    return bgList;

while True:

    try:
        temp = 0.01
        hum = 0.01
        [ temp,hum ] = dht(dht_sensor_port,0)       #Get the temperature and Humidity from the DHT sensor
                                                    #Change the second parameter to 0 when using DHT (instead of DHT Pro)
                                                    #You will get very large number values if you don't!
        if (CtoF(temp) != lastTemp) and (hum != lastHum) and not math.isnan(temp) and not math.isnan(hum):
                print("lowC : ",FtoC(tooLow),"C\t\t","rightC  : ", FtoC(justRight),"C\t\t","highC : ",FtoC(tooHigh),"C") # comment these three lines
                print("lowF : ",tooLow,"F\t\tjustRight : ",justRight,"F\t\ttoHigh : ",tooHigh,"F")                       # if no monitor display
                print("tempC : ", temp, "C\t\ttempF : ",CtoF(temp),"F\t\tHumidity =", hum,"%\r\n")
                
                lastHum = hum          # save temp & humidity values so that there is no update to the RGB LCD
#                 ftemp = CtoF(temp)     # unless the value changes
                lastTemp = temp       # this reduces the flashing of the display
                # print "ftemp = ",ftemp,"  temp = ",temp   # this was just for test and debug
                
                bgList = calcBG(temp)           # Calculate background colors
                
                t = str(temp)   # "stringify" the display values
                h = str(hum)
                # print "(",bgList[0],",",bgList[1],",",bgList[2],")"   # this was to test and debug color value list
                setRGB(bgList[0],bgList[1],bgList[2])   # parse our list into the color settings
                setText("Temp:" + t + "C      " + "Humidity :" + h + "%") # update the RGB LCD display
                
    except (IOError,TypeError) as e:
        print("Error" + str(e))
    


