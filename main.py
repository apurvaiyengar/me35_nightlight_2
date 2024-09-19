import asyncio
from machine import I2C, Pin, PWM
import neopixel
from button import Button
from accel import Acceleration
import struct
import time
import math
from mqtt import MQTTClient


# Setup WiFi connection
import network

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('Tufts_Robot', '')

while wlan.ifconfig()[0] == '0.0.0.0':
    print('.', end=' ')
    time.sleep(1)

print(wlan.ifconfig())

# MQTT setup
mqtt_broker = 'broker.hivemq.com'
port = 1883
topic_sub = 'ME35-24/Apurva'  # Updated topic
topic_pub = 'ME35-24/Apurva'
# MQTT callback function
def mqtt_callback(topic, msg):
    global system_on
    print(f"Message received: {topic.decode()}, {msg.decode()}")

    if msg.decode() == 'on':
        print("Turning system ON")
        system_on = True
    elif msg.decode() == 'off':
        print("Turning system OFF")
        system_on = False


client = MQTTClient('ME35_chris', mqtt_broker, port, keepalive=60)
client.connect()
client.set_callback(mqtt_callback)
client.subscribe(topic_sub.encode())
print('Connected to MQTT broker')

# Initialize Button and Accelerometer
button = Button(pin=20, neopixel_pin=28, buzzer_pin=18)
accelerometer = Acceleration(sda=Pin('GPIO26', Pin.OUT), scl = Pin('GPIO27', Pin.OUT), mqtt_client=client, indicator_pin=15)

# Global variable to turn the system on/off
system_on = False

# External LED dimming (breathe) function
async def breathe_led():
    led_pwm = machine.PWM(machine.Pin(13))  # Pin 13 for the external LED
    led_pwm.freq(1000)
    while system_on:
        for duty in range(0, 65535, 500):
            led_pwm.duty_u16(duty)
            await asyncio.sleep_ms(10)
        for duty in range(65535, 0, -500):
            led_pwm.duty_u16(duty)
            await asyncio.sleep_ms(10)

# Button checking task
async def check_button():
    while system_on:
        await button.check_and_update()
        await asyncio.sleep_ms(50)

# Accelerometer task to check for taps
async def check_accelerometer():
    while system_on:
        await accelerometer.read_event()

# MQTT task to continually check messages
async def mqtt_check():
    global system_on
    while True:
        client.check_msg()
        await asyncio.sleep(0.1)



# Main loop
async def main():
    while True:
        if system_on:
            # Start tasks when system is on
            asyncio.create_task(breathe_led())
            asyncio.create_task(check_button())
            asyncio.create_task(check_accelerometer())
        await asyncio.sleep(1)

# Get the event loop and schedule tasks
loop = asyncio.get_event_loop()

# Schedule mqtt_check task
loop.create_task(mqtt_check())

# Start the loop and run forever
try:
    loop.run_forever()
except KeyboardInterrupt:
    print("Stopped by user")
finally:
    loop.close()
