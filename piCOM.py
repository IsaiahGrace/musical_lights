import sys

# This class uses a variety of methods to communicate with the Pi that is controlling the LEDs
class piCOM:
    PI_USERNAME = 'pi'
    PI_HOSTNAME = 'beacon'
    PI_PATH = "/home/pi/lightRemote/pi/signals/"
    
    def __init__(self):
        pass

    def ping(self):
        if os.system("ping -q -c 1 -W 1 " + PI_NAME + " > /dev/null") == 0:
            return True
        else:
            return False

    def sendSignal(self, signal, message):
        with open('./signals/' + signal,'w') as f:
            f.write(message)

        if ping() and os.system("scp -q ./signals/" + signal + " " + PI_USERNAME + "@" + PI_HOSTNAME + ':' + PI_PATH + signal) == 0:
            return True
        else:
            return False

