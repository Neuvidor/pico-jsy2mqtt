# boot.py
import machine
import network
import time
import os
from config import *

if DEBUG:
    print("-----------------------------------------------------------")
    print("boot.py - Starting...")

# Désactivation du REPL sur UART0 (libère GP0/GP1 pour Modbus)
os.dupterm(None, 0)

# Configuration UART0 pour JSY-MK-194G
uart = machine.UART(0)
uart.init(baudrate=9600, tx=machine.Pin(0), rx=machine.Pin(1))

# LED démarrage
led = machine.Pin("LED", machine.Pin.OUT)
led.on()
time.sleep(2)
led.off()


if DEBUG:
    print("boot.py - END")
