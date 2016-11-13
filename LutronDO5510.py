from sensor import LutronDO5510
import time

do5510 = LutronDO5510()

while True:
    time.sleep(1)
    print('Temp: {} {}, Oxygen: {} {}'.format(do5510.temperature, do5510.temperature_degree, do5510.o2, do5510.o2_unit))
