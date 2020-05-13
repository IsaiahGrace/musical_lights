import sys
import os
import json
from termcolor import colored

# This class uses a variety of methods to communicate with the Pi that is controlling the LEDs
class PiCOM:   
    def __init__(self):
        self.PI_USERNAME = 'pi'
        self.PI_HOSTNAME = 'beacon'
        self.PI_PATH = "/home/pi/lightRemote/pi/signals/"

    def ping(self):
        if os.system("ping -c 1 -W 1 " + self.PI_HOSTNAME + " > /dev/null") == 0: # add -q to quiet
            return True
        else:
            return False

    def sendSignal(self, signal, message):
        if isinstance(message, dict):
            message = json.dumps(message)
            
        with open('./signals/' + signal,'w') as f:
            f.write(message)

        if self.ping() and os.system("scp -q ./signals/" + signal + " " + self.PI_USERNAME + "@" + self.PI_HOSTNAME + ':' + self.PI_PATH + signal) == 0:
            print(colored('Sent "' + signal + '" signal to Pi','yellow'))
            return True
        else:
            print(colored('Failed to send "' + signal + '" signal to Pi','red'))
            return False

