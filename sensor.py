from config import DO_METER
import serial
import threading
import time


class Sensor:
    pass


class LutronDO5510(Sensor):
    PORT = DO_METER
    BAUDRATE = 9600
    PARITY = serial.PARITY_NONE
    STOPBITS = serial.STOPBITS_ONE
    BYTESIZE = serial.EIGHTBITS

    lock = threading.Lock()

    temperature = 0
    temperature_degree = ''
    o2 = 0
    o2_unit = ''

    def __init__(self):
        self.ser = serial.Serial(
            port=self.PORT,
            baudrate=self.BAUDRATE,
            parity=self.PARITY,
            stopbits=self.STOPBITS,
            bytesize=self.BYTESIZE
        )
        self.thread_reset_input_buffer_per_second = threading.Thread(target=self.reset_input_buffer_per_second,
                                                                     daemon=True)
        self.thread_reset_input_buffer_per_second.start()
        self.thread_update_reading_per_second = threading.Thread(target=self.update_reading_per_second, daemon=True)
        self.thread_update_reading_per_second.start()

    def reset_input_buffer(self):
        with self.lock:
            self.ser.reset_input_buffer()

    def reset_input_buffer_per_second(self):
        while True:
            self.reset_input_buffer()
            time.sleep(1)

    def read_input_buffer(self):
        v_str = self.ser.read(16)
        buf = []
        for i in range(0, 16, 1):
            buf.append(v_str[i:i + 1])
        return buf

    def update_reading(self):

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

        buf = self.read_input_buffer()

        # Temperature
        lower_display_reading = 0
        lower_display_reading += byte_char_to_int_digit(buf[7]) * 10 ** 3
        lower_display_reading += byte_char_to_int_digit(buf[8]) * 10 ** 2
        lower_display_reading += byte_char_to_int_digit(buf[9]) * 10
        lower_display_reading += byte_char_to_int_digit(buf[10])
        lower_display_reading /= 10 ** byte_char_to_int_digit(buf[5])
        self.temperature = lower_display_reading

        # Temperature Degree
        digit2_switcher = {
            b'0': 'NO SYMBOL',
            b'1': '℃',
            b'2': '℉'
        }
        self.temperature_degree = digit2_switcher.get(buf[2], 'N/A')

        # O2
        upper_display_reading = 0
        upper_display_reading += byte_char_to_int_digit(buf[11]) * 10 ** 3
        upper_display_reading += byte_char_to_int_digit(buf[12]) * 10 ** 2
        upper_display_reading += byte_char_to_int_digit(buf[13]) * 10
        upper_display_reading += byte_char_to_int_digit(buf[14])
        upper_display_reading /= 10 ** byte_char_to_int_digit(buf[6])
        self.o2 = upper_display_reading

        # O2 Unit
        digit4_switcher = {
            b'0': 'NO SYMBOL',
            b'1': '℃',
            b'2': '℉',
            b'7': 'mg/L',
            b'6': '%O2'
        }
        self.o2_unit = digit4_switcher.get(buf[4], 'N/A')

        # Reading Polarity for the Display
        if buf[1] == b'0':
            pass
        elif buf[1] == b'1':
            self.o2 *= -1.0
        elif buf[1] == b'2':
            self.temperature *= -1.0
        elif buf[1] == b'3':
            self.o2 *= -1.0
            self.temperature *= -1.0

    def update_reading_per_second(self):
        while True:
            self.update_reading()
            time.sleep(1)
