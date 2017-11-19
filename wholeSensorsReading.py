# GrovePi
import grovepi

# LCD
import decimal
import drivers.grove_rgb_lcd #import *
import drivers.grove_oled #import *

# Auxilary packages
import time, math, csv
import random as rd
import numpy as np

noiseTreshold = 700
distanceTreshold0 = 10
distanceTreshold1 = 600

# Connected devices
Devices = {
    'sound_sensor': 0,    
    'co2_sensor': 1,
    'photoresistor': 2,
    'led_red': 4,
    'led_green': 3,
    'led_yellow': -1,
    'dht_sensor': 7,
    'ultrasonic_ranger': 8
}

#sentences that will appear if a sensor theshold is exceeded
sentences_sound = [
        "I've heard a noise!", 
        "Who's there?", 
        'I can hear you!',
        'Who is making noise?'
        ]
sentences_distance0 = [
        'This is my eye.', 
        'Hey!', 
        'This is an ultrasonic sensor',
        'Proximity alert!'
        ]
sentences_distance1 = [
        'I can see you!', 
        'Who is there?', 
        'Someone is in front of me.',
        'Hello?'
        ]

# OUTPUT devices
class LCD:                
    def __init__(self):
        self.dpR, self.dpG, self.dpB = 100, 100, 100
        self.dpText = ''
        self.busy = False
        self.pendingMessages = []
        
    class Message:
        def __init__(self, text, colour):
            self.text = text
            self.colour = colour
    
    def reset(self):
        self.deletePendingMessages()
        drivers.grove_rgb_lcd.setRGB(0,0,0)
        drivers.grove_rgb_lcd.setText('')        
        
    def updateColour(self):
        if not self.busy:
            drivers.grove_rgb_lcd.setRGB(self.dpR, self.dpG, self.dpB)     
        
    def updateColourVar(self,r,g,b):
        self.dpR, self.dpG, self.dpB = r, g, b
        self.updateColour()
        
    def defaultColour(self):
        self.dpR, self.dpG, self.dpB = 100,100,100  
        self.updateColour()
    
    def updateText(self,):
        if not self.busy:
            drivers.grove_rgb_lcd.setText(self.dpText)
        
    def updateTextVar(self, text=''):
        self.dpText = text
        self.updateText()
        
    def newMessage(self, text, colour=[10,10,10]):
        self.pendingMessages.append(self.Message(text,colour))
        
    def popMessage(self, message):
        drivers.grove_rgb_lcd.setText(message.text)
        drivers.grove_rgb_lcd.setRGB(message.colour[0], message.colour[1], message.colour[2])        
        try:
            self.pendingMessages.pop(0)
        except:
            print('Error: Message: List is already empty')
#         time.sleep(message.duration)
    
    def displayMessage(self):
        self.busy = True
        if len(self.pendingMessages) > 0:
            self.popMessage(self.pendingMessages[0])                
                
    def endDisplayMessage(self):
        self.busy = False
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
    
def mainEvent(fps = 10.0, lcd_fps = 0.5):    
    
    spf = 1 / fps
    lcdMain_spf = 1 / lcd_fps

    messageDuration = 3.0

    lcd = LCD()
#     resetLEDs()

    frametime = spf    
    lcdMain_frametime = lcdMain_spf
    lcdMain_starttime = time.time()    
    
    lcdMessage_starttime = 3.0
    lcdMessage_frametime = 3.0    
    
    messageInProgress = False
    
    lcd.defaultColour()
    
    while True:   
        try:
            if frametime >= spf:
                starttime = time.time()               
            
                try:
                    # reading from sensors and changing LEDS accordingly  
                    # ---sound                
                    sound = grovepi.analogRead(Devices['sound_sensor'])                
                    # ---light                
                    light = grovepi.analogRead(Devices['photoresistor'])  
                    # ---distance
                    distance = grovepi.ultrasonicRead(Devices['ultrasonic_ranger'])
                except TypeError:
                    sound,light,distance = -1,-1,-1
            
                # ---humidity & temperature
                [temp, hum] = grovepi.dht(Devices['dht_sensor'], 0)                
                # ---gas
#                 gas = grovepi.analogRead(Devices['gas_sensor'])  

                # LED reaction 
#                 grovepi.analogWrite(Devices['led_green'],int(light/4))
#                 grovepi.analogWrite(Devices['led_green'],int(sound/4))
                
#                 if distance < distanceTreshold0:
#                     grovepi.analogWrite(Devices['led_red'],255)
#                 else:   
#                     grovepi.analogWrite(Devices['led_red'],0)
                    
#                 if not math.isnan(light):                        
#                     grovepi.analogWrite(Devices['led_green'],255-int(light/4))
                    
                # write to CSV                
                t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(starttime))
                print('%s, %d, %d,%d, %1.f, %1.f' % (t,distance,light,sound,hum,temp), end='\r', flush=True)
                
                # message on LCD ?
                if not messageInProgress:
                    if sound > noiseTreshold:     
                        sentence = rd.randint(0,len(sentences_sound)-1)
                        lcd.newMessage(sentences_sound[sentence], colour=[10,200,200])

                    if distance < distanceTreshold0 and distance>0:
                        sentence = rd.randint(0,len(sentences_distance0)-1)
                        lcd.newMessage(sentences_distance0[sentence], colour=[200,200,10])
                    
                
                if len(lcd.pendingMessages) > 0:   

                    if not messageInProgress:
                        lcdMessage_starttime = time.time()
                        lcd.displayMessage() 
                        messageInProgress = True

                if lcdMessage_frametime >= messageDuration:
                    lcd.endDisplayMessage()     
                    messageInProgress = False
                    
                if lcdMain_frametime >= lcdMain_spf:
                    if not messageInProgress:
                        lcdMain_starttime = time.time() 
                        stringForLCD = 'lumi temp  humid%4d%5.1fC%5.1f%%' % (light, temp, hum)
#                         stringForLCD = 'lumi temp  humid'+str(int(light*999/1024))+'  '+str(temp)+'C '+str(hum)+'%'
                        lcd.updateTextVar(stringForLCD)
                        lcd.updateText()
                
            # FIXED TIME STEP technique
            frametime = time.time() - starttime
            lcdMain_frametime = time.time() - lcdMain_starttime
            lcdMessage_frametime = time.time() - lcdMessage_starttime
            # UPDATE LCD 
        except (KeyboardInterrupt, SystemExit):
#             resetLEDs()            
            lcd.reset()
            break
            
mainEvent(1)