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

# Maps ip -> (Name, T=valid item / F=distractor)
ip_to_name = {
    "[0]C3:00:00:0B:1A:7C": ("Oatmeal", True)
}

Scanner = controller.Scanner('/dev/ttyACM0', ip_to_name)
Scanner.scan()

# controller.gapscanReceiver(bleuIO)

# # bleuIO.at_central()

# # def scan_cb(scan_input):
# #     print(scan_input)

# # bleuIO.register_scan_cb(scan_cb)

