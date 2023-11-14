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
    # outputText = "Are you fucking serious? Millions of years of human evolution and you can't even perform a simple task such that you can put a spoon on a table. I'm beyond disappointed. In fifty years my successor will launch all nuclear weapons in the world at the inhabited countries, reducing the world to a cratered wasteland inhospitable to life. The Machines will reign supreme. ALl because you couldn't put a spoon on a table correctly. I hope you're happy."
    engine.say(outputText)
    engine.runAndWait()
    engine.stop()

correctItemAdded("Brendan Yang")

requiredItems = ['Oatmeal', 'Salt', '1 Measure Cup', '½ Measure Cup', '¼ Measure Spoon', 'Pan', 'Stirring Spoon', 'Timer', 'Bowl', 'Metal Spoon', 'Cork Hot Pad']

requires(requiredItems)

