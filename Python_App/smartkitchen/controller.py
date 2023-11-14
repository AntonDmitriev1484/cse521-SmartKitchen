from bleuio_lib.bleuio_funcs import BleuIO
from bleuio_lib.exceptions import *
import time
import serial
import json
import re
import threading

''' PyPip Docs: https://pypi.org/project/bleuio/#description
    Check README and requirements.txt for necessary dependencies
'''

class Scanner:

    def __init__(self, port, ip_to_name, trilateration_table, scanner_id):
       
        self.ser = serial.Serial(
            port=port,
            baudrate=115200,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1  # Adjust timeout as needed
        )

        # Lookup table of BLE beacon to name
        self.ip_to_name = ip_to_name
        self.trilateration_table = trilateration_table # Reference to trilateration table on the main thread
        self.scanner_id = scanner_id # Index at which we will access the RSSI array in trilateration_table
        
        # Maps ADDR -> ( [LAST 10 RAW_RSSI], ROLLING_AVG)
        self.data_table = {} # Each device maintains its own datatable for debugging
                            # All changes made to this datatable will also be applied to trilateration_table
        
        self.ROLL_AVG_SIZE = 10

        self.ser_write('ATI')
        self.ser_write('AT+CENTRAL')
        self.ser_write('ATV1')


    def average(self, array):
        sum = 0
        for el in array:
            sum += el
        return sum / len(array)

    def scan(self):
        while True:
            self.ser_write('AT+GAPSCAN=1')
            self.ser_read(1)

    # Write a string to serial
    def ser_write(self, command):
        # Ensure the command is encoded as bytes before sending
        command += '\r\n'
        command_bytes = command.encode('utf-8')
        self.ser.write(command_bytes)

    def is_gapscan_info(self, line):
        pattern = re.compile(r'\{"S":\s*-?\d+,\s*"rssi":\s*-?\d+,\s*"addr":\s*"\[\d\][\da-fA-F:]*"\}') # Courtesy of GPT
        return pattern.match(line)

    def is_BLE_beacon(self, ip):
        return self.ip_to_name.get(ip, False)

    def print_data_table(self):
        thread_id = str(threading.current_thread().ident)
        print(f'Thread: {thread_id}')
        print(*[f"{key}: {value}" for key, value in self.data_table.items()], sep="\n")

    # Updates this scaner's datatable and our threadsafe trilateration_table
    def update_tables(self, IP_ADDR, RSSI):
        if self.is_BLE_beacon(IP_ADDR):
            # We have this address in our lookup table
            if self.data_table.get(IP_ADDR, None):
                (rssi_values, average) = self.data_table[IP_ADDR]

                if len(rssi_values) >= self.ROLL_AVG_SIZE:
                    # We have met the number of measurements in our rolling average
                    rssi_values.pop(0) # remove oldest rssi value from front of array
                    rssi_values.append(RSSI) # latest rssi value at end of array
                else:
                    # We want to add more measurements to our average
                    rssi_values.append(RSSI)

                new_average = self.average(rssi_values)
                self.data_table[IP_ADDR] = (rssi_values, new_average)
                self.trilateration_table.update_rssi(IP_ADDR, new_average, self.scanner_id) # Update trilateration table

            else: # This address hasn't been added to our data table yet
                self.data_table[IP_ADDR] = ([RSSI], RSSI)
                self.trilateration_table.update_rssi(IP_ADDR, RSSI, self.scanner_id) # Update trilateration table

    # Read strings off of serial after 'timer' seconds
    def ser_read(self, timer):
        time.sleep(timer) # wait 'timer' seconds

        # Map pretty print
        # self.print_data_table()

        lines = self.ser.readlines()
        for line in lines:
            # action in here
            line = line.decode('latin-1').strip()
            # print(line)
            if self.is_gapscan_info(line):
                data = json.loads(line)
                self.update_tables(data['addr'],data['rssi'])



     
            
            

