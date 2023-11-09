import sys
import serial
import threading

# Returns list of port names with active devices connected
# @courtesy: https://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python
def DiscoverSerialDevices():
    # Windows ports
    if (sys.platform.startswith('win')):
        ports = [f'COM{i}' for i in range(1,256)]
    # Linux devices
    elif sys.platform.startswith('linux'):
        ports = [f'/dev/ttyACM{i}' for i in range(256)]
    # Unsupported OS
    else:
        raise EnvironmentError("Unsupported platform!")
    
    foundDevicePortNames = []
    for port in ports:
        try:
            # If successfully open w/o exception, add port name
            s = serial.Serial(port)
            s.close()
            foundDevicePortNames.append(port)
        except (OSError, serial.SerialException):
            pass
        
    return foundDevicePortNames

class ThreadSafeTrilaterationMap:
    def __init__(self):
        self.inner_map = {}
        self.lock = threading.Lock()

    def put(self, key, value):
        with self.lock:
            self.inner_map[key] = value

    def get(self, key):
        with self.lock:
            return self.inner_map.get(key)

    def delete(self, key):
        with self.lock:
            if key in self.inner_map:
                del self.inner_map[key]
    
    # Update value array specifically at scanner_id
    def update_rssi(self, key, rssi_value, scanner_id):
        with self.lock:
            # Only take the rssi array out of the value tuple
            # Key = ip, Value = ( [ rssi1, rssi2, rssi3 ] , any calculations , ...)
            value_tuple = self.inner_map.get(key)
            rssi_array = value_tuple[0]
            rssi_array[scanner_id] = rssi_value
            value_tuple[0] = rssi_array
            self.inner_map.put(value_tuple)
