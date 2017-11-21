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


computationalSpeed = []

def event(fps=1.0, distanceTreshold0=25):    
    frametime = fps
    
    dst_prev, dst_next = 0, 0   
    lt_prev, lt_next = 0, 0
    
    try:
        while True:
            if frametime >= 1/fps:
                starttime = time.time()  
                
                # reading from sensors        
#                 sound = grovepi.analogRead(Devices['sound_sensor'])     
                sound = 0
                light = grovepi.analogRead(Devices['photoresistor'])
                distance = grovepi.ultrasonicRead(Devices['ultrasonic_ranger'])
                [temp, hum] = grovepi.dht(Devices['dht_sensor'], 0)        
#                 gas = grovepi.analogRead(Devices['gas_sensor'])  
                
                #LED reaction
#                 grovepi.analogWrite(Devices['led_green'],int(sound/4))
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
                    
                print('%s, %5dcm, %5dlum, %5d' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(starttime)),distance, light, sound), end='\r')
                
                computationalSpeed.append(time.time()-starttime)
            # FIXED TIME STEP technique
            frametime = time.time() - starttime

    except (KeyboardInterrupt, SystemExit):
        grovepi.analogWrite(Devices['led_green'],0)  
        grovepi.digitalWrite(Devices['led_yellow'],0)
        grovepi.digitalWrite(Devices['led_red'],0)
        aipt = np.mean(computationalSpeed)
        print("\n\naverage iteration processing time: %5.10f ms" % aipt)
        print("maximum fps possible: %5.10f ms" % (1/aipt))
        if fps > 1/aipt:
            print("warning: frame skipping")

event()