# Isaiah Grace

import hid
import random
import math
import colorsys

class PlanckCOM:
    def __init__(self):
        self.VENDOR_ID = 0x3297
        self.PRODUCT_ID = 0xC6CF
        self.INTERFACE_NUM = 1
        self.HID_CODES = {'HID_PING'  : 1,
                          'HID_START' : 2,
                          'HID_COLOR' : 3,
                          'HID_STOP'  : 4
                          }

        self.dev_info = [x for x in hid.enumerate() if x['vendor_id'] == self.VENDOR_ID and x['interface_number'] == self.INTERFACE_NUM][0]
        self.dev = hid.device()
        self.messages = []

    def openPlanck(self):
        if self.dev == None:
            self.__init__()
        try:
            self.dev.open_path(self.dev_info['path'])
        except OSError:
            self.dev = None
            self.messages.append("Failed to open Planck: " + str(self.dev_info['path']))
            return False
        return True
    
    def ping(self):
        if (True):
            self.messages.append("Skipped Planck Ping")
            return True
        
        # This does not have replacement, but I don't care
        packet = random.sample(range(0,255),20) 
        packet[0] = self.HID_CODES['HID_PING']
        recv = None
        
        if self.openPlanck():
            num_sent = self.dev.write(packet)
            recv = self.dev.read(num_sent)
            self.dev.close()
        
        if recv == packet:
            return True
        else:
            self.messages.append("Failed to ping Planck")
            self.messages.append(self.dev_info['path'])
            return False
    

    def sendCode(self, code):
        if code not in self.HID_CODES:
            self.messages.append("ERROR: sendCode was given a code not in the HID_CODES dict")
            return False
        
        # When the packet was only one byte in length, something was not working and the placnk wasn't responding correctly.
        # When the packet is longer, but random, the planck recieves the packet correctly
        packet = random.sample(range(0,255),20)
        packet[0] = self.HID_CODES[code]
        
        if self.openPlanck():
            self.dev.write(packet)
            self.dev.close()
            self.messages.append("Sent " + code + " to Planck")
            return True
        
        return False
        
    def sendColors(self, red, blue, green):
        if self.openPlanck():
            self.dev.open_path(self.dev_info['path'])
            self.dev.write([self.HID_CODES['HID_COLOR'],red, blue, green])
            self.dev.close()
            self.messages.append("Set Planck color: " + str((red,blue,green)))
            return True
        return False
    
    def sendSignal(self, signal, message):
        # at the moment, signal will always be music, so we can ignore it
        if not message['is_playing']:
            self.sendCode('HID_STOP')
            return

        hue = message['valence'] + 0.66 # hue_offset
        if hue > 1:
            hue = hue - 1

        red, blue, green = tuple(int(i * 255) for i in colorsys.hsv_to_rgb(hue,1,1))
        
        self.sendColors(red,blue,green)

        
    def collect_messages(self):
        messages = self.messages
        self.messages = []
        return messages
