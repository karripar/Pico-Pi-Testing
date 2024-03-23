from machine import Pin, I2C
from ssd1306 import SSD1306_I2C


sda_pin = 14
scl_pin = 15

i2c = I2C(1, scl=Pin(scl_pin), sda=(sda_pin))
oled = SSD1306_I2C(128, 64, i2c)

buttons = [Pin(pin, Pin.IN, Pin.PULL_UP) for pin in [7, 8, 9, 12]] #assign the pins

ufo_w = 24 #width # determine the ufo dimensions
ufo_h = 8 #height
ufo_x = (oled.width - ufo_w) / 2
ufo_y = (oled.height - ufo_h) 

while True:
    oled.fill(0)
    button_left = buttons[0].value()  # buttons used to control the ufo
    button_right = buttons[2].value()
    button_up = buttons[1].value()
    button_down = buttons[3].value()
    
    if button_left == 0 and ufo_x > 0: # press of a button moves the ufo on the y-, or x-axis
        ufo_x -= 1
        
    if button_right == 0 and ufo_x < (oled.width - ufo_w):
        ufo_x += 1
        
    if button_up == 0 and ufo_y < (oled.height - ufo_h):
        ufo_y += 1
        
    if button_down == 0 and ufo_y > 0:
        ufo_y -= 1
        
    oled.text("<=>", int(ufo_x), int(ufo_y)) # draws the ufo on the screen based on button-input
    oled.show()
    
