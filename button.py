import machine
import neopixel
import asyncio

class Button:
    def __init__(self, pin, neopixel_pin, buzzer_pin):
        self.button = machine.Pin(pin, machine.Pin.IN)
        self.led = neopixel.NeoPixel(machine.Pin(neopixel_pin), 1)
        self.buzzer = machine.PWM(machine.Pin(buzzer_pin, machine.Pin.OUT))
        self.buzzer.freq(440)
        self.on_color = (40, 0, 0)  # RGB color for "on"
        self.off_color = (0, 0, 0)  # RGB color for "off"
    
    async def check_and_update(self):
        if not self.button.value():
            self.led[0] = self.on_color
            self.led.write()
            self.buzzer.duty_u16(1000)  # Activate buzzer
            await asyncio.sleep(0.1)  # Duration of the buzz
            self.buzzer.duty_u16(0)    # Deactivate buzzer
        else:
            self.led[0] = self.off_color
            self.led.write()
