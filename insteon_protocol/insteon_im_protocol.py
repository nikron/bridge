import logging
import bitstring

#you can only know how many bytes to read after you read a byte
#from the device, so here is a dict that tells you how much you
# need to read

modemCommands = { 
                    b'\x50': 9, # Received Standard Message
                    b'\x51': 23, # Received Extended Message
                    b'\x52': 2, # Received X10
                    b'\x53': 8, # All Link Complete
                    b'\x54': 1, # SET button action
                    b'\x55': 0, # SET reset
                    b'\x56': 5, # All Link Record Response
                    b'\x57': 8, # All Link Record Response
                    b'\x58': 1, # All Link Record Response

                    b'\x60': 7, # Get IM Info
                    b'\x61': 4, # Send All Link Command
                    b'\x62': 6, # Send Standard or Extended Message
                    b'\x63': 3, # Send X10
                    b'\x64': 3, # Start All Linking
                    b'\x65': 1, # Cancel All Linking
                    b'\x66': 4, # Set Host device category
                    b'\x67': 1, # Reset the IM
                    b'\x68': 2, # Set INSTEON Ack byte
                    b'\x69': 1, # Get First All Link Record
                    b'\x6A': 1, # Get Next All Link Record
                    b'\x6B': 2, # Set IM Configuration
                    b'\x6C': 1, # Get ALL-link for sender
                    b'\x6D': 2, # LED on
                    b'\x6E': 2, # LED off
                    b'\x6F': 10, # Manage ALL-link record

                    b'\x70': 2, # Set INSTEN NAK Message Byte
                    b'\x71': 3, # Set INSTEN NAK Two Message Byte
                    b'\x72': 1, # RF Sleep
                    b'\x73': 4, # Get IM Configuration
                    }


#function to read the command bytes from an im
#im has to support .read(num)
def read_command(im):
    buf = None

    rsp = self.im_ser.read(1)
    if rsp == b'\x02':
            
        im_cmd = self.im_ser.read(1)
        if im_cmd == b'\x62': #62 can be either 6 or 20 bytes left to read
            control = self.im_ser.read(4) #control bytes of insteon messages
            bs = bitstring.BitString(control[3])

            if bs[7] == True:
                left = self.im_ser.read(16) #16 bytes left for ed insteon
                buf = im_cmd + control + left
            else:
                left = self.im_ser.read(2) #two bytes left for a sd insteon    
                buf = im_cmd + control + left
            else: 
                to_read = modemCommands[b]
                buf = self.im_ser.read(to_read)
                buf = im_cmd + buf
    else:
        logging.error("Didn't get a start of text for first byte, communications messed up.")

    return buf

def decode(buf):
    
    
    
    return None
