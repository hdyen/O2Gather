import time
import serial
from config import DO_METER


def o2_simulator():
    pass


def byte_char_to_int_digit(b_char):
    switcher = {
        b'0': 0,
        b'1': 1,
        b'2': 2,
        b'3': 3,
        b'4': 4,
        b'5': 5,
        b'6': 6,
        b'7': 7,
        b'8': 8,
        b'9': 9
    }
    return switcher.get(b_char)


def parse_D(D):
    reading = {}

    # Lower Display reading
    LD = 0
    LD += byte_char_to_int_digit(D[7]) * 10 ** 3
    LD += byte_char_to_int_digit(D[8]) * 10 ** 2
    LD += byte_char_to_int_digit(D[9]) * 10
    LD += byte_char_to_int_digit(D[10])
    LD /= 10 ** byte_char_to_int_digit(D[5])
    reading['LD'] = LD

    # Lower Display Annunciator
    D2_switcher = {
        b'0': 'NO SYMBOL',
        b'1': '℃',
        b'2': '℉'
    }
    reading['LDA'] = D2_switcher.get(D[2], 'N/A')

    # Upper Display reading

    UD = 0
    UD += byte_char_to_int_digit(D[11]) * 10 ** 3
    UD += byte_char_to_int_digit(D[12]) * 10 ** 2
    UD += byte_char_to_int_digit(D[13]) * 10
    UD += byte_char_to_int_digit(D[14])
    UD /= 10 ** byte_char_to_int_digit(D[6])
    reading['UD'] = UD

    # Upper Display Annunciator
    D4_switcher = {
        b'0': 'NO SYMBOL',
        b'1': '℃',
        b'2': '℉',
        b'7': 'mg/L',
        b'6': '%O2'
    }

    reading['UDA'] = D4_switcher.get(D[4], 'N/A')

    # Reading polarity for the display
    if D[1] == b'0':
        pass
    elif D[1] == b'1':
        reading['UD'] *= -1.0
    elif D[1] == b'2':
        reading['LD'] *= -1.0
    elif D[1] == b'3':
        reading['UD'] *= -1.0
        reading['LD'] *= -1.0

    return reading

if __name__ == '__main__':
    ser = serial.Serial(
        port=DO_METER,
        baudrate=9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS
    )
    while 1:
        ser.reset_input_buffer()
        v_str = ser.read(16)
        D = []
        for i in range(0, 16, 1):
            D.append(v_str[i:i + 1])
        reading = parse_D(D)
        temp = reading['LD']
        temp_degree = reading['LDA']
        o2 = reading['UD']
        o2_unit = reading['UDA']
        print('Temp: {} {}, Oxygen: {} {}'.format(temp, temp_degree, o2, o2_unit))
        time.sleep(1)
