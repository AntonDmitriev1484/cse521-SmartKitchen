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

class BeaconInfo:
    # Struct / class to deal with beacon information
    # Extend this however you want

    def __init__(self, name, is_not_distractor):
        self.rssi_array = [None, None, None]
        self.is_distractor = not is_not_distractor
        self.name = name

    def __repr__(self):
        if self.is_distractor:
            return f"Distractor {self.name} | {self.rssi_array} "
        else:
            return f"{self.name} | {self.rssi_array}"


class ThreadSafeTrilaterationMap:
    def __init__(self, ip_to_name):
        self.inner_map = {}
        self.lock = threading.Lock()
        self.ip_to_name = ip_to_name

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

    def print(self):
        print(*[f"{key}: {value}" for key, value in self.inner_map.items()], sep="\n")
    
    # Update value array specifically at scanner_id
    def update_rssi(self, key, rssi_value, scanner_id):
        with self.lock:

            info = self.inner_map.get(
                key,
                BeaconInfo(self.ip_to_name[key][0], self.ip_to_name[key][1]) # Create a new BeaconInfo object if not present
                )

            info.rssi_array[scanner_id] = round(rssi_value, 2)

            self.inner_map[key] = info
