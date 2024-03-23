from machine import Pin, I2C, PWM
from ssd1306 import SSD1306_I2C
import random
import time

SDA_PIN = 14  
SCL_PIN = 15  


i2c = I2C(1, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN)) 
oled = SSD1306_I2C(128, 64, i2c)

led_pins = [Pin(pin, Pin.OUT) for pin in [20, 21, 22]] # determine the pins

button = Pin(12, Pin.IN, Pin.PULL_DOWN)

words = ["Party!", "Now!", "Yes!", "Bomboclat!", "Crazy!", "Go!", "Let's go!", "DAMN!", "STFU!" ] # words displayed on the OLED screen


def debounce(pin):
    cur_state = pin.value() # store the current state of the pins and inputs
    utime.sleep_ms(10)
    return pin.value() == cur_state


def spam():
    
    spam_mode = False
    last_state = False
    
    while True:
        
        if debounce(button):
            last_state = not last_state
            spam_mode = last_state
            
        if spam_mode:
            oled.fill(0)
            oled.text(random.choice(words), 45, 30, 1) # randomly choose a word to display and refresh the screen
            oled.show()
        
            for _ in range(10): # spam the led-lights with a short delay, blinding the user because why not
                led_pin = random.choice(led_pins)
                led_pin.value(1)
                time.sleep_ms(random.randint(30, 100))
                led_pin.value(0)
                time.sleep_ms(random.randint(30, 100))
                oled.text(random.choice(words), 0, 1)
        
        else:
            oled.fill(0) # 
            oled.show()
            
            for led_pin in led_pins:
                led_pin.value(0)
        
    
            
spam()
