#! /usr/bin/env python

import time
from rpi_ws281x import *

# LED strip configuration:
LED_COUNT      = 150     # Number of LED pixels. 36 on bottom, 38, on side, 150 total
LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 0       # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

def wakeup(strip):
    try:
        color = Color(255,167, 87)
        # slowly turn on lights over 15 min period
        startTime = time.time() # The time, in seconds that the script was initiatied
        brightness = 0
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, color)
            
        # to spread 255 over 15 minutes, increase brightness by 17 every mintue
        print("Start Wakeup @ " + time.ctime())
        while brightness < 254:
            brightness += 1
            strip.setBrightness(brightness)
            strip.show()
            #print(brightness)
            time.sleep(4)
            
        # hold at max brightness for 30 min
        print("Max brightness @ " + time.ctime())
        strip.setBrightness(255)
        while time.time() - startTime < 2700:
            strip.show()
            time.sleep(60)

        print("Shutdown @ " + time.ctime())
        print("--------------------")
        # turn off lights and return
        for i in range(strip.numPixels()):
            strip.setPixelColorRGB(i, 0,0,0)
        strip.setBrightness(0)
        strip.show()

    except KeyboardInterrupt:
        for i in range(strip.numPixels()):
            strip.setPixelColorRGB(i,0,0,0)
        strip.show()
    
        

if __name__ == '__main__':
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()
    wakeup(strip)
    
