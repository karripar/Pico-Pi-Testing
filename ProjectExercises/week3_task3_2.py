from machine import Pin, PWM, I2C
from fifo import Fifo
import time
from ssd1306 import SSD1306_I2C

# Led- and Encoder-class not created by me, provided by teacher/school. 
class Led:
    """Dimmable LED class that implements the same interface as Pin (GPIO pin class).
    Adds method brightness() that is used to set brightness of the LED on state.
    Brightness is specified as a percentage in range 0.5 - 100%. Values exceeding the
    range are capped to range limits.
    """
    def __init__(self, pin, mode=Pin.OUT, brightness=1, value=None):
        # mode can only be Pin.OUT
        # It is defined only to keep the interface compatible with the Pin class
        if mode != Pin.OUT:
            raise RuntimeError('Pin.OUT is the only allowed value for Led mode')
        self._pin = Pin(pin, Pin.OUT)
        self._pwm = PWM(self._pin)
        self._pwm.freq(1000)
        self.brightness(brightness)
        if value is not None:
            self.value(value)

    def on(self):
        self._pwm.duty_u16(self._on_val)

    def off(self):
        self._pwm.duty_u16(0)

    def low(self):
        self.off()

    def high(self):
        self.on()

    def toggle(self):
        if self._pwm.duty_u16():
            self.off()
        else:
            self.on()

    def __call__(self, *args):
        return self.value(*args)

    def value(self, *args):
        if len(args) > 1:
            raise TypeError("Too many arguments. Only one argument allowed")
        elif len(args):
            if args[0]:
                self.on()
            else:
                self.off()
        else:
            if self._pwm.duty_u16():
                return 1
            else:
                return 0

    def brightness(self, brightness):
        brightness = min(100, max(0.5, brightness))  # limit val to range [0.5-100]
        self._on_val = int(65535 * brightness / 100)
        if self._pwm.duty_u16():
            self.on()

class Button:
    def __init__(self, pin):
        self.pin = Pin(pin, Pin.IN, Pin.PULL_UP)
        self.last_state = self.pin.value()
        self.last_change_time = time.ticks_ms()

    def pressed(self):
        current_state = self.pin.value()

        if current_state != self.last_state:
            time.sleep_ms(50)
            self.last_change_time = time.ticks_ms()
            self.last_state = current_state

        elif time.ticks_diff(time.ticks_ms(), self.last_change_time) > 20:
            time.sleep_ms(50)
            if current_state == 0:  # Button is pressed
                return True

        return False

# Encoder class also from school provided content
class Encoder:
    def __init__(self, rotary_a, rotary_b):
        self.a = Pin(rotary_a, Pin.IN, Pin.PULL_UP)
        self.b = Pin(rotary_b, Pin.IN, Pin.PULL_UP)
        self.fifo = Fifo(30)
        self.a.irq(handler=self.handler, trigger=Pin.IRQ_RISING, hard=True)
        
    def handler(self, pin):
        if self.b.value():
            self.fifo.put(-1)
        else:
            self.fifo.put(1)
            

i2c = I2C(1, scl=Pin(15), sda=Pin(14))
oled = SSD1306_I2C(128, 64, i2c)

led1 = Led(20)  # Pin 20 as LED1
led2 = Led(21)  # Pin 21 as LED2
led3 = Led(22)  # Pin 22 as LED3

encoder = Encoder(10, 11)  # Pins 10 and 11 for encoder button
button = Button(12)  # Pin 12 for button

menu_items = [led1, led2, led3]
selection = 0
led_state = "OFF"


def update_screen(selection, led_state): # update selector position and led-state
    oled.fill(0)
    for i, led in enumerate(menu_items):
        if i == selection:
            oled.text("-> LED" + str(i + 1)+ " "+led_state, 0, i * 16)
            oled.show()
        else:
            oled.text("LED" + str(i + 1), 0, i * 16)
            oled.show()
            

update_screen(selection, led_state)

while True:
    if button.pressed():
        menu_items[selection].toggle()
        time.sleep_ms(50)  # Button debounce 

    while encoder.fifo.has_data(): # logic for moving the cursor/selector
        turn = encoder.fifo.get()
        if turn > 0: 
            time.sleep_ms(50)
            selection = (selection + 1) % len(menu_items)
        else:
            time.sleep_ms(50)
            selection = (selection - 1) % len(menu_items)
        
        if menu_items[selection].value(): # update led state on screen
            led_state = "ON"
        else:
            led_state = "OFF"

        update_screen(selection, led_state)

    time.sleep_ms(20)  # Main loop delay, because why not
