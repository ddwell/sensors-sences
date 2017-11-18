import time
import grovepi

# LCD
import decimal
# from grovepi import *
import drivers.grove_rgb_lcd #import *
import drivers.grove_oled #import *

# Auxilary packages
import random as rd

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

# OUTPUT devices
class LCD:                
    def __init__(self):
        self.dpR, self.dpG, self.dpB = 100, 100, 100
        self.dpText = ''
        self.busy = False
        self.pendingMessages = []
        
    class Message:
        def __init__(self, text, duration, colour):
            self.text = text
            self.duration = duration
            self.colour = colour
    
    def reset(self):
        lcd.deletePendingMessages()
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
        self.pendingMessages.append(self.Message(text,duration,colour))
        
    def popMessage(self, message):
        drivers.grove_rgb_lcd.setRGB(message.colour[0], message.colour[1], message.colour[2])
        drivers.grove_rgb_lcd.setText(message.text)
        try:
            self.pendingMessages.pop(0)
        except:
            print('Error: Message: List is already empty')
#         time.sleep(message.duration)
    
    def displayMessage(self):
        if len(self.pendingMessages) > 0:
            self.popMessage(self.pendingMessages[0])                
                
    def endDisplayMessage(self):
        self.updateColour()
        self.updateText()
        
    def deletePendingMessages(self):
        for i,x in enumerate(self.pendingMessages):
            self.pendingMessages.pop(i)

def resetLEDs():      
    grovepi.pinMode(Devices['led_red'],"OUTPUT")
    grovepi.pinMode(Devices['led_green'],"OUTPUT")
    grovepi.analogWrite(Devices['led_red'],0)
    grovepi.analogWrite(Devices['led_green'],0)    
    
    
fps = 30.0
spf = 1.0 / fps 

messageDuration = 2.0

lcd = LCD()
resetLEDs()

def mainEvent():
    frametime = spf
    lcdMessage_starttime = 0
    lcdMessage_frametime = 0
    
    messageInProgress = False
    
    lcd.defaultColour()
    
    while True:
        try:
            if frametime >= spf:
                
                starttime = time.time()                
            
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
                print('%f, %f, %f, %f, %f       ' % (starttime,distance,hum,sound,temp), end='\r', flush=True)

                # message on LCD ?
                if not messageInProgress:
                    if sound > noiseTreshold:     
                        sentence = rd.randint(0,len(sentences_sound)-1)
                        lcd.newMessage(sentences_sound[sentence], duration=2.0, colour=[10,10,200])

                    if distance < distanceTreshold0:
                        sentence = rd.randint(0,len(sentences_distance0)-1)
                        lcd.newMessage(sentences_distance0[sentence], duration=2.0, colour=[200,200,10])
                
#                     elif distance < distanceTreshold1:
#                         sentence = rd.randint(0,len(sentences_distance1)-1)
#                         lcd.newMessage(sentences_distance1[sentence], duration=2.0, colour=[10,200,10])
                
                if len(lcd.pendingMessages) > 0:   
                    
                    if not messageInProgress:
                        lcdMessage_starttime = time.time()
                        lcd.displayMessage() 
                        messageInProgress = True
                        
                if lcdMessage_frametime >= messageDuration:                            
                    lcd.endDisplayMessage()     
                    messageInProgress = False
            
                lcdMessage_frametime = time.time() - lcdMessage_starttime
            
            # FIXED TIME STEP technique
            frametime = time.time() - starttime
            # UPDATE LCD    
                
        except (KeyboardInterrupt, SystemExit):
            resetLEDs()            
            lcd.reset()
            break

mainEvent()