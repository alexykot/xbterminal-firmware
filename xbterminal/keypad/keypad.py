# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import time


button_last_pressed = None
cycle_index = -1
alphanum_char_index = 0
buttons_to_chars = {1: ('/', '%', '$', '&', '^', '*', '(', ')', '=', '-', '{', '}', '[', ']', ),
                    2: ('a', 'b', 'c', 'A', 'B', 'C', ),
                    3: ('d', 'e', 'f', 'D', 'E', 'F', ),
                    4: ('g', 'h', 'i', 'G', 'H', 'I', ),
                    5: ('j', 'k', 'l', 'J', 'K', 'L', ),
                    6: ('m', 'n', 'o', 'M', 'N', 'O', ),
                    7: ('p', 'q', 'r', 's', 'P', 'Q', 'R', 'S', ),
                    8: ('t', 'u', 'v', 'T', 'U', 'V', ),
                    9: ('w', 'x', 'y', 'z', 'W', 'X', 'Y', 'Z', ),
                    0: ('#', '!', '@', '.', ',', '\\', '~', '<', '>', '_', '+', ':', ';', ),
                    }

class keypad():
    def __init__(self, columnCount=3):
        GPIO.setmode(GPIO.BCM)

        # CONSTANTS 
        if columnCount is 3:
            self.KEYPAD = [
                [1,2,3],
                [4,5,6],
                [7,8,9],
                ["*",0,"#"]
            ]

            self.ROW         = [18,23,24,25]
            self.COLUMN      = [4,17,22]

        elif columnCount is 4:
            self.KEYPAD = [
                [1,2,3,"A"],
                [4,5,6,"B"],
                [7,8,9,"C"],
                [".",0,"#","D"]
            ]

            self.ROW         = [4,17,27,22]
            self.COLUMN      = [18,23,24,25]
        else:
            return
     
    def getKey(self):
         
        # Set all columns as output low
        for j in range(len(self.COLUMN)):
            GPIO.setup(self.COLUMN[j], GPIO.OUT)
            GPIO.output(self.COLUMN[j], GPIO.LOW)
         
        # Set all rows as input
        for i in range(len(self.ROW)):
            GPIO.setup(self.ROW[i], GPIO.IN, pull_up_down=GPIO.PUD_UP)
         
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
                GPIO.setup(self.COLUMN[j], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
         
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
        if colVal <0 or colVal >4:
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

        cycle_index = cycle_index + 1
        button_last_pressed = button_pressed

        return buttons_to_chars[button_pressed][cycle_index]

    def formAlphaNumString(self, current_string, button_pressed):
        global alphanum_char_index

        if button_pressed == 'D':
            alphanum_char_index = alphanum_char_index + 1
            return current_string

        if button_pressed == 'A':
            current_string = current_string[:-1]
            return current_string

        if button_pressed in ('B', 'C', '*', '#'):
            return current_string

        new_char = self.toAlphaNum(button_pressed)
        new_string = current_string[0:alphanum_char_index] + new_char

        return new_string

    def exit(self):
        # Reinitialize all rows and columns as input at exit
        for i in range(len(self.ROW)):
                GPIO.setup(self.ROW[i], GPIO.IN, pull_up_down=GPIO.PUD_UP) 
        for j in range(len(self.COLUMN)):
                GPIO.setup(self.COLUMN[j], GPIO.IN, pull_up_down=GPIO.PUD_UP)
