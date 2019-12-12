#! /usr/bin/env python

from rpi_ws281x import *

# LED strip configuration:
LED_COUNT      = 150     # Number of LED pixels. 36 on bottom, 38, on side, 150 total
LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 0       # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

def clear_lights(strip):
    for i in range(strip.numPixels()):
        strip.setPixelColorRGB(i,0,0,0)
    strip.show()
    

if __name__ == "__main__":
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()
    clear_lights(strip)
