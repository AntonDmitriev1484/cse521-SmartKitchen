from smartkitchen import controller
from smartkitchen import util

import threading
import time


# Maps ip -> (Name, T=valid item / F=distractor)
IP_TO_NAME = {
    "[0]C3:00:00:0B:1A:7C": ("Oatmeal", True),
    "[0]C3:00:00:0B:1A:7A": ("Communist Manifesto", True),
    "Placeholder" : ("Salt", True),
    "Placeholder" : ("1 Measure Cup", True),
    "Placeholder" : ("½ Measure Cup", True),
    "Placeholder" : ("¼ Measure Spoon", True),
    "Placeholder" : ("Pan", True),
    "Placeholder" : ("Stirring Spoon", True),
    "Placeholder" : ("Timer", True),
    "Placeholder" : ("Bowl", True),
    "Placeholder" : ("Metal Spoon", True),
    "Placeholder" : ("Cork Hot Pad", True),
}

itemsOnTable = []


def main():
    # List devices
    print("\n=== Finding devices connected to serial port...")
    devices =  util.DiscoverSerialDevices()

    trilateration_table = util.ThreadSafeTrilaterationMap(IP_TO_NAME)
    
    scanner_id = 0
    for devc in devices:
        print("\n=== Creating a BleuIO receiver instance and thread for "+devc)

        # Each scanner will asynchronously do this:
        def scanning_process(scanner_id):
            # Create BleuIO instance
            print("\n=== "+devc+" has started scanning on thread "
            +str(threading.current_thread().name) + " scanner id is "+str(scanner_id))

            Scanner = controller.Scanner(devc, IP_TO_NAME, trilateration_table, scanner_id)
            Scanner.scan()

        scanner_thread = threading.Thread(target=scanning_process, args=(scanner_id,))
        scanner_thread.start()
        scanner_id+=1

    while True:
        time.sleep(1)
        print("Main")
        
        # !!! INSERTION TRILATERATION LOGIC HERE OR IN BEACONINFO !!!

        trilateration_table.print()

main()


import pyttsx3
import time



def requires(inputArray):
    engine = pyttsx3.init()  # object creation
    """ RATE"""
    rate = engine.getProperty('rate')  # getting details of current speaking rate
    print(rate)  # printing current voice rate
    engine.setProperty('rate', 100)  # setting up new voice rate

    requireString = "The following items are required."

    """VOLUME"""
    volume = engine.getProperty('volume')  # getting to know current volume level (min=0 and max=1)
    print(volume)  # printing current volume level
    engine.setProperty('volume', 2.0)  # setting up volume level  between 0 and 1

    """VOICE"""
    voices = engine.getProperty('voices')  # getting details of current voice
    # engine.setProperty('voice', voices[0].id)  #changing index, changes voices. o for male

    engine.say("Put the following items on the table.")
    engine.runAndWait()
    for item in inputArray:
        engine.say(item)
        engine.runAndWait()
    engine.stop()

inputTest = ['Spoon', 'Oatmeal', 'Pot', 'Water']

# requires(inputTest)

def distractorPresent():
    engine = pyttsx3.init()  # object creation
    """ RATE"""
    rate = engine.getProperty('rate')  # getting details of current speaking rate
    print(rate)  # printing current voice rate
    engine.setProperty('rate', 100)  # setting up new voice rate

    requireString = "The following items are required."

    """VOLUME"""
    volume = engine.getProperty('volume')  # getting to know current volume level (min=0 and max=1)
    print(volume)  # printing current volume level
    engine.setProperty('volume', 2.0)  # setting up volume level  between 0 and 1

    """VOICE"""
    voices = engine.getProperty('voices')  # getting details of current voice
    # engine.setProperty('voice', voices[0].id)  #changing index, changes voices. o for male

    engine.say("There is a distractor on the table. Please remove it.")
    engine.runAndWait()
    engine.stop()

def correctItemAdded(ItemName):
    engine = pyttsx3.init()  # object creation
    """ RATE"""
    rate = engine.getProperty('rate')  # getting details of current speaking rate
    print(rate)  # printing current voice rate
    engine.setProperty('rate', 100)  # setting up new voice rate

    requireString = "The following items are required."

    """VOLUME"""
    volume = engine.getProperty('volume')  # getting to know current volume level (min=0 and max=1)
    print(volume)  # printing current volume level
    engine.setProperty('volume', 2.0)  # setting up volume level  between 0 and 1

    """VOICE"""
    voices = engine.getProperty('voices')  # getting details of current voice
    engine.setProperty('voice', voices[0].id)  #changing index, changes voices. o for male
    outputText = "The "
    outputText = outputText + ItemName
    outputText = outputText + " has been detected on the table. Good job! Smiling Emoji"
    engine.say(outputText)
    engine.runAndWait()
    engine.stop()

correctItemAdded("Brendan Yang")


requires(requiredItems)

