#! /usr/bin/env python


# TODO: Make this code object oriented with a lights_service class


from time import time, ctime, sleep
from os.path import getmtime
from json import loads
from colorsys import hsv_to_rgb
from rpi_ws281x import *
from random import randint
import signal
import sys
import os
#from termcolor import colored    

# LED strip configuration:
LED_COUNT      = 150     # Number of LED pixels. 36 on bottom, 38, on side, 150 total
LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53


readingMode = False # Hack for global variable controlling reading mode
readingRed = 240
readingGreen = 254
readingBlue = 184

# These are the attributes we are passed about the track that is currenty playing
# analysis_url:       An HTTP URL to access the full audio analysis of this track.
# id:                 The Spotify ID for the track.
# track_href:         A link to the Web API endpoint providing full details of the track.
# type:               "audio_features"
# uri:                "audio_features"
# duration_ms:        The duration of the track in milliseconds.
# loudness:         -60 - 0 (dB loudness of track)
# tempo:              0 - 200+ (BPM 100-150 typical)
# liveness:           0 - 1 (0.8 likley live performance)
# mode:               0 - 1 (Major: 1 Minor: 0)
# speechiness:        0 - 1
# valence:            0 - 1 ("mood" or "emotion" of the song. 0 more negative, 1 more positive)
# instrumentalness:   0 - 1
# energy:             0 - 1
# danceability:       0 - 1
# acousticness:       0 - 1
# time_signature:     number of beats in each bar
# key:                0 C
#                     1 C#
#                     2 D
#                     3 D#
#                     4 E
#                     5 F
#                     6 F#
#                     7 G
#                     8 G#
#                     9 A
#                    10 A#
#                    11 B

def handler_stop_signals(signum, frame):
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()
    clear_strip(strip)
    sys.exit(0)
    
signal.signal(signal.SIGINT, handler_stop_signals)
signal.signal(signal.SIGTERM, handler_stop_signals)

def hsv2rgb(h,s,v):
    # This function takes h,s,v values from 0 - 1 and converts them to RGB 0 - 255
    return tuple(int(i * 255) for i in hsv_to_rgb(h,s,v))


def clear_strip(strip):
    # Clears the strip (turns off all the LEDs)
    for i in range(strip.numPixels()):
        strip.setPixelColorRGB(i,0,0,0)
    strip.show()


def getColorFromValence(valence):
    # takes a valence value (0 - 1) describing the song
    # and returns a color representing that valence value
    hue = valence + 0.666
    if hue > 1:
        hue = hue - 1

    (red, green, blue) = hsv2rgb(hue,1,1)
    return Color(red,green,blue)

    
def getAudioFeatures(path):
    # reads the data from path and converts the text into a dict
    f = open(path,'r')
    current_song = f.read()
    f.close()
    return loads(current_song)

    
def slowVariations(strip, mutationRate, mutationStep, baseColor, boundSize):
    # Applies slow vatiations to each of the pixels on the strip according to the parameters:
    # mutationRate (0 - 1),
    # mutationStep (0 - 255),
    # baseColor (packed 24 bit color),
    # boundSize (0 - 255)

    global readingMode # Tell python that readingMode is a global variable
    global readingRed, readingGreen, readingBlue # make the colors global too

    # Extract the base R G B values from the packed 24 bit color
    baseRed   = (0xFF0000 & baseColor) >> 16
    baseGreen = (0x00FF00 & baseColor) >> 8
    baseBlue  = (0x0000FF & baseColor)

    for i in range(strip.numPixels()):
        color = strip.getPixelColor(i)

        # Extract the R G B values for this pixel from the packed 24 bit color
        red   = (0xFF0000 & color) >> 16
        green = (0x00FF00 & color) >> 8
        blue  = (0x0000FF & color)    

        # Mutate each of the colors to find a new color value for the pixel
        red   = mutateColor(red,   mutationRate, mutationStep)
        green = mutateColor(green, mutationRate, mutationStep)
        blue  = mutateColor(blue,  mutationRate, mutationStep)

        # Apply the limiting bound on the new pixel color
        red   = applyBound(red,   baseRed, boundSize)
        green = applyBound(green, baseGreen, boundSize)
        blue  = applyBound(blue,  baseBlue, boundSize)

        # Update the color of this pixel
        strip.setPixelColorRGB(i, red, green, blue)

    if readingMode:
        # Reading Mode is enabled: now we override the last lights on the array to a nice warm color
        for i in range(strip.numPixels() - 19, strip.numPixels()):
            strip.setPixelColorRGB(i, readingRed, readingGreen, readingBlue)
                
    # After all the pixels have a new color in the array, push the changes to the actual lights
    strip.show()

    
def applyBound(color, baseColor, boundSize):
    # Applies the bound on a particular color value (0 - 255).
    # If the color is outside the allowed bound, gently push it towards the bound.
    # This allows the lights to turn on/off change colors from song to song gradually
    if color > baseColor + boundSize:
        return color - 1
    if color < baseColor - boundSize:
        return color + 1
    return color


def mutateColor(color, mutationRate, mutationStep):
    # Applies a random mutation to each pixel, allowing a natural variation between pixel colors
    randInt = randint(0,100)
    if randInt < mutationRate * 100:
        # Apply the color mutation, either increase or decrease the color
        if randInt % 2 == 0:
            color = color + mutationStep
        else:
            color = color - mutationStep

        # Make sure the mutated color is within 0 - 255
        if color > 255:
            color = 255
        if color < 0:
            color = 0
            
    return color


def lighting_control_client():
    # The overall control client for the LED lights.
    #print colored('Starting up lighting control client: ' + ctime(), 'blue')
    print 'Starting up lighting control client: ' + ctime()

    # Initilize the PixelStrip
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()

    # Set some starting parameters
    track_file = '/home/pi/Documents/lights/current_song'
    modified_time = time()
    mutationRate = 0 # This is set inside the loop. This is an initial value
    mutationStep = 2 # Tweak this to change how fast the lights mutate
    boundSize = 0 # This is set inside the loop. This is an initial value
    baseColor = 0 # This is set inside the loop. This is an initial value
    tick = time()
    sleep_mode = 0

    global readingMode # Tell python that readingMode is global
    
    try:
        while(True):
            # Check if the track_file has been changed since the last time we looked
            if modified_time != getmtime(track_file):
                
                # Update the modified_time so that we dont keep reading the track_file
                modified_time = getmtime(track_file)

                # Read the audio_features from the track_file
                audio_features = getAudioFeatures(track_file)
                
                readingMode = audio_features['readingMode']

                print("Reading Mode: " + str(readingMode))

                if audio_features['is_playing']:
                    # The track is currently playing and we should update the lights                    
                    #print colored(audio_features['name'] + ' -- ' + audio_features['artist'], 'green')
                    print audio_features['name'] + ' -- ' + audio_features['artist']

                    # Get a new baseColor for the song
                    baseColor = getColorFromValence(audio_features['valence'])

                    # Tweak these to controll the characteristics of the lights
                    boundSize = 50
                    mutationRate = 1
                    
                else:
                    # The track is not currently being played
                    # audio_features likley only has one entry in the dict!
                    # either spotify is closed, or paused
                    baseColor = 0
                    boundSize = 0
                    mutationRate = 0
                    #print colored('No track currently playing','red')
                    print 'No track currently playing'

            if audio_features['is_playing'] or time() - modified_time < 60 or readingMode:
                # The song is playing or has recently stopped.
                # If the song has just stopped, we should still update the lights for one minute
                # This allows the lights to turn off gradually
                sleep_mode = 0
                slowVariations(strip, mutationRate, mutationStep, baseColor, boundSize)
                
            else:
                # The song is not playing and it has been more than one minute.
                # Enter sleep mode so that we are no longer updating the light colors
                # This allows another program to control the lights (wakeup.py)
                message = 'Sleep mode'
                
                if sleep_mode > 0:
                    #message = '\033[F' + message + ' (' + str(sleep_mode) + ')'
                    message = message + ' (' + str(sleep_mode) + ')'
                else:
                    clear_strip(strip)
                    
                #print colored(message, 'red')
                #print message
                
                sleep_mode = sleep_mode + 1

                # Time to sleep before checking if the song is now playing (exit sleep mode)
                sleep(1)
            
            # Experimental rates suggest that everything else in this while loop takes ~0.08s.
            # Adding 0.05 s reduces CPU load and brings an update period for the lights to ~0.13s.
            # It seems that this script takes aproximatly 60% of the CPU time
            # UPDATE: some small library import optomizations may have reduced this to ~56% of CPU time
            sys.stdout.flush()
            sleep(0.05)
        
    except KeyboardInterrupt:
        clear_strip(strip)
        #print colored('\nShutting down lighting control client:' + ctime(), 'blue')
        print 'Shutting down lighting control client:' + ctime()
    
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '-q':
        sys.stdout = open(os.devnull, 'w')

    # This is an attempt to prevent the script from crashing on boot because
    # this script gets started too early in the boot process and the SPI
    # module is not initilized yet! I can't figure out what module the SPI
    # is initilized on. at the moment musical-lights.service is executed after
    # network.target
    #wait(5)    
    lighting_control_client()
