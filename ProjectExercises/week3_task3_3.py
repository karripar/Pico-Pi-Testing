from machine import Pin, PWM, I2C
from fifo import Fifo
import time
from ssd1306 import SSD1306_I2C
from filefifo import Filefifo

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

class Encoder:
    def __init__(self, rotary_a, rotary_b):
        self.a = Pin(rotary_a, Pin.IN, Pin.PULL_UP)
        self.b = Pin(rotary_b, Pin.IN, Pin.PULL_UP)
        self.fifo = Fifo(30, typecode = 'i')
        self.a.irq(handler=self.handler, trigger=Pin.IRQ_RISING, hard=True)
        
    def handler(self, pin):
        if self.b.value():
            self.fifo.put(-1)
        else:
            self.fifo.put(1)

# some classes copied from the led.py file 


i2c = I2C(1, scl=Pin(15), sda=Pin(14))
oled = SSD1306_I2C(128, 64, i2c)

encoder = Encoder(10, 11)  # Pins 10 and 11 for encoder button
button = Button(12)  # Pin 12 for button (not actually used here)

fifo_data = Filefifo(10, name='capture_250Hz_02.txt')
data = []
for _ in range(1000): # take 1000 values to go through
    line = fifo_data.get()
    if line:
        data.append(int(line))


# Find min and max values
min_value = min(data)
max_value = max(data)

# a window of 128 values
window_size = 128

# Function to update screen when scrolling
def update_screen(window_start): 
    oled.fill(0)
    oled.text("Min: {}".format(min_value), 0, 0) # had to study built-in format-methods because f-strings are too complicated apparently
    oled.text("Max: {}".format(max_value), 0, 10)
    for i in range(window_size):
        index = window_start + i
        if index < window_size: # take 128 samples
            value = data[index]
            oled.text("{}".format(value), 0, 20 + i * 10)
    oled.show()

window_start = 0 # index for list scrolling
update_screen(0)

while True:
    while encoder.fifo.has_data():
        turn = encoder.fifo.get()
        print(turn) # debugging using the rotary output value
        if turn > 0:  # Scroll down
            if window_start < window_size - 4: # prevent the scroll from going over the last item in the list plus some buffer 
                window_start += 1
                update_screen(window_start)
        elif turn < 0:  # Scroll up
            if window_start > 0:
                window_start -= 1
                update_screen(window_start)

    time.sleep_ms(20)  # Main loop delay, just because