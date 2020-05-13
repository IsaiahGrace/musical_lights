#! /usr/bin/env python

# Isaiah Grace
# May 11 2020

# This is an attempt to re-write the send_music_to_pi script with a sane ammount of bodging

import signal # Used to respond to Ctrl+C events
import sys
#import os
import time
import json # Used to convert Dict to Str so we can send a text file to the pi
from termcolor import colored
from pprint import pprint as pp

import piCOM
import songData
import dbusManager

PI_NAME = 'beacon'
PI_PATH = "/home/pi/lightRemote/pi/from_old_pi/lights/"

class AbstractFSM():  
    def step(self):
        print(colored(self.get_name() + ": " + self.get_state(),'green'))
        self.state()

    def get_state(self):
        return self.state.__name__

    def get_name(self):
        return self.__class__.__name__

    def IDLE(self):
        raise Error("IDLE() is abstract, you must overwrite it if inheriting from abstractFSM")

    def SHUTDOWN(self):
        raise Error("SHUTDOWN() is abstract, you must overwrite it if inheriting from abstractFSM")

    
class MusicFSM(AbstractFSM):
    def __init__(self):
        self.state = self.IDLE
        self.musicDbusManager = dbusManager.DbusManager()
        self.musicPiCOM = piCOM.PiCOM()
        self.musicSongData = songData.SongData()
        self.song_id = None
        
    def IDLE(self):
        # Only leave IDLE state if spotify is open and we can contact the Pi
        if self.musicDbusManager.connect_to_spotify() and self.musicPiCOM.ping():
            self.state = self.SPOTIFY_PAUSED
        else:
            self.state = self.IDLE

    def SPOTIFY_PAUSED(self):
        if not self.musicDbusManager.isOpen():
            self.state = self.SHUTDOWN
        elif self.musicDbusManager.isPlaying():
            self.state = self.NEW_SONG
        else:
            self.state = self.SPOTIFY_PAUSED

    def NEW_SONG(self):
        # get song data
        self.musicSongData.set_playing_track()
        self.musicSongData.set_audio_features()
        
        # package up data for the pi
        message = json.dumps(self.musicSongData.get_audio_features())
        signal = "audio_features"
        
        # send the data to the pi
        self.musicPiCOM.sendSignal(signal, message)

        self.song_id = self.musicSongData.song_id()
        self.state = self.SPOTIFY_PLAYING
    
    def SPOTIFY_PLAYING(self):
        if not self.musicDbusManager.isPlaying():
            self.state = self.SHUTDOWN
        elif self.song_id != self.musicSongData.song_id():
            self.state = self.NEW_SONG
        else:
            self.state = self.SPOTIFY_PLAYING

    def SHUTDOWN(self):
        message = dict()
        message['is_playing'] = False
        signal = "audio_features"
        self.musicPiCOM.sendSignal(signal, message)
        self.state = self.IDLE

    
class ReadingFSM(AbstractFSM):
    def __init__(self):
        self.state = self.IDLE
        self.readingPiCOM = piCOM.PiCOM()
        self.timeout = 0
        
    def IDLE(self):
        self.state = self.IDLE
        # We've got to figure out how to initiate reading mode..

    def START_READING(self):
        message = dict()
        message['reading'] = True
        signal = 'reading'
        self.readingPiCOM.sendSignal(signal, message)
        self.state = self.READING
    
    def READING(self):
        # TODO: decriment timeout, maybe with time.time?
        if timeout == 0:
            self.state = self.SHUTDOWN
        else:
            self.state = self.READING

    def SHUTDOWN(self):
        message = dict()
        message['reading'] = False
        signal = 'reading'
        self.readingPiCOM.sendSignal(signal, message)
        self.state = self.IDLE


class FanFSM(AbstractFSM):
    def __init__(self):
        self.state = self.IDLE
        self.fanPiCOM = piCOM.PiCOM()

        # TODO: setup monitoring functions (callbacks? interrupts?) to signal a notification
        self.notification = None

        # TODO: setup a system to turn on music mode
        self.musicMode = False

        # TODO: setup a system to turn on FX mode
        self.fxMode = False
        self.fxNum = 0

        # TODO: setup a system to turn off the fan lights
        self.shutdown = False
        
    def IDLE(self):
        if self.notification != None:
            self.state = self.NOTIFY
        elif self.musicMode:
            self.state = self.MUSIC
        elif self.fxMode:
            self.state = self.FX
        elif self.shutdown:
            self.state = self.SHUTDOWN
        else:
            self.state = self.IDLE
            
    def MUSIC(self):
        message = dict()
        message['fan_on'] = True
        message['mode'] = 'MUSIC'
        signal = 'fan'
        self.fanPiCOM.sendSignal(signal, message)
        self.musicMode = False
        self.state = self.IDLE
    
    def FX(self):
        message = dict()
        message['fan_on'] = True
        message['mode'] = 'FX'
        message['FX'] = fxNum
        signal = 'fan'
        self.fanPiCOM.sendSignal(signal, message)
        self.fxMode = False
        self.state = self.IDLE


    def NOTIFY(self):
        message = dict()
        message['fan_on'] = True
        message['mode'] = 'FX'
        signal = 'fan'
        self.fanPiCOM.sendSignal(signal, message)
        self.state = self.IDLE
        pass
    
    def SHUTDOWN(self):
        message = dict()
        message['fan_on'] = False
        signal = 'fan'
        self.fanPiCOM.sendSignal(signal, message)
        self.state = self.IDLE
        

# This class is the top level controller for our FSMs that will coordinate the efforts of the other classes
class ControlFSM:
    def __init__(self):
        self.FSMs = [MusicFSM(), ReadingFSM(), FanFSM()] #, fanFSM()] # maybe add another fanFSM to have seperate fan control?
        signal.signal(signal.SIGINT, self.SHUTDOWN)
        signal.signal(signal.SIGTERM, self.SHUTDOWN)

    def step(self):
        for FSM in self.FSMs:
            # Evaluate the FSM as many times as necessary so that a state repeats
            old_state = None
            while(FSM.get_state() != old_state):
                old_state = FSM.get_state()
                FSM.step()
                # That means that each element in the iterable FSMs must be a class with the step() function defined

    def SHUTDOWN(self, signum, frame):
        # shutdown all the lights
        print(colored('SHUTDOWN! lights turning off','red'))
        for FSM in self.FSMs:
            FSM.SHUTDOWN()

        sys.exit(0)
    

if __name__ == '__main__':
    controlFSM = ControlFSM()
    #while(True):
    for i in range(10):
        controlFSM.step()
        time.sleep(1)

    controlFSM.SHUTDOWN(None, None)
