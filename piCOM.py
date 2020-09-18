import sys
import os
import json
from termcolor import colored

# This class uses a variety of methods to communicate with the Pi that is controlling the LEDs
class PiCOM:   
    def __init__(self):
        self.PI_USERNAME = 'pi'
        self.PI_HOSTNAME = '10.0.0.30' # 'beacon' # The hard coded IP address is for the "Error 404" network in CT
        self.PI_PATH = "/home/pi/lightRemote/pi/signals/"
        self.messages = []

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
            #print(colored('Sent "' + signal + '" signal to Pi','yellow'))
            self.messages.append('Sent "' + signal + '" signal to Pi')
            return True
        else:
            #print(colored('Failed to send "' + signal + '" signal to Pi','red'))
            self.messages.append('Failed to send "' + signal + '" signal to Pi')
            return False

    def collect_messages(self):
        return self.messages

