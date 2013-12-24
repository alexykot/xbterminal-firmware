__author__ = 'tux'

import Adafruit_BBIO.GPIO as GPIO
import time


button_last_pressed = None
cycle_index = None
buttons_to_chars = {1: ('/', '%', '$', '&', '^', '*', '(', ')', '=', '-', '{', '}', '[', ']',),
                    2: ('a', 'b', 'c', 'a', 'b', 'c',),
                    3: ('d', 'e', 'f', 'd', 'e', 'f',),
                    4: ('g', 'h', 'i', 'g', 'h', 'i',),
                    5: ('j', 'k', 'l', 'j', 'k', 'l',),
                    6: ('m', 'n', 'o', 'm', 'n', 'o',),
                    7: ('p', 'q', 'r', 's', 'p', 'q', 'r', 's',),
                    8: ('t', 'u', 'v', 't', 'u', 'v',),
                    9: ('w', 'x', 'y', 'z', 'w', 'x', 'y', 'z',),
                    0: ('#', '!', '@', '.', ',', '\\', '~', '<', '>', '_', '+', ':', ';',),
                    }

class keypad():
    def __init__(self, columnCount = 4):

        # Define pins to use for 3x4 Keypad
        pin1 = "P8_14"
        pin2 = "P8_16"
        pin3 = "P8_11"
        pin4 = "P9_13"
        pin5 = "P9_12"
        pin6 = "P9_26"
        pin7 = "P9_11"
        pin8 = "P9_24"

        # CONSTANTS
        if columnCount is 3:
            self.KEYPAD = [
                [1,2,3],
                [4,5,6],
                [7,8,9],
                ["*",0,"#"]
            ]

            self.ROW         = [pin7, pin6, pin5, pin4]
            self.COLUMN      = [pin3, pin2, pin1]

        elif columnCount is 4:
            self.KEYPAD = [
                [1,2,3,"A"],
                [4,5,6,"B"],
                [7,8,9,"C"],
                ["*",0,"#","D"]
            ]

            self.ROW         = [pin8, pin7, pin6, pin5]
            self.COLUMN      = [pin4, pin3, pin2, pin1]
        else:
            return

    def getKey(self):
        # Set all columns as output low
        for j in range(len(self.COLUMN)):
            GPIO.setup(self.COLUMN[j], GPIO.OUT)
            GPIO.output(self.COLUMN[j], GPIO.LOW)

        # Set all rows as input
        for i in range(len(self.ROW)):
            GPIO.setup(self.ROW[i], GPIO.IN, GPIO.PUD_DOWN)

        # Scan rows for pushed key/button
        # A valid key press should set "rowVal"  between 0 and 3.
        rowVal = -1
        for i in range(len(self.ROW)):
            tmpRead = GPIO.input(self.ROW[i])
            if tmpRead == 0:
                rowVal = i

        # if rowVal is not 0 thru 3 then no button was pressed and we can exit
        if rowVal <0 or rowVal >4:
            self.exit()
            return

        # Convert columns to input
        for j in range(len(self.COLUMN)):
                GPIO.setup(self.COLUMN[j], GPIO.IN, GPIO.PUD_DOWN)

        # Switch the i-th row found from scan to output
        GPIO.setup(self.ROW[rowVal], GPIO.OUT)
        GPIO.output(self.ROW[rowVal], GPIO.HIGH)

        # Scan columns for still-pushed key/button
        # A valid key press should set "colVal"  between 0 and 2.
        colVal = -1
        for j in range(len(self.COLUMN)):
            tmpRead = GPIO.input(self.COLUMN[j])
            if tmpRead == 1:
                colVal=j

        # if colVal is not 0 thru 2 then no button was pressed and we can exit
        if colVal <0 or colVal >2:
            self.exit()
            return

        # Return the value of the key pressed
        self.exit()
        return self.KEYPAD[rowVal][colVal]


    #this allows to use numeric keypad to enter digits, upper and lower letters and special chars
    def toAlphaNum(self, button_pressed):
        global button_last_pressed, cycle_index, buttons_to_chars

        if button_pressed not in buttons_to_chars:
            return button_pressed

        if button_pressed != button_last_pressed or cycle_index+1 == len(buttons_to_chars[button_pressed]):
            cycle_index = -1

        cycle_index = cycle_index

        return buttons_to_chars[button_pressed][cycle_index]


    def exit(self):
        # Reinitialize all rows and columns as input at exit
        for i in range(len(self.ROW)):
                GPIO.setup(self.ROW[i], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        for j in range(len(self.COLUMN)):
                GPIO.setup(self.COLUMN[j], GPIO.IN, pull_up_down=GPIO.PUD_UP)


if __name__ == '__main__':
    # Initialize the keypad class
    kp = keypad()

    # Loop while waiting for a keypress
    digit = None
    while True:
        digit = kp.getKey()
        print digit
        time.sleep(1)


