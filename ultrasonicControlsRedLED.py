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

def ultrasonicControlsRedLED(fps=24.0, distanceTreshold0=25):    
    frametime = fps
    
    dst_prev, dst_next = 0, 0
    
    while True:
        try:
            if frametime >= 1/fps:
                starttime = time.time()  
                distance = grovepi.ultrasonicRead(Devices['ultrasonic_ranger'])
                
                if distance < distanceTreshold0:
                    dst_next = 255
                else:   
                    dst_next = 0
                    
                if dst_prev != dst_next:
                    grovepi.analogWrite(Devices['led_red'],dst_next)
                    dst_prev = dst_next
                print('%s, %5dcm' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(starttime)),distance), end='\r', flush=True)

            # FIXED TIME STEP technique
            frametime = time.time() - starttime

        except (KeyboardInterrupt, SystemExit):
            grovepi.analogWrite(Devices['led_green'],0)     
            break
            
print()
ultrasonicControlsRedLED()