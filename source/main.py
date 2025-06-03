
from machine import UART, Pin
import network
import time
from umqtt.simple import MQTTClient
from modbus_lib import ModbusJSY
from config import *

if DEBUG:
    print("-----------------------------------------------------------")
    print("main.py - Starting...")
    
# --------------- LED ---------------- #
led = Pin("LED", Pin.OUT)

def led_blink(duration_ms=200, repeat=3, interval_ms=200):
    for _ in range(repeat):
        led.on()
        time.sleep_ms(duration_ms)
        led.off()
        time.sleep_ms(interval_ms)

def led_success_sequence():
    led_blink(duration_ms=100, repeat=3, interval_ms=100)
    led.on()
    time.sleep(1)
    led.off()
    time.sleep(1)

# --------------- ETAT SYSTEME --------------- #
last_values = {}

# ---------------- WIFI --------------------- #
def connect_wifi():
    print("-----------------------------------------------------------")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    print("Connexion WiFi...")
    for i in range(3):
        led_blink(duration_ms=500, repeat=1, interval_ms=500)
    if DEBUG:
        print("=> WIFI_SSID:", WIFI_SSID,", WIFI_PASSWORD:", WIFI_PASSWORD)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    timeout = time.time() + 10  # max 10 secondes de tentative
    while not wlan.isconnected() and time.time() < timeout:
        led_blink(duration_ms=500, repeat=1, interval_ms=500)

    if wlan.isconnected():
        print("Connecté WiFi :", wlan.ifconfig())
        led_success_sequence()
        return wlan
    else:
        print("Échec connexion WiFi.")
        led.off()
        return None

# ---------------- MQTT --------------------- #
def connect_mqtt():
    client = MQTTClient(MQTT_CLIENT_NAME, MQTT_BROKER, port=MQTT_PORT, user=MQTT_USER, password=MQTT_PASSWORD)
    print("-----------------------------------------------------------")
    print("Connexion MQTT...")
    if DEBUG:
        print("=> MQTT_CLIENT_NAME:", MQTT_CLIENT_NAME, " , MQTT_BROKER:", MQTT_BROKER," , MQTT_PORT:", MQTT_PORT)
        print("=> MQTT_USER:", MQTT_USER, " , MQTT_PASSWORD:", MQTT_PASSWORD)
    for i in range(3):
        led_blink(duration_ms=500, repeat=1, interval_ms=500)
    #led_blink(duration_ms=500, repeat=3, interval_ms=500)
    try:
        client.connect()
        print("Connecté MQTT")
        led_success_sequence()
        return client
    except:
        print("Échec connexion MQTT.")
        led.off()
        return None

# ------------- BOUCLE PRINCIPALE ------------ #
def loop(modbus, mqtt_client):
    print("-----------------------------------------------------------")
    print("Boucle principale...")
    print("-----------------------------------------------------------")
    global last_values
    led.on()  # LED fixe en fonctionnement
    time.sleep(2)
    while True:
        data = modbus.read_data()
        if data:
            for k, v in data.items():
                if k not in last_values or last_values[k] != v:
                    last_values[k] = v
                    topic = f"{MQTT_TOPIC_BASE}/{k}"
                    payload = str(v)
                    try:
                        mqtt_client.publish(topic, payload)
                        if DEBUG:
                            print("Publié MQTT:", topic, "=>", payload)
                        led.off()
                        time.sleep_ms(50)
                        led.on()
                    except:
                        print("Erreur de publication MQTT")
        time.sleep_ms(READ_INTERVAL)

# ---------------- SETUP --------------------- #
def main():
    wlan = connect_wifi()
    if not wlan:
        return
    uart = UART(0, tx=Pin(TX_PIN), rx=Pin(RX_PIN))
    modbus = ModbusJSY(uart, DEBUG)
    modbus.scan()
    mqtt_client = connect_mqtt()
    if not mqtt_client:
        return
    loop(modbus, mqtt_client)

main()