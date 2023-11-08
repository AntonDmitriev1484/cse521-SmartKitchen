from bleuio_lib.bleuio_funcs import BleuIO
from bleuio_lib.exceptions import *
import time
import serial

''' PyPip Docs: https://pypi.org/project/bleuio/#description
    Check README and requirements.txt for necessary dependencies
'''

class Scanner:

    def __init__(self, port):
       
        self.ser = serial.Serial(
            port=port,
            baudrate=115200,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1  # Adjust timeout as needed
        )

        self.ser_write('ATI')
        time.sleep(2)

        # line = self.ser.read(1000).decode('utf-8').strip()
        # print(line)
        self.ser_read(2) # Ok it genuinely seems like nothing is being written to serial
        
        # self.ser_write('AT+CENTRAL')
        # lines = self.ser.readlines()


    def scan(self):
        while True:
            time.sleep(2)
            print("Scanning")
            self.ser_write('AT+GAPSCAN\n')
            self.ser_read(1)
            

    # Write a string to serial
    def ser_write(self, command):
        # Ensure the command is encoded as bytes before sending
        command_bytes = command.encode('utf-8')
        self.ser.write(command_bytes)
    
    # Read strings off of serial for 'timer' number of seconds
    def ser_read(self, timer):
        while True:
            line = self.ser.readline().decode('utf-8').strip()
            print(line)
        # # Get the start time
        # start_time = time.time()
        # # Loop for the specified duration
        # while time.time() - start_time < timer:
        #     print("in")
        #     # Read line of text from serial port
            # lines = self.ser.readlines()
            # # Print the received text
            # for line in lines:
            #     print("Received:" + line.decode('utf-8').strip())
            
            

