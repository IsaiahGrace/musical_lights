#! /usr/bin/env python

import dbus
import signal
import sys
import os
from time import sleep, time
import json
from random import random
import spotipy
import spotipy.util as util
import spotipy.oauth2
from spotipy import SpotifyException
from termcolor import colored
from pprint import pprint as pp

USERNAME = 'Isaiah Robert Grace'
USER_ID = '12149734788' # Isaiah Robert Grace
CLIENT_ID = '9b6ff36aec5442088e9043520640f941'
CLIENT_SECRET = 'e5baf7417df54c979cb2be7e67a337f2'
REDIRECT_URI = 'http://localhost:8080'
PORT_NUMBER = 8080
SCOPE = 'user-read-currently-playing'
CACHE = '.spotipyoauthcache'
PI_NAME = 'beacon'
PI_PATH = "/home/pi/lightRemote/pi/from_old_pi/lights/"


readingMode = False
readingModeTimer = 0

# This mode determines weather to send simple or complex data to the Pi, for either C or Python clients
CMODE = False

# This flag is set when we are trying to shut down the lights, and will limit the number of times that we try to ping the pi
SHUTDOWN = False

def handler_stop_signals(signum, frame):
    global readingMode
    readingMode = False
        
    global SHUTDOWN
    SHUTDOWN = True
    
    turn_off_lights()
    print(colored('\nSIGINT or SIGTERM, lights turning off','red'))
    sys.exit(0)
    
signal.signal(signal.SIGINT, handler_stop_signals)
signal.signal(signal.SIGTERM, handler_stop_signals)

def turn_off_lights():
    audio_features = dict()
    audio_features['is_playing'] = False
    send_data_to_pi(audio_features)

def sleepReading(seconds):
    global readingModeTimer
    global readingMode

    #print(str(readingModeTimer) +  ' : ' + str(time()) + '\n')
    if readingModeTimer != 0 and readingModeTimer < time():
        print("readingMode disabled!\n")
        readingModeTimer = 0
        readingMode = False
        turn_off_lights()

    sleep(seconds)
        
    
def send_data_to_pi(audio_features):

    # Add the readingMode attribute to the dict we are about to send to the pi weather or not it is true.
    global readingMode
    #print("readingMode: " + str(readingMode) + "\n")
    audio_features['readingMode'] = readingMode
    
    if(CMODE):
        send_simple_data_to_pi(audio_features)
    else:
        send_complex_data_to_pi(audio_features)


def send_complex_data_to_pi(audio_features):
    #pp(audio_features)
    f = open('current_song', 'w')
    f.write(json.dumps(audio_features))
    f.close()
    
    if os.system("ping -q -c 1 -W 1 " + PI_NAME + " > /dev/null") == 0:
        os.system('scp -q current_song pi@' + PI_NAME + ':' + PI_PATH + 'current_song')
    
def send_simple_data_to_pi(audio_features):
    if(audio_features['is_playing']):
        valence = int(audio_features['valence'] * 255)
    else:
        valence = -1
    f = open('valence_data','w')
    f.write(str(valence) + '\n')
    f.close()

    if os.system("ping -q -c 1 -W 1 " + PI_NAME + " > /dev/null") == 0:
        os.system("scp -q valence_data pi@" + PI_NAME + ':' + PI_PATH + 'valence_data')
        
        
def send_music_to_pi(mediaPlayer):
    # wait unitl the Pi is online. No point doing anything else if it wont hear us
    count = 0
    while os.system("ping -q -c 1 -W 1 " + PI_NAME + " > /dev/null") != 0:
        message = 'Pi is not responding'
        if count > 0:
            message = '\r' + message + ' (' + str(count) + ')'
        print(colored(message, 'red'),end='')
        count = count + 1
        
        # Time to sleep before checking if the Pi is back online 
        sleepReading(1)
    
    # Check if any music is playing
    if not mediaPlayer.isPlaying():
        turn_off_lights()
        
        # This loop will capture the program until the mediaPlayer starts playing again
        count = 0
        try:
            while not mediaPlayer.isPlaying():
                message = 'Spotify is paused'
                if count > 0:
                    message = '\r' + message + ' (' + str(count) + ')' 
                print(colored(message, 'red'),end='')
                count = count + 1
                
                # Time to sleep before checking again if spotify is playing music
                sleepReading(1)
                
        except dbus.exceptions.DBusException:
            return

    # Refresh the token if needed.
    # This will not call the spotify API unless the token in cache is expired
    token = util.prompt_for_user_token(username=USERNAME,
                                       scope=SCOPE,
                                       client_id=CLIENT_ID,
                                       client_secret=CLIENT_SECRET,
                                       redirect_uri=REDIRECT_URI)

    # construct the Spotipy API object
    sp = spotipy.Spotify(auth=token)

    # Get currently playing song from spotify
    try:
        results = sp.current_user_playing_track()
    except:
        raise

    
    # Print the name and artist of the song
    try:
        print('\r\n' + results['item']['name'], "--", results['item']['artists'][0]['name'])
    except:
        # This means that I somehow got a Dict with NoneType...
        raise

    # Get Audio Features Dict
    song_id = results['item']['uri']
    try:
        audio_features = sp.audio_features([song_id])[0]
    except:
        raise

    if audio_features == None:
        print(colored("Error: unable to find audio features. Using random color instead",'red'))
        audio_features = dict()
        audio_features['valence'] = random()
        
    # Add some more info to the dict to help out the Pi
    audio_features['name']       = results['item']['name']
    audio_features['artist']     = results['item']['artists'][0]['name']
    audio_features['is_playing'] = results['is_playing']
        
    # Send the data to the Pi to tell the lights to change color
    send_data_to_pi(audio_features)
        
    # Wait until a new track is started OR media is paused OR Pi turns off, then return
    count = 0
    try:
        while mediaPlayer.song_name() == audio_features['name'] and mediaPlayer.isPlaying():
            message = 'Track is playing'
            if count > 0:
                message = '\r' + message + ' (' + str(count) + ')'
            
            print(colored(message,'green'), end='')
            count = count + 1
            
            if os.system("ping -q -c 1 -W 1 " + PI_NAME + " > /dev/null") != 0:
                # The Pi is not listening to us, so it's useless to wait.
                return
            
            # Time to wait before checking if a new song has started or playback is paused
            sleepReading(1)
            
    except dbus.exceptions.DBusException:
        # This exception means that spotify has closed.
        return


    
class MediaPlayer:
    # gist.github.com/FergusInLondon
    # MediaPlayer class from FergusInLondon, with modifications
    # Recieves state from a MediaPlayer using dbus.
    player_properties = False

    
    def __init__(self, player_name):
        # Get an instance of the dbus session bus, and retrieve
        #  a proxy object for accessing the MediaPlayer
        #print('about to get session_bus')
        session_bus = dbus.SessionBus()
        #print('about to get player_proxy')
        player_proxy = session_bus.get_object(
            'org.mpris.MediaPlayer2.%s' % player_name,
            '/org/mpris/MediaPlayer2')
        
        
        # Apply the interface 'org.freedesktop.DBus.Properties to
        #  the player proxy, allowing us to call .Get() and .GetAll()
        #print('about to get player_properties')
        self.player_properties = dbus.Interface(player_proxy, 'org.freedesktop.DBus.Properties')
    
    
    # Retrieve the properties from the Player interface, return a song string.
    def song_string(self):
        #print(about to get props')
        props = self.player_properties.GetAll('org.mpris.MediaPlayer2.Player')
        return "%s, %s, %s" % (props["Metadata"]["xesam:artist"][0],
                               props["Metadata"]["xesam:title"],
                               props["Metadata"]["xesam:album"])
    
    
    def song_name(self):
        # Written by Isaiah
        props = self.player_properties.GetAll('org.mpris.MediaPlayer2.Player')
        return "%s" % (props["Metadata"]["xesam:title"])
        
        
    def isPlaying(self):
        # Written by Isaiah
        props = self.player_properties.GetAll('org.mpris.MediaPlayer2.Player')
        if props['PlaybackStatus'] == 'Playing':
            return True
        else:
            return False
    
    
    
if __name__ == "__main__":
    count = 0
    if len(sys.argv) > 1:
        if sys.argv[1] == '-q':
            sys.stdout = open(os.devnull, 'w')
        if sys.argv[1] == '-l':
            sys.stdout = open('log-music.txt','w')
        if sys.argv[1] == '-r':
            readingMode = True
            if len(sys.argv) == 3:
                readingModeTimer = time() + int(sys.argv[2]) * 60

            
    while(True):
        try:
            player = MediaPlayer('spotify')
        except dbus.exceptions.DBusException:
            player = None
                
        if player != None:
            # Spotify is open! Let's try to send music data to the Pi
            count = 0
            try:
                send_music_to_pi(player)
            except SystemExit:
                raise
            else:
                pass
                
        else:
            # Spotify is closed. Wait for it to reopen
            message = 'Spotify is closed'
            
            if count == 0:
                # On the first time that we detect spotify is closed,
                # send a message to the Pi to turn off the lights
                turn_off_lights()
            else:
                message = '\r' + message + ' (' + str(count) + ')'
                
            count = count + 1
            print(colored(message,'red'),end='')
            
            # Time to sleep before checking again if spotify has been opened
            sleepReading(1)

