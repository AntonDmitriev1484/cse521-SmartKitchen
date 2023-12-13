# Anton, Brendan, Jason - Group 11 - CSE 521 Project
# Designing an IoT Smart Kitchen Application with Bluetooth Low Energy RSSI Localization

This project is split into two parts:
 - NodeJS_App runs on Node server a Raspberry Pi connected by USB to 4 BleuIO dongles
 - Python_App runs a Python Server, localization, and TTS loop locally on a laptop
 - To facilitate communication between the two, make sure they are on the same network, and enter your laptop's hostname in NodeJS_App/BleuIO/index.js

 NodeJS_App
 - This is solely used for data collection, as we encountered a bug with PySerial midway through our development process.
 - Install dependencies by running `npm install`, run the server by running `node NodeJS_App/BleuIO/index.js`.

    This part of the app commands BleuIO receivers to scan for BLE beacons, and exports the RSSI data collected by each receiver to the Python server by HTTP request.

 Python_App
 - This is the meat & bones of our application, and runs on your personal computer
 - Install dependencies by running `pip install -r requirements.txt`, run the main app by running `python3 Python_App/smartkitchen2/app2.py`

 - Voice
    This part of the app receives messages from the Pi, and feeds them into trilateration logic running on one thread.
    A text to speech loop reads from a threadsafe datastructure (TrilaterationTable) that contains all localization data, and provides cues to the user.

    The Voice Instruction code is executed based on an adjustable iteration frequency of 8 seconds. To increase or decrease this, modify the time.sleep() commands in the main while loop in app2.py. Functions for generating voice commands can be found within the Voice.py file.

    NOTE: In the final version of the code, the requires() function takes in an array of items, but as of right now, the item array only has a length of 1, since only 1 item is required at a time. This can be modified in app2.py.

 - Localization
    To handle the significant noise in the raw data measurements uploaded by the Pi. We implemented TrilaterationTable, a threadsafe datastructure that runs a rolling exponential average over all incoming data, callibrates measurements at runtime, and makes data available to our primary localization function.

    NOTE: Trilateration table is somewhat of a misnomer, our implementation does not use trilateration, but our own localization technique

    The trilateration table is constantly being updated with data from the pi. This table is read from the main thread, to generate localization estimates, that are fed into the text to speech loop.

    The localization function, accepts a trilateration table as a system state, and outputs a localtion estimate for a specified beacon. If the beacon is within the "on-table" RSSI threshold of 3 receivers to be deemed as "on-table". The 2 receivers that report the two strongest RSSI readings help output a more precise estimate "on-table-right" "on-table-bottom" etc...