#only on ESP32
from machine import Pin, I2C
import ssd1306
import time

# Initialize I2C
i2c = I2C(
    0,
    scl=Pin(20),
    sda=Pin(22),
    freq=400000
)

# Initialize OLED
oled = ssd1306.SSD1306_I2C(128, 32, i2c, addr =0x3C)

def display_text(text):
    oled.fill(0)  # Clear the display
    oled.text(text, 0, 0)
    oled.show()
    
#display_text("Hello World")





