import time
import utime
import uselect
import machine
import sys
from sys import stdin, stdout
from machine import I2C, Pin, UART
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd


I2C_ADDR     = 39
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

i2c = I2C(0, sda=machine.Pin(0), scl=machine.Pin(1), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)
resetLetterAddress = 0
nextRowCol = 0
curMenu = 0
curTask = 0
#taskDisplayMode is of the types LOOP, MANUAL, and AUTO
taskDisplayMode = 'LOOP'
button1 = Pin(16, Pin.IN, Pin.PULL_UP)
builtInLed = Pin(25, Pin.OUT)
tasks = []

def displayIntro():
    lcd.clear()
    lcd.move_to(2,0)
    lcd.putstr('Google Tasks')
    lcd.move_to(6,1)
    lcd.putstr('Pico')
    lcd.move_to(15,1)
    lcd.putchar(chr(6))

def displayGettingTasks():
    lcd.clear()
    lcd.move_to(0,0)
    lcd.putstr('Getting Tasks')
    lcd.move_to(0,1)
    lcd.putstr('Please Wait...')

def displayTasks(tasks):
    lcd.clear()
    lcd.move_to(0,0)
    lcd.putstr('Tasks: ' + str(curTask + 1) + ' of ' + str(len(tasks)))
    lcd.move_to(0,1)
    lcd.putstr(tasks[0])

def displayNextTask(tasks,curTask):
    lcd.clear()
    lcd.move_to(0,0)
    lcd.putstr('Tasks: ' + str(curTask + 1) + ' of ' + str(len(tasks)))
    lcd.move_to(0,1)
    lcd.putstr(tasks[curTask])

def read_until_end():
    builtInLed.toggle()
    received_lines = []
    while True:
        line = sys.stdin.readline()  # Read a line from stdin
        if not line:
            continue  # If no line is received, continue the loop
        line = line.strip()  # Remove leading and trailing whitespace
        if line == "end":
            break  # Stop reading if 'end' is encountered
        received_lines.append(line)
    builtInLed.toggle()
    return received_lines

def getTasks():
    #read the task list title form the stdin
    #first by writing the command to the stdin to retreive tasks
    print('getTasks')
    #wait for the response from the pico
    time.sleep(1)
    print('finished sleep')
    print("Ready")
    #read the response from the pico
    # while there are lines in the std in read all the lines from the stdin
    tasks = []
    #read the tasks from the pico
    tasks = read_until_end()

    # select_result = uselect.select([stdin], [], [], 0)
    # if(select_result != None):
    #     while select_result[0]:
    #         input_character = stdin.readline().rstrip()
    #         print(input_character)
    #         #also print the character back to the stdout
    print("over here")
    if(tasks == []):
        tasks = ['No Tasks']
    return tasks
    #return ['Task 1', 'Task 2', 'Task 3', 'Task 4', 'Task 5']

def customcharacter():
    
  #character      
  lcd.custom_char(0, bytearray([
  0x0E,
  0x0E,
  0x04,
  0x1F,
  0x04,
  0x0E,
  0x0A,
  0x0A
        
        ]))
  
    #character2      
  lcd.custom_char(1, bytearray([
    0x1F,
  0x15,
  0x1F,
  0x1F,
  0x1F,
  0x0A,
  0x0A,
  0x1B
        
        ]))
  
  
  
  
  #smiley
  lcd.custom_char(2, bytearray([
  0x00,
  0x00,
  0x0A,
  0x00,
  0x15,
  0x11,
  0x0E,
  0x00
        
        ]))
  
  #heart
  lcd.custom_char(3, bytearray([
   0x00,
  0x00,
  0x0A,
  0x15,
  0x11,
  0x0A,
  0x04,
  0x00
        
        ]))
  
      #note
  lcd.custom_char(4, bytearray([
   0x01,
  0x03,
  0x05,
  0x09,
  0x09,
  0x0B,
  0x1B,
  0x18
        
        ]))
    #celcius
  lcd.custom_char(5, bytearray([
  0x07,
  0x05,
  0x07,
  0x00,
  0x00,
  0x00,
  0x00,
  0x00
        
        ]))
    #Checkmark
  lcd.custom_char(6, bytearray([
  0x08,
  0x0C,
  0x0E,
  0x0F,
  0x0F,
  0x0E,
  0x0C,
  0x08
  ]))

def navUI(irq):
    global curMenu
    global curTask
    global tasks
    print('tasks: ' + str(tasks))
    if(tasks == []):
        displayGettingTasks()
        tasks = getTasks()
        displayTasks(tasks)
        curMenu = 1
        return
        
    #tasks = ['Task 1', 'Task 2', 'Task 3', 'Task 4', 'Task 5']
    # if the button1 is pressed then
    # ............. move right in the menus
    if(irq == button1):
        if(curMenu == 0):
            curMenu = 1
            displayTasks(tasks)
        elif(curMenu == 1):
            if(curTask < len(tasks)):
                displayNextTask(tasks,curTask)
            if(curTask < len(tasks)):
                curTask += 1
            else:
                curTask = 0
        print('button1 pressed')
        time.sleep(0.3)

displayIntro()

def main():
    customcharacter()
    #if(curMenu == 0):
        
    while True:
        button1.irq(trigger=Pin.IRQ_FALLING, handler=navUI)

##execute main
if __name__ == '__main__':
    main()