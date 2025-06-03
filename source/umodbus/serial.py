
from umodbus.modbus import crc16, ModbusException
import struct
import time

class SerialModbusRTU:
    def __init__(self, uart, slave_addr=1):
        self.uart = uart
        self.slave_addr = slave_addr

    def read_holding_registers(self, addr, count):
        function_code = 3
        payload = struct.pack(">B B H H", self.slave_addr, function_code, addr, count)
        crc = crc16(payload)
        payload += struct.pack("<H", crc)
        self.uart.write(payload)

        time.sleep(0.1)
        resp = self.uart.read()

        if not resp or len(resp) < 5:
            raise ModbusException("No response or too short")

        if resp[1] & 0x80:
            raise ModbusException("Modbus exception response")

        byte_count = resp[2]
        registers = []
        for i in range(3, 3 + byte_count, 2):
            registers.append(resp[i] << 8 | resp[i + 1])
        return registers

    def write_single_register(self, addr, value):
        function_code = 6
        payload = struct.pack(">B B H H", self.slave_addr, function_code, addr, value)
        crc = crc16(payload)
        payload += struct.pack("<H", crc)
        self.uart.write(payload)
        time.sleep(0.05)
        return self.uart.read()
