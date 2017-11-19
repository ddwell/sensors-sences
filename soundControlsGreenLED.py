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


def soundControlsGreenLED(fps=30.0):    
    frametime = fps
    
    while True:
        try:
            if frametime >= 1/fps:
                starttime = time.time() 
                
                sound = grovepi.analogRead(Devices['sound_sensor'])
                grovepi.analogWrite(Devices['led_green'],int(sound/4))
                print('%s, %5d' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(starttime)),sound), end='\r', flush=True)


            # FIXED TIME STEP technique
            frametime = time.time() - starttime

        except (KeyboardInterrupt, SystemExit):
            grovepi.analogWrite(Devices['led_green'],0)     
            break
            
soundControlsGreenLED()