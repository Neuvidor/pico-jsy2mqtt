
import time
import ustruct

class ModbusJSY:
    def __init__(self, uart, debug=False):
        self.uart = uart
        self.debug = debug
        self.baudrates = [2400, 4800, 9600, 19200, 28800, 38400, 57600, 76800, 115200]
        self.addresses = range(1, 11)
        self.unit_id = None
        self.baudrate = None

    def crc16(self, data):
        crc = 0xFFFF
        for pos in data:
            crc ^= pos
            for i in range(8):
                if (crc & 1):
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return ustruct.pack('<H', crc)

    def scan(self):
        if self.debug:
            print("-----------------------------------------------------------")
            print(f"JSY module ID & Baudrate scan...")
        for baud in self.baudrates:
            self.uart.init(baudrate=baud)
            for addr in self.addresses:
                request = bytearray([addr, 0x03, 0x00, 0x01, 0x00, 0x04])
                request += self.crc16(request)
                self.uart.write(request)
                time.sleep(0.1)
                if self.uart.any():
                    response = self.uart.read()
                    if response and response[0] == addr:
                        self.unit_id = addr
                        self.baudrate = baud
                        if self.debug:
                            print(f"=> Module détecté - Baudrate: {baud}, ID: {addr}")
                        return True
                if self.debug:
                    print(f"XXX Pas de réponse @ Baudrate: {baud}, ID: {addr}")
        raise Exception("Aucun module JSY-MK-194G trouvé")

    def read_data(self):
        if self.unit_id is None:
            return None
        request = bytearray([self.unit_id, 0x03, 0x00, 0x48, 0x00, 0x0E])
        request += self.crc16(request)
        self.uart.write(request)
        time.sleep(0.2)
        if self.uart.any():
            response = self.uart.read()
            if len(response) >= 61:
                return self.parse_data(response)
        return None

    def parse_data(self, response):
        data = {}
        try:
            raw = response[3:3+56]
            vals = [ustruct.unpack(">I", raw[i:i+4])[0] for i in range(0, len(raw), 4)]

            sens = vals[6]
            ch1_sign = -1 if (sens >> 24) == 1 else 1
            ch2_sign = -1 if ((sens >> 16) & 0xFF) == 1 else 1

            data["ch1_voltage"] = round(vals[0] / 10000, 1)
            data["ch1_current"] = round(vals[1] / 10000, 1)
            data["ch1_power"] = ch1_sign * int(vals[2] / 10000)
            data["ch1_energy_pos"] = round(vals[3] / 10000, 3)
            data["ch1_power_factor"] = round(vals[4] / 1000, 2)
            data["ch1_energy_neg"] = round(vals[5] / 10000, 3)
            data["frequency"] = round(vals[7] / 100, 1)

            data["ch2_voltage"] = round(vals[8] / 10000, 1)
            data["ch2_current"] = round(vals[9] / 10000, 1)
            data["ch2_power"] = ch2_sign * int(vals[10] / 10000)
            data["ch2_energy_pos"] = round(vals[11] / 10000, 3)
            data["ch2_power_factor"] = round(vals[12] / 1000, 2)
            data["ch2_energy_neg"] = round(vals[13] / 10000, 3)
        except:
            if self.debug:
                print("Erreur de décodage Modbus")
        return data
