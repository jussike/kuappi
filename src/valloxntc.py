
vallox_ntc_temp = {
    160: 20,
    161: 20,
    162: 21,
    163: 21,
    164: 21,
    165: 22,
    166: 22,
    167: 22,
    168: 23,
    169: 23,
    170: 24,
    171: 24,
    172: 24,
    173: 25,
    174: 25,
    175: 26,
    176: 26,
    177: 27,
    178: 27,
    179: 27,
    180: 28,
    181: 28,
    182: 29,
    183: 29,
    184: 30,
    185: 30,
    186: 31,
    187: 31,
    188: 32,
    189: 32,
    190: 33,
}

def get_vallox_temp(raw):
    try:
        value = vallox_ntc_temp[raw]
    except IndexError:
        if raw < 160:
            value = -100
        elif raw > 190:
            value = 100
        else:
            value = 0
    return value
