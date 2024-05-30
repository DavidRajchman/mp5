from machine import Pin, ADC, unique_id
import network
from simple import MQTTClient
import time
import random
import json
print("script started")

SERVER = "mqtt.eclipseprojects.io"
TOPIC = "NSI/david/test/teploty"
PORT = 1883

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

SSID = "IoTtest"
PASSWORD = "123456789"



wlan.connect(SSID, PASSWORD)

time.sleep(2)

while wlan.isconnected() == False:
    print("WiFi connection status: ", wlan.status())
    time.sleep(2)
    print("wifi ready")
print(wlan.ifconfig())
client = MQTTClient(client_id="RaspberryPiPico", server=SERVER, port=PORT)
client.connect()
print("client connected")

while True:
    temperature = 15 + random.randint(0, 15)  
    
    timestamp = time.time()

    payload = json.dumps({"temperature": temperature, "timestamp": timestamp})

    client.publish(TOPIC, payload)
    print(payload)
    print("message sent")
    time.sleep(5)
