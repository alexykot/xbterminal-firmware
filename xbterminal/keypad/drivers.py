# -*- coding: utf-8 -*-
import time
GPIO = None

class keypadDriverRPi():
    def __init__(self):
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)

        self.KEYPAD = [
            [1,2,3,"A"],
            [4,5,6,"B"],
            [7,8,9,"C"],
            [".",0,"#","D"]
        ]

        self.ROW         = [4,17,27,22]
        self.COLUMN      = [18,23,24,25]

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

    def exit(self):
        # Reinitialize all rows and columns as input at exit
        for i in range(len(self.ROW)):
                GPIO.setup(self.ROW[i], GPIO.IN, pull_up_down=GPIO.PUD_UP) 
        for j in range(len(self.COLUMN)):
                GPIO.setup(self.COLUMN[j], GPIO.IN, pull_up_down=GPIO.PUD_UP)


class keypadDriverBBB():
    def __init__(self):
        global GPIO
        import Adafruit_BBIO.GPIO as GPIO

        pins = {
                'pin1': "P8_14",
                'pin2': "P8_16",
                'pin3': "P8_11",
                'pin4': "P8_10",
                'pin5': "P8_7",
                'pin6': "P8_9",
                'pin7': "P8_26",
                'pin8': "P8_8",
        }
        self.KEYPAD = {17: 1,
                       18: 2,
                       20: 3,
                       49: 4,
                       50: 5,
                       52: 6,
                       81: 7,
                       82: 8,
                       84: 9,
                       146: 0,
                       24: 'A',
                       56: 'B',
                       88: 'C',
                       152: 'D',
                       145: '*',
                       148: '#',
                        }
        self.ROW = [pins['pin8'], pins['pin7'], pins['pin6'], pins['pin5']]
        self.COLUMN = [pins['pin4'], pins['pin3'], pins['pin2'], pins['pin1']]

    def getKey(self):
        bits_list = [0,0,0,0,0,0,0,0]
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
                bits_list[7-i] = 1

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
                bits_list[3-j] = 1

        # if colVal is not 0 thru 2 then no button was pressed and we can exit
        if colVal <0 or colVal >3:
            self.exit()
            return

        for key, val in enumerate(bits_list):
            bits_list[key] = str(val)
        binary_str = ''.join(bits_list)
        binary_str = '0b'+binary_str
        keynum = int(binary_str, 2)
        try:
            key = self.KEYPAD[keynum]
        except KeyError:
            key = None

        # Return the value of the key pressed
        self.exit()
        return key

    def exit(self):
        # Reinitialize all rows and columns as input at exit
        for i in range(len(self.ROW)):
                GPIO.setup(self.ROW[i], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        for j in range(len(self.COLUMN)):
                GPIO.setup(self.COLUMN[j], GPIO.IN, pull_up_down=GPIO.PUD_UP)

