import board
import busio
import time
import adafruit_character_lcd.character_lcd_rgb_i2c as character_lcd

lcd_columns = 16
lcd_rows = 2

i2c = board.I2C()
lcd = character_lcd.Character_LCD_RGB_I2C(i2c, lcd_columns, lcd_rows)

def intro():
    j = 3
    for i in range(3):
        lcd.message = "Light show in:\n%s" % j
        time.sleep(1)
        j -= 1

def show():
    # Scroll to the left
    for i in range(3):
        lcd.clear()
        lcd.color = [100, 0, 0]
        lcd.message = "Marenn"
        for i in range(16):
            time.sleep(0.5)
            lcd.move_right()
        lcd.clear()
        lcd.color = [0, 100, 0]
        lcd.message = "loves"
        for i in range(16):
            time.sleep(0.5)
            lcd.move_right()
        lcd.clear()
        lcd.color = [0, 0, 100]
        lcd.message = "cows"
        for i in range(16):
            time.sleep(0.5)
            lcd.move_right()
        time.sleep(1)

lcd.color = [20, 20, 20]
intro()
show()
lcd.color = [0, 0, 0]
lcd.clear()

