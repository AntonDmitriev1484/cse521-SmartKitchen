import sys
import serial
import threading
from enum import Enum

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

def average(array):
        sum = 0
        for el in array:
            sum += el
        return sum / len(array)


class LocationEstimate(Enum):
    TOP_LEFT = 1
    TOP_RIGHT = 2
    BOT_LEFT = 3
    BOT_RIGHT = 4
    OFF = 5
    IDK = 6
    # Location estimate, can be directly printed in a string by just passing the object
    # ex.
    # selected_position = Position.TOP_LEFT
    # print(f"You selected {selected_position}") -> prints: You selected top left
    def __str__(self): 
        return LocationEstimateToString[self]

LocationEstimateToString = {
    LocationEstimate.TOP_LEFT: "top left",
    LocationEstimate.TOP_RIGHT: "top right",
    LocationEstimate.BOT_LEFT: "bottom left",
    LocationEstimate.BOT_RIGHT: "bottom right",
    LocationEstimate.OFF: "off of the table",
    LocationEstimate.IDK: "uncertain"
}



class BeaconInfo:
    # Struct / class to deal with beacon information

    def __init__(self, name, is_not_distractor):
        self.rssi_raw_data = [[], [], []] 
        # device_id is an index to its past 3 rssi measurements for this beacon

        self.rssi_array = [None, None, None]
        self.ROLL_AVG_SIZE = 4
        
        self.name = name

        self.required_item = is_not_distractor
        
        self.coord = (0,0)
        self.loc_estimate = LocationEstimate.OFF

    def add_data(self, device_id, data_point):
        # NOTE: Device should be passed as an int
        # We have this address in our lookup table

        smoothing_factor = 1.5

        if self.rssi_raw_data[device_id]:
            rssi_values = self.rssi_raw_data[device_id] 
            #Gives us an array of rolling average values for this beacon for this device
            if len(rssi_values) >= self.ROLL_AVG_SIZE:
                # We have met the number of measurements in our rolling average
                rssi_values.pop(0) # remove oldest rssi value from front of array
                rssi_values.append(data_point) # latest rssi value at end of array
            else:
                # We want to add more measurements to our average
                rssi_values.append(data_point)
                
            #new_average = average(rssi_values) # Error here -> adding 'int' to NoneType
            # Exponential average
            prev_avg = self.rssi_array[device_id]
            # new_average = smoothing_factor * (data_point - prev_avg)
            smooth_term = (smoothing_factor / (1 + self.ROLL_AVG_SIZE))
            new_average = (data_point * smooth_term) + (prev_avg * (1-smooth_term))

            self.rssi_raw_data[device_id] = rssi_values
            self.rssi_array[device_id] = round(new_average,2)

        else: # This address hasn't been added to our data table yet
            self.rssi_raw_data[device_id] = [data_point]
            self.rssi_array[device_id] = data_point # Update trilateration table

        return

    def __repr__(self):
        if not self.required_item:
            return f"Distractor {self.name} | {self.rssi_array} | {self.loc_estimate}"
        else:
            return f"{self.name} | {self.rssi_array} | {self.loc_estimate}"


class ThreadSafeTrilaterationMap:

    def __init__(self, ip_to_name):
        self.inner_map = {}
        self.lock = threading.Lock()
        self.ip_to_name = ip_to_name
        self.bounds_initialized = False


    def init_bounds(self, scan0_bound, scan1_inner_bound, scan1_outer_bound, scan2_bound):
        self.scan0_bound = scan0_bound
        self.scan1_inner_bound = scan1_inner_bound
        self.scan1_outer_bound = scan1_outer_bound
        self.scan2_bound = scan2_bound
        self.bounds_initialized = True

        print("Initialized bounds: ")
        print("scan0_bound "+str(self.scan0_bound))
        print("scan1_inner_bound "+str(self.scan1_inner_bound))
        print("scan1_outer_bound "+str(self.scan1_outer_bound))
        print("scan2_bound "+str(self.scan2_bound))


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

        for key, value in self.inner_map.items():
            if value.name == "Pan":
                print(f"Pan {value.name} | 0: {str(value.rssi_raw_data[0])} , 1: {value.rssi_raw_data[1]}, 2: {value.rssi_raw_data[2]}| \n{value.rssi_array} | {value.loc_estimate}")

        # print(*[f"{key}: {value}" for key, value in self.inner_map.items()], sep="\n")

    # Return a LocationEstimate enum based on 4 rssi bounds
    def get_location(self, beacon_info):

        # While we callibrate, don't do any bounds estimates
        if not self.bounds_initialized:
            return LocationEstimate.OFF
        
        rssi = beacon_info.rssi_array

        in_inner_ring = self.scan1_inner_bound > rssi[1] > self.scan1_outer_bound
        
        
        in_scan0_bounds = rssi[0] > self.scan0_bound
        in_scan2_bounds = rssi[2] > self.scan2_bound

        if in_scan0_bounds and in_inner_ring:
            # upper_right_confirmation = rssi[0] < rssi[2] and rssi[1] < rssi[2]
            # if upper_right_confirmation:
                return LocationEstimate.TOP_RIGHT
            # else:
            #     return LocationEstimate.IDK
        
        if in_scan2_bounds and in_inner_ring:
            # upper_left_confirmation = rssi[2] > rssi[0] and rssi[1] > rssi[0]
            # if upper_left_confirmation:
                return LocationEstimate.TOP_LEFT
            # else:
            #     return LocationEstimate.IDK
        if not in_scan0_bounds and not in_scan2_bounds:
            return LocationEstimate.OFF
        
        return LocationEstimate.IDK
    
    # Update value array specifically at scanner_id
    def update_rssi(self, key, rssi_value, scanner_id):
        with self.lock:

            info = self.inner_map.get(
                key,
                BeaconInfo(self.ip_to_name[key][0], self.ip_to_name[key][1]) # Create a new BeaconInfo object if not present
                )
            
            # No idea why it doesn't make it in here for distractor
            # if key == "[0]C3:00:00:0B:1A:7A":
            #     print("Updating rssi for distractor")
            
            info.add_data(scanner_id, round(rssi_value, 2)) # Add new data to our rolling average
            info.loc_estimate = self.get_location(info) # Use updated beacon data to update the location estimate

            self.inner_map[key] = info
