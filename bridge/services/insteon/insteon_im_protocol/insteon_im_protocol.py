#you can only know how many bytes to read after you read a byte
#from the device, so here is a dict that tells you how much you
# need to read

modemCommands = { b'\x60': 7,  # Get IM Info
                    b'\x61': 4, # Send All Link Command
                    b'\x62': 7, # Send Standard or Extended Message
                    b'\x63': 3, # Send X10
                    b'\x64': 3, # Start All Linking
                    b'\x65': 1, # Cancel All Linking
                    b'\x69': 1, # Get First All Link Record
                    b'\x6A': 1, # Get Next All Link Record
                    b'\x50': 9, # Received Standard Message
                    b'\x51': 23, # Received Extended Message
                    b'\x52': 3, # Received X10
                    b'\x56': 4, # All Link Record Response
                    b'\x57': 8, # All Link Record Response
                    b'\x58': 1, # All Link Record Response
                    }

def get_response_length(byte):
    return modemCommands[byte]
