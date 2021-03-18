import sys
import os
import json

# This class uses a variety of methods to communicate with the Pi that is controlling the LEDs
class PiCOM:   
    def __init__(self):
        self.PI_USERNAME = 'pi'
        # '10.0.0.30' The hard coded IP address is for the "Error 404" network in CT
        self.PI_HOSTNAME = 'music-pi.local'
        self.PI_PATH = "/home/pi/lightRemote/pi/signals/"
        self.messages = []
        self.active = False

    def ping(self):
        if os.system("ping -q -c 1 -W 1 " + self.PI_HOSTNAME + " > /dev/null") == 0: # add -q to quiet
            self.active = True
            return True
        else:
            self.active = False
            return False
        

    def sendSignal(self, signal, message):
        if isinstance(message, dict):
            message = json.dumps(message)
            
        with open('./signals/' + signal,'w') as f:
            f.write(message)

        if not self.ping():
            return False
        
        if os.system("scp -q ./signals/" + signal + " " + self.PI_USERNAME + "@" + self.PI_HOSTNAME + ':' + self.PI_PATH + signal) == 0:
            self.messages.append('Sent "' + signal + '" signal to Pi')
            return True
        else:
            self.messages.append('Failed to send "' + signal + '" signal to Pi')
            return False

    def collect_messages(self):
        messages = self.messages
        self.messages = []
        return messages

    def isActive(self):
        return self.active
