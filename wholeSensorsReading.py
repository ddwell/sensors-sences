from __future__ import print_function

# GrovePi
import grovepi# import *

# LCD
from drivers.LCD import *
# import decimal
# import drivers.grove_rgb_lcd as grove_rgb_lcd  #import *
# import drivers.grove_oled as grove_oled #import *

# Auxilary packages
import time, math, csv
import random as rd
import numpy as np

noiseTreshold = 700
distanceTreshold0 = 30
distanceTreshold1 = 600
lightTreshold = 100

# Connected devices
Devices = {
    'sound_sensor': 0,    
    'co2_sensor': 1,
    'photoresistor': 2,
    'led_red': 4,
    'led_green': 3,
    'led_yellow': 2,
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
        'This is ultrasonic sensor', 
        'Hello there!', 
        'Ultrasonic sensor says it is close',
        'Proximity alert!'
        ]
sentences_distance1 = [
        'I can see you!', 
        'Who is there?', 
        'Someone is in front of me.',
        'Hello?'
        ]
sentences_light = [
        'This is dark', 
        'Who turned off the light?', 
        'Did you cover photo diod?',
        'Photo diod says it is dark'
        ]

computationalSpeed = []

def resetLEDs():      
    grovepi.pinMode(Devices['led_red'],"OUTPUT")
    grovepi.pinMode(Devices['led_green'],"OUTPUT")
    grovepi.pinMode(Devices['led_yellow'],"OUTPUT")
    grovepi.analogWrite(Devices['led_green'],0) 
    grovepi.digitalWrite(Devices['led_yellow'],0)
    grovepi.digitalWrite(Devices['led_red'],0)
    
def rectify(param,paramTreshold):
    if param < paramTreshold:
        return 1
    else:   
        return 0 

def mainEvent(fps = 1.0, lcd_fps = 0.25, messageDuration = 3.0):       
    
    spf = 1 / fps
    lcdMain_spf = 1 / lcd_fps  
    frametime = spf    
    lcdMain_frametime = lcdMain_spf
    lcdMain_starttime = time.time()        
    lcdMessage_starttime = 3.0
    lcdMessage_frametime = 3.0   
    messageInProgress = False
    
    lcd = LCD()
    resetLEDs()
    dst_prev, dst_next = 0, 0
    lt_prev, lt_next = 0, 0
    lcd.defaultColour()
    
    try:
        while True: 
            
            if frametime >= spf:
                starttime = time.time()               
            
                # reading from sensors        
                sound = grovepi.analogRead(Devices['sound_sensor'])              
                light = grovepi.analogRead(Devices['photoresistor'])
                distance = grovepi.ultrasonicRead(Devices['ultrasonic_ranger'])
                [temp, hum] = grovepi.dht(Devices['dht_sensor'], 0)        
#                 gas = grovepi.analogRead(Devices['gas_sensor'])  
                
                #LED reaction
                grovepi.analogWrite(Devices['led_green'],int(sound/4))
                #grovepi.analogWrite(Devices['led_green'],255-int(light/4))
                
                #---avoiding excessive write to LEDs                
                dst_next = rectify(distance, distanceTreshold0)                
                if dst_prev != dst_next:
                    grovepi.digitalWrite(Devices['led_red'],dst_next)
                    dst_prev = dst_next                    
                
                lt_next = rectify(light,lightTreshold)
                if lt_prev != lt_next:
                    grovepi.digitalWrite(Devices['led_yellow'],lt_next)
                    lt_prev = lt_next
                    
                # write to CSV                
                t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(starttime))
                print('%s, %dcm, %dlum,%ddB, %3.1f%%, %3.1fC' % (t,distance,light,sound,hum,temp), end='\r')
                
                # message on LCD ?
                if not messageInProgress:
                    if sound > noiseTreshold:     
                        sentence = rd.randint(0,len(sentences_sound)-1)
                        lcd.newMessage(sentences_sound[sentence], colour=[10,200,200])
                    if distance < distanceTreshold0 and distance>0:
                        sentence = rd.randint(0,len(sentences_distance0)-1)
                        lcd.newMessage(sentences_distance0[sentence], colour=[250,50,10]) 
                    if light < lightTreshold:
                        sentence = rd.randint(0,len(sentences_light)-1)
                        lcd.newMessage(sentences_light[sentence], colour=[200,200,10])                          
                
                if len(lcd.pendingMessages) > 0: 
                    if not messageInProgress:
                        lcdMessage_starttime = time.time()
                        lcd.displayMessage() 
                        messageInProgress = True
                        
                if messageInProgress:
                    if lcdMessage_frametime >= messageDuration:
                        lcd.endDisplayMessage()     
                        messageInProgress = False
                    
                if lcdMain_frametime >= lcdMain_spf:
                    if not messageInProgress:
                        lcdMain_starttime = time.time() 
                        stringForLCD = 'lumi temp  humid%4d%5.1fC%5.1f%%' % (light, temp, hum)
                        lcd.updateTextVar(stringForLCD)
                        lcd.updateText()
        
                computationalSpeed.append(time.time()-starttime)
#             else:
#                 if grovepi.analogRead(Devices['sound_sensor']) > noiseTreshold:     
#                     sentence = rd.randint(0,len(sentences_sound)-1)
#                     lcd.newMessage(sentences_sound[sentence], colour=[10,200,200])
                
            # FIXED TIME STEP technique
            frametime = time.time() - starttime
            lcdMain_frametime = time.time() - lcdMain_starttime
            lcdMessage_frametime = time.time() - lcdMessage_starttime
    except (KeyboardInterrupt, SystemExit):
        #resetLEDs()            
        lcd.reset()
        aipt = np.mean(computationalSpeed)
        print("\n\naverage iteration processing time: %5.10f ms" % aipt)
        print("maximum fps possible: %5.10f ms" % (1/aipt))
        if fps > 1/aipt:
            print("warning: frame skipping")
#         break
            
mainEvent(1)
