#! /usr/bin/env python

# Isaiah Grace
# May 11 2020

# This is an attempt to re-write the send_music_to_pi script with a sane ammount of bodging

import dbus # Used to communicate with spotify desktop client
import signal # Used to respond to Ctrl+C events
import sys
import os
import time
import json # Used to convert Dict to Str so we can send a text file to the pi
from termcolor import colored
from pprint import pprint as pp

import "piCOM"
import "songData"
import "dbusManager"

PI_NAME = 'beacon'
PI_PATH = "/home/pi/lightRemote/pi/from_old_pi/lights/"

class abstractFSM(): 
    def __init__(self):
        self.state = IDLE
   
    def step(self):
        self.state()

    def get_state(self):
        return self.state.__NAME__

    def IDLE(self):
        raise Error("IDLE() is abstract, you must overwrite it if inheriting from abstractFSM")

    def SHUTDOWN(self):
        raise Error("SHUTDOWN() is abstract, you must overwrite it if inheriting from abstractFSM")

    
class MusicFSM(abstractFSM):
    def IDLE(self):
        # if spotify is open:
        #   self.state = SPOTIFY_OPEN
        pass

    def SPOTIFY_OPEN(self):
        #if song is playing:
        #   self.state = SPOTIFY_PLAYING
        pass

    def NEW_SONG(self):
        # get song data
        # package up data for the pi
        # send the data to the pi
        # self.state = NEW_SONG
    
    def SPOTIFY_PLAYING(self):
        # get song data
        # compare to current song data
        # if different:
        #     self.state = NEW_SONG
        pass

    def SPOTIFY_PAUSED(self):
        # Checks to see if a song is playing
        pass

    def SHUTDOWN(self):
        pass

    
class ReadingFSM(abstractFSM):
    def IDLE(self):
        pass

    def START_READING(self):
        pass
    
    def READING(self):
        pass

    def SHUTDOWN(self):
        pass

    
class FanFSM(abstractFSM):
    def IDLE(self):
        pass
        
    def MUSIC(self):
        pass
    
    def FX(self):
        pass

    def NOTIFY(self):

    def SHUTDOWN(self):
        pass

    

# This class is the top level FSM that will coordinate the efforts of the other classes
class ControlFSM:
    def __init__(self):
        self.FSMs = [musicFSM(), readingFSM(), fanFSM(), fanFSM()]

    def step(self):
        for FSM in FSMs:
            # Evaluate the FSM as many times as necessary so that a state repeats
            state = None
            while(FSM.get_state() != state):
                FSM.step()
        # That means that each element in the iterable FSMs must be a class with the step() function defined




if __NAME__ == '__MAIN__':
    controlFSM = ControlFSM()

    while(True):
        controlFSM.step()

        time.sleep(1)
    
