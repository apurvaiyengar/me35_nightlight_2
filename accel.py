import machine
import math
import asyncio
from machine import I2C, Pin, PWM 

class Acceleration:
    TAP_THRESHOLD = 10.0  # Define your threshold value for a tap

    def __init__(self, sda_pin, scl_pin, mqtt_client, indicator_pin):
        self.i2c = machine.I2C(0, scl=scl, sda=sda)
        self.client = mqtt_client
        self.indicator = machine.Pin(indicator_pin, machine.Pin.OUT)
        self.isTap = False
        self.connected = False
        if self.is_connected():
            print('connected')
            asyncio.create_task(self.write_byte(0x11,0)) #start data stream

    def is_connected(self):
        options = self.i2c.scan() 
        print(options)
        self.connected = self.addr in options
        return self.connected 

    async def read_accel(self):
        buffer = self.i2c.readfrom_mem(self.addr, 0x02, 6) # read 6 bytes starting at memory address 2
        await asyncio.sleep_ms(10)
        return struct.unpack('<hhh',buffer)

    async def write_byte(self, cmd, value):
        self.i2c.writeto_mem(self.addr, cmd, value.to_bytes(1,'little'))

    aasync def read_event(self):
        print('-------ACCEL.READ_EVENT CALLED-----')
        while True:
            try:
                data = await self.read_accel()
                mag = math.sqrt(data[0]**2 + data[1]**2 + data[2]**2)
                await asyncio.sleep(0.01)
            
                if mag > self.TAP_THRESHOLD:
                    print(f"Tap detected with magnitude: {mag}")
                    self.isTap = True
                    self.indicator.on()  # Turn on an indicator if necessary
                    await asyncio.sleep(0.05)
                    self.indicator.off()
                    self.client.publish("ME35-34/Apurva", "tapped")
            except Exception as e:
                print(f"Error in read_event: {e}")
            await asyncio.sleep(0.1)

    
