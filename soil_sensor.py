import time
from machine import UART

PH_DATA = b"\x01\x03\x00\x03\x00\x04\xB4\x09"           #the soil ph
MOISTURE_DATA = b"\x01\x03\x00\x00\x00\x01\x84\x0A"     #the soil humidity
TEMP_DATA = b"\x01\x03\x00\x01\x00\x02\x95\xCB"         #the soil temp
CONDUCTIVITY_DATA = b"\x01\x03\x00\x02\x00\x03\xA4\x0B" #the soil conductivity
NITROGEN_DATA = b"\x01\x03\x00\x04\x00\x05\xC4\x08"     #the soil N's content
PHOSPHORUS_DATA = b"\x01\x03\x00\x05\x00\x06\xD5\xC9"   #the soil P's content
POTASSIUM_DATA = b"\x01\x03\x00\x06\x00\x07\xE4\x09"    #the soil K's content
SAINITY_DATA = b"\x01\x03\x00\x07\x00\x08\xF5\xCD"      #the soil salt's content

#crc16 modbus计算http://www.ip33.com/crc.html



class the_soil_sensor():
    def __init__(self,uart,freq):
        self.uart = uart
        self.freq = freq
        self.UART = UART(self.uart,self.freq)
        self.uartinit = self.UART.init(self.freq,bits = 8,parity = None,stop = 1)
    def write_cmd(self,cmd):
        self.UART.write(cmd)

    def read_uart(self):
        return(self.UART.read())


    def _read_measurement(self, command, divisor):
        """Read one value while retaining the original wire and error behavior."""
        self.write_cmd(command)
        time.sleep(0.2)
        response = self.read_uart()
        try:
            # Keep legacy unpadded hex concatenation for compatibility.
            # A big-endian conversion would change values when the low byte < 16.
            high = hex(response[3]).lstrip("0").lstrip("x")
            low = hex(response[4]).lstrip("0").lstrip("x")
            return float(int(high + low, 16) / divisor)
        except TypeError:
            return "error"

    def the_soil_ph(self, test=None):
        return self._read_measurement(PH_DATA, 10)

    def the_soil_water(self, test=None):
        return self._read_measurement(MOISTURE_DATA, 10)

    def the_soil_temp(self, test=None):
        return self._read_measurement(TEMP_DATA, 10)

    def the_soil_conductivity(self, test=None):
        return self._read_measurement(CONDUCTIVITY_DATA, 10)

    def the_soil_nitrogen(self, test=None):
        return self._read_measurement(NITROGEN_DATA, 100)

    def the_soil_phosphorus(self, test=None):
        return self._read_measurement(PHOSPHORUS_DATA, 100)

    def the_soil_potassium(self, test=None):
        return self._read_measurement(POTASSIUM_DATA, 100)

    def the_soil_sainity(self, test=None):
        return self._read_measurement(SAINITY_DATA, 100)

if __name__ == "__main__":
    from soil_sensor import the_soil_sensor
    soilsensor = the_soil_sensor(2,4800)
    soilsensor.the_soil_conductivity()
    soilsensor.the_soil_nitrogen()
    soilsensor.the_soil_ph()
    soilsensor.the_soil_phosphorus()
    soilsensor.the_soil_potassium()
    soilsensor.the_soil_sainity()
    soilsensor.the_soil_temp()
    soilsensor.the_soil_water()

