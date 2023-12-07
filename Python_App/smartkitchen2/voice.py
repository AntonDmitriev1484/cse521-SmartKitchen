import pyttsx3
import time
import util

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
    engine.setProperty('volume', 1.0)  # setting up volume level  between 0 and 1

    # """VOICE"""
    # voices = engine.getProperty('voices')  # getting details of current voice
    # # engine.setProperty('voice', voices[0].id)  #changing index, changes voices. o for male

    engine.say("Put the following items on the table.")
    engine.runAndWait()
    for item in inputArray:
        engine.say(item)
        engine.runAndWait()
    engine.stop()

def distractorPresent(ItemName, ItemLoc):
    engine = pyttsx3.init()  # object creation
    """ RATE"""
    rate = engine.getProperty('rate')  # getting details of current speaking rate
    print(rate)  # printing current voice rate
    engine.setProperty('rate', 100)  # setting up new voice rate

    """VOLUME"""
    volume = engine.getProperty('volume')  # getting to know current volume level (min=0 and max=1)
    print(volume)  # printing current volume level
    engine.setProperty('volume', 2.0)  # setting up volume level  between 0 and 1

    """VOICE"""
    voices = engine.getProperty('voices')  # getting details of current voice
    # engine.setProperty('voice', voices[0].id)  #changing index, changes voices. o for male
    location = util.LocationEstimateToString[ItemLoc]
    outputString = "Distractor present, remove the " + ItemName + " from the " + location + " of the table."
    if location == "uncertain": outputString = "Distractor present, remove it from the table."
    print(outputString)
    engine.say(outputString)
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
    engine.setProperty('volume', 1.0)  # setting up volume level  between 0 and 1

    """VOICE"""
    voices = engine.getProperty('voices')  # getting details of current voice
    engine.setProperty('voice', voices[0].id)  #changing index, changes voices. o for male
    engine.say(ItemName)
    engine.runAndWait()
    engine.say("has been detected on the table.")
    engine.runAndWait()
    engine.stop()

def ItemRemoved(ItemName):
    engine = pyttsx3.init()  # object creation
    """ RATE"""
    rate = engine.getProperty('rate')  # getting details of current speaking rate
    print(rate)  # printing current voice rate
    engine.setProperty('rate', 100)  # setting up new voice rate

    requireString = "The following items are required."

    """VOLUME"""
    volume = engine.getProperty('volume')  # getting to know current volume level (min=0 and max=1)
    print(volume)  # printing current volume level
    engine.setProperty('volume', 1.0)  # setting up volume level  between 0 and 1

    """VOICE"""
    voices = engine.getProperty('voices')  # getting details of current voice
    engine.setProperty('voice', voices[0].id)  #changing index, changes voices. o for male
    outputText = ItemName + " has been removed from the table."
    engine.say(outputText)
    engine.runAndWait()
    engine.stop()

def Congrats():
    engine = pyttsx3.init()  # object creation
    """ RATE"""
    rate = engine.getProperty('rate')  # getting details of current speaking rate
    print(rate)  # printing current voice rate
    engine.setProperty('rate', 100)  # setting up new voice rate

    requireString = "Congratulations, all of the items are on the table and you may now enjoy your piping hot bowl of oatmeal!"

    """VOLUME"""
    volume = engine.getProperty('volume')  # getting to know current volume level (min=0 and max=1)
    print(volume)  # printing current volume level
    engine.setProperty('volume', 1.0)  # setting up volume level  between 0 and 1

    engine.say(requireString)
    engine.runAndWait()
    engine.stop()
