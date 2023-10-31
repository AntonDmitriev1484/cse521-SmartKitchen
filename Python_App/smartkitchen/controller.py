from bleuio_lib.bleuio_funcs import BleuIO
from bleuio_lib.exceptions import *

''' PyPip Docs: https://pypi.org/project/bleuio/#description
    Check README and requirements.txt for necessary dependencies
'''

def testCreateDevice():
    try:
        bleReceiver = BleuIO()
    except (OSError, BleuIoError, IndexError) as e:
        print("Error: Could not instantiate BleuIO receiver device")

        if (type(e) == IndexError):
            print(" | Could not autodetect any connected BleuIO devices")

        return

    print("Successfully created BleuIO device")

    # ATI info
    atiResponse = bleReceiver.ati()
    print(atiResponse.Cmd)
    print(atiResponse.Ack)
    print(atiResponse.Rsp)
    print(atiResponse.End)


def gapscanReceiver(receiver: BleuIO):
    # Put receiver into dual role mode
    receiver.at_dual()

    # Perform scan
    res = receiver.at_gapscan()

    # Return results (is the scan blocking?)
    print(res.Cmd)
    print(res.Ack)
    print(res.Rsp)
    print(res.End)

