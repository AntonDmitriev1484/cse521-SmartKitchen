from smartkitchen import controller
from smartkitchen import util

# List devices
print("\n=== Finding devices connected to serial port...")
devices =  util.DiscoverSerialDevices()
for devc in devices:
    print(devc)


# Create BleuIO instance
print("\n=== Attempting to create a BleuIO receiver instance...")
controller.testCreateDevice()