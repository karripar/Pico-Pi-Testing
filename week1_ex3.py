from machine import Pin, I2C
from ssd1306 import SSD1306_I2C

sda_pin = 14
scl_pin = 15

i2c = I2C(1, scl=Pin(scl_pin), sda=Pin(sda_pin))
oled = SSD1306_I2C(128, 64, i2c) # OLED screen as a display

buttons = [Pin(pin, Pin.IN, Pin.PULL_UP) for pin in [7, 8, 9]] #determine pins on the board


x = 0
y = oled.height // 2 # start from the middle of the screen based on the y-axis

def draw(): # function to draw pixels
    oled.pixel(x, y, 1)
    oled.show()
    
while True:
    button_up = buttons[0].value() 
    button_down = buttons[2].value()
    button_reset = buttons[1].value()
        
    if button_up == 0:        
        y = max(0, y - 1)
    if button_reset == 0: # reset the screen and pixels drawn
        oled.fill(0)
        x = 0
        y = oled.height // 2
    if button_down == 0: # draw downwards on the screen
        y = min(oled.height -1, y + 1)
        
    draw()
    x += 1
    if x >= oled.width:  # when the exceeding the x-axis limit of the screen, return to the mirrored side = sketch loops back
        x = 0
        if y == oled.height - 1:
            y = 0
        