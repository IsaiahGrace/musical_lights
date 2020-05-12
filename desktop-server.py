#! /usr/bin/env python

# Isaiah Grace
# May 11 2020

# This is an attempt to re-write the send_music_to_pi script with a sane ammount of bodging

import dbus # Used to communicate with spotify desktop client
import signal # Used to respond to Ctrl+C events
import sys
import os
from time import sleep, time
import json # Used to convert Dict to Str so we can send a text file to the pi
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

# This class is the top level FSM that will coordinate the efforts of the other classes
class controlFSM:
    def __init__(self):
        pass

# This class uses the dbus to interact with the open spotipy desktop client
class dbusManager:
    pass

# This class uses a variety of methods to communicate with the Pi that is controlling the LEDs
class piCOM:
    pass

#
