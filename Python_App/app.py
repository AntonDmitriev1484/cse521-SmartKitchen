from smartkitchen import controller
from smartkitchen import util

# Command to see all devices:
# 


# List devices
print("\n=== Finding devices connected to serial port...")
devices =  util.DiscoverSerialDevices()
for devc in devices:
    print(devc)


# Create BleuIO instance
print("\n=== Attempting to create a BleuIO receiver instance...")
Scanner = controller.Scanner('/dev/ttyACM0')
# Scanner.scan()

# controller.gapscanReceiver(bleuIO)

# # bleuIO.at_central()

# # def scan_cb(scan_input):
# #     print(scan_input)

# # bleuIO.register_scan_cb(scan_cb)

