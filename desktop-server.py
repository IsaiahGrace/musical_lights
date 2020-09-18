#! /usr/bin/env python

# Isaiah Grace
# May 11 2020

# This is an attempt to re-write the send_music_to_pi script with a sane ammount of bodging

import curses
import signal # Used to respond to Ctrl+C events
import sys
import time
import json # Used to convert Dict to Str so we can send a text file to the pi
from termcolor import colored
#from pprint import pprint as pp

import piCOM
import songData
import dbusManager

class AbstractFSM():
    messages = []
    
    def step(self):
        #print(colored(self.get_name() + ": " + self.get_state(),'green'))
        self.state()

    def get_state(self):
        return self.state.__name__

    def get_name(self):
        return self.__class__.__name__

    def collect_messages(self):
        collection = '\n'.join(self.messages)
        self.messages = []
        return collection

    def IDLE(self):
        raise Error("IDLE() is abstract, you must overwrite it if inheriting from AbstractFSM")

    def SHUTDOWN(self):
        raise Error("SHUTDOWN() is abstract, you must overwrite it if inheriting from AbstractFSM")

    
class MusicFSM(AbstractFSM):
    def __init__(self):
        self.state = self.IDLE
        self.prints = []
        self.dbusManager = dbusManager.DbusManager()
        self.piCOM = piCOM.PiCOM()
        self.songData = songData.SongData()
        self.song_id = None
        
    def IDLE(self):
        # Only leave IDLE state if spotify is open and we can contact the Pi
        if self.dbusManager.connect_to_spotify() and self.piCOM.ping():
            self.state = self.SPOTIFY_PAUSED
        else:
            self.state = self.IDLE
        self.messages.extend(self.piCOM.collect_messages())
        

    def SPOTIFY_PAUSED(self):
        if not self.dbusManager.isOpen():
            self.state = self.SHUTDOWN
        elif self.dbusManager.isPlaying():
            self.state = self.NEW_SONG
        else:
            self.state = self.SPOTIFY_PAUSED
        

    def NEW_SONG(self):
        # get song data
        self.songData.init_sp()
        
        self.songData.set_playing_track()
        self.songData.set_audio_features()
        
        # package up data for the pi
        message = json.dumps(self.songData.get_audio_features())
        signal = "music"
        
        # send the data to the pi
        self.piCOM.sendSignal(signal, message)
        #self.musicPiCOM.sendSignal("audio_features", message)

        self.song_info = self.dbusManager.get_song_info()
        self.state = self.SPOTIFY_PLAYING
        self.messages.extend(self.songData.collect_messages())
        self.messages.extend(self.piCOM.collect_messages())

        
    def SPOTIFY_PLAYING(self):
        if not self.dbusManager.isPlaying():
            self.state = self.SHUTDOWN
        elif self.song_info != self.dbusManager.get_song_info():
            self.state = self.NEW_SONG
        else:
            self.state = self.SPOTIFY_PLAYING

    def SHUTDOWN(self):
        message = {'is_playing' : False}
        signal = "music"
        self.piCOM.sendSignal(signal, message)
        self.piCOM.sendSignal("audio_features", message)
        self.state = self.IDLE
        self.messages.extend(self.piCOM.collect_messages())
    
class ReadingFSM(AbstractFSM):
    def __init__(self):
        self.state = self.IDLE
        self.piCOM = piCOM.PiCOM()
        self.timeout = 0
        
    def IDLE(self):
        self.state = self.IDLE
        # We've got to figure out how to initiate reading mode..

    def START_READING(self):
        message = dict()
        message['reading'] = True
        signal = 'reading'
        self.piCOM.sendSignal(signal, message)
        self.state = self.READING
        self.messages.extend(self.piCOM.collect_messages())
    
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
        self.piCOM.sendSignal(signal, message)
        self.state = self.IDLE
        self.messages.extend(self.piCOM.collect_messages())


class FanFSM(AbstractFSM):
    def __init__(self):
        self.state = self.MUSIC
        self.piCOM = piCOM.PiCOM()

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
        self.piCOM.sendSignal(signal, message)
        self.musicMode = False
        self.state = self.IDLE
        self.messages.extend(self.piCOM.collect_messages())

    
    def FX(self):
        message = dict()
        message['fan_on'] = True
        message['mode'] = 'FX'
        message['FX'] = fxNum
        signal = 'fan'
        self.piCOM.sendSignal(signal, message)
        self.fxMode = False
        self.state = self.IDLE
        self.messages.extend(self.piCOM.collect_messages())


    def NOTIFY(self):
        message = dict()
        message['fan_on'] = True
        message['mode'] = 'NOTIFY'
        signal = 'fan'
        self.piCOM.sendSignal(signal, message)
        self.state = self.IDLE
        self.messages.extend(self.piCOM.collect_messages())
    
    def SHUTDOWN(self):
        message = dict()
        message['fan_on'] = False
        signal = 'fan'
        self.piCOM.sendSignal(signal, message)
        self.state = self.IDLE
        self.messages.extend(self.piCOM.collect_messages())
        

# This class is the top level controller for our FSMs that will coordinate the efforts of the other classes
class ControlFSM:
    def __init__(self):
        signal.signal(signal.SIGINT, self.SHUTDOWN)
        signal.signal(signal.SIGTERM, self.SHUTDOWN)

    
    def start(self):
        curses.wrapper(self._start)
        
        
    def _start(self, stdscr):
        self.stdscr = stdscr
        self.statesWin = curses.newwin(4, curses.COLS - 1, 3, 0)
        self.msgWin = curses.newwin(20, curses.COLS - 1, 9, 0)
        self.stdscr.addstr(0, (curses.COLS // 2) - 7, 'Musical Lights', curses.A_STANDOUT)
        self.FSMs = [MusicFSM(), FanFSM(), ReadingFSM()] # ommited ReadingFSM

        
        # Write the FSM titles
        for idx, FSM in enumerate(self.FSMs):
            x = 1 + (idx * ((curses.COLS - 3) // len(self.FSMs)))
            self.statesWin.addstr(1, x, FSM.get_name())

        # Wite the MSG title
        self.msgWin.addstr(1, 1, 'Messages', curses.A_STANDOUT)

        # Draw borders on the windows
        self.statesWin.border()
        self.msgWin.border()

        self.statesWin.noutrefresh()
        self.msgWin.noutrefresh()
        curses.doupdate()
        
        while(True):
            self.printStates()
            self.printMessages()
            self.msgWin.noutrefresh()
            self.statesWin.noutrefresh()
            curses.doupdate()
            time.sleep(1)
            self.step()

            
    def printStates(self):
        for idx, FSM in enumerate(self.FSMs):
            x = 1 + (idx * ((curses.COLS - 3) // len(self.FSMs)))
            self.statesWin.addstr(2, x, FSM.get_state())


    def printMessages(self):
        #self.msgWin.clear()
        #self.msgWin.border()
        for idx, FSM in enumerate(self.FSMs):
            x = 1 + (idx * ((curses.COLS - 3) // len(self.FSMs)))
            self.msgWin.addstr(2, x, FSM.collect_messages())

    
    def step(self):
        for FSM in self.FSMs:
            # Evaluate the FSM as many times as necessary so that a state repeats
            old_state = None
            while((old_state := FSM.get_state()) != old_state):
                FSM.step()
                # This means that each element in the iterable FSMs must be a class with the step() function defined

                
    def SHUTDOWN(self, signum, frame):
        # shutdown all the l.ights
        print(colored('SHUTDOWN! lights turning off','red'))
        self.stdscr.addstr(1,curses.COLS // 2, 'SHUTDOWN')
        self.stdscr.noutrefresh()
        curses.doupdate()
        
        for FSM in self.FSMs:
            FSM.SHUTDOWN()
            self.printMessages()
            self.msgWin.noutrefresh()
            curses.doupdate()

        sys.exit(0)
    

if __name__ == '__main__':
    controlFSM = ControlFSM()
    controlFSM.start()
    
