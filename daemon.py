import avango.daemon
import os
import sys

print("whats up")

def init_mouse():

    mouse_name = os.popen(
        "ls /dev/input/by-id | grep \"-event-mouse\" | sed -e \'s/\"//g\'  | cut -d\" \" -f4").read(
        )

    mouse_name = mouse_name.split()
    if len(mouse_name) > 0:

        mouse_name = mouse_name[0]

        mouse = avango.daemon.HIDInput()
        mouse.station = avango.daemon.Station('gua-device-mouse')
        mouse.device = "/dev/input/by-id/" + mouse_name

        mouse.values[0] = "EV_REL::REL_X"
        mouse.values[1] = "EV_REL::REL_Y"

        mouse.buttons[0] = "EV_KEY::BTN_LEFT"
        mouse.buttons[1] = "EV_KEY::BTN_RIGHT"

        device_list.append(mouse)
        print("Mouse started at:", mouse_name)

    else:
        print("Mouse NOT found !")


def init_keyboard():
    keyboard_name = os.popen(
        "ls /dev/input/by-id | grep \"-event-kbd\" | sed -e \'s/\"//g\'  | cut -d\" \" -f4").read(
        )

    keyboard_name = keyboard_name.split()

    for i, name in enumerate(keyboard_name):

        keyboard = avango.daemon.HIDInput()
        keyboard.station = avango.daemon.Station(
            'gua-device-keyboard' + str(i))
        keyboard.device = "/dev/input/by-id/" + name

        keyboard.buttons[0] = "EV_KEY::KEY_Q"
        keyboard.buttons[1] = "EV_KEY::KEY_W"
        keyboard.buttons[2] = "EV_KEY::KEY_E"
        keyboard.buttons[3] = "EV_KEY::KEY_R"
        keyboard.buttons[4] = "EV_KEY::KEY_T"
        keyboard.buttons[5] = "EV_KEY::KEY_Z"
        keyboard.buttons[6] = "EV_KEY::KEY_U"
        keyboard.buttons[7] = "EV_KEY::KEY_I"
        keyboard.buttons[8] = "EV_KEY::KEY_O"
        keyboard.buttons[9] = "EV_KEY::KEY_P"
        keyboard.buttons[10] = "EV_KEY::KEY_A"
        keyboard.buttons[11] = "EV_KEY::KEY_S"
        keyboard.buttons[12] = "EV_KEY::KEY_D"
        keyboard.buttons[13] = "EV_KEY::KEY_F"
        keyboard.buttons[14] = "EV_KEY::KEY_G"
        keyboard.buttons[15] = "EV_KEY::KEY_H"
        keyboard.buttons[16] = "EV_KEY::KEY_J"
        keyboard.buttons[17] = "EV_KEY::KEY_K"
        keyboard.buttons[18] = "EV_KEY::KEY_L"
        keyboard.buttons[19] = "EV_KEY::KEY_Y"
        keyboard.buttons[20] = "EV_KEY::KEY_X"
        keyboard.buttons[21] = "EV_KEY::KEY_C"
        keyboard.buttons[22] = "EV_KEY::KEY_V"
        keyboard.buttons[23] = "EV_KEY::KEY_B"
        keyboard.buttons[24] = "EV_KEY::KEY_N"
        keyboard.buttons[25] = "EV_KEY::KEY_M"

        keyboard.buttons[26] = "EV_KEY::KEY_PAGEUP"
        keyboard.buttons[27] = "EV_KEY::KEY_PAGEDOWN"

        keyboard.buttons[28] = "EV_KEY::KEY_1"
        keyboard.buttons[29] = "EV_KEY::KEY_2"
        keyboard.buttons[30] = "EV_KEY::KEY_LEFT"
        keyboard.buttons[31] = "EV_KEY::KEY_RIGHT"

        device_list.append(keyboard)
        print("Keyboard " + str(i) + " started at:", name)

## Initializes AR Track
def init_art_tracking_wall():

    # create instance of DTrack
    _dtrack = avango.daemon.DTrack()
    _dtrack.port = "5000" # ART port

    _dtrack.stations[10] = avango.daemon.Station('tracking-glasses-1') # 3D-TV wired shutter glasses
    _dtrack.stations[2] = avango.daemon.Station('tracking-glasses-2') # small powerwall polarization glasses

    _dtrack.stations[1] = avango.daemon.Station('tracking-pointer-1') # AUGUST pointer
    _dtrack.stations[18] = avango.daemon.Station('tracking-pointer-2') # Gyromouse
   

    device_list.append(_dtrack)
    print("ART Tracking  @Powerwall started")

def init_spacemouse():
    
    # search for new spacemouse (blue LED)
    _string = get_event_string(1, "3Dconnexion SpaceNavigator for Notebooks")

    if _string is None:
        _string = get_event_string(1, "3Dconnexion SpaceNavigator")
            
    if _string is not None: # new spacemouse was found
        _spacemouse = avango.daemon.HIDInput()
        _spacemouse.station = avango.daemon.Station('gua-device-spacemouse') # create a station to propagate the input events
        _spacemouse.device = _string
        _spacemouse.timeout = '14' # better !
        _spacemouse.norm_abs = 'True'

        # map incoming spacemouse events to station values
        _spacemouse.values[0] = "EV_REL::REL_X"   # trans X
        _spacemouse.values[1] = "EV_REL::REL_Z"   # trans Y
        _spacemouse.values[2] = "EV_REL::REL_Y"   # trans Z
        _spacemouse.values[3] = "EV_REL::REL_RX"  # rotate X
        _spacemouse.values[4] = "EV_REL::REL_RZ"  # rotate Y
        _spacemouse.values[5] = "EV_REL::REL_RY"  # rotate Z

        # buttons
        _spacemouse.buttons[0] = "EV_KEY::BTN_0" # left button
        _spacemouse.buttons[1] = "EV_KEY::BTN_1" # right button

        device_list.append(_spacemouse)
        print("New SpaceMouse started at:", _string)

        return


    print("SpaceMouse NOT found!")


## Gets the event string of a given input device.
# @param STRING_NUM Integer saying which device occurence should be returned.
# @param DEVICE_NAME Name of the input device to find the event string for.
def get_event_string(STRING_NUM, DEVICE_NAME):

    # file containing all devices with additional information
    _device_file = os.popen("cat /proc/bus/input/devices").read()
    _device_file = _device_file.split("\n")
    
    DEVICE_NAME = '\"' + DEVICE_NAME + '\"'
    
    # lines in the file matching the device name
    _indices = []

    for _i, _line in enumerate(_device_file):
        if DEVICE_NAME in _line:
            _indices.append(_i)

    # if no device was found or the number is too high, return an empty string
    if len(_indices) == 0 or STRING_NUM > len(_indices):
        return None

    # else captue the event number X of one specific device and return /dev/input/eventX
    else:
        _event_string_start_index = _device_file[_indices[STRING_NUM-1]+4].find("event")
                
        return "/dev/input/" + _device_file[_indices[STRING_NUM-1]+4][_event_string_start_index:].split(" ")[0]
    

device_list = []

init_mouse()
init_keyboard()
init_art_tracking_wall()
init_spacemouse()

avango.daemon.run(device_list)
