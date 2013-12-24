import Adafruit_BBIO.GPIO as GPIO


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

class keypad():
    def __init__(self):

        global pins

        # self.KEYPAD = {17: 1,
        #                49: 2,
        #                81: 3,
        #                18: 4,
        #                50: 5,
        #                82: 6,
        #                20: 7,
        #                52: 8,
        #                84: 9,
        #                56: 0,
        #                145: 'A',
        #                146: 'B',
        #                148: 'C',
        #                152: 'D',
        #                88: '#',
        #                24: '*',
        #                 }
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

