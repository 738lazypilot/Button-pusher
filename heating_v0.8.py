from machine import Pin, PWM, I2C
from utime import sleep
from ds1307 import DS1307
from pico_i2c_lcd import I2cLcd
import time, utime
from machine import Timer
import _thread
import os


global timer #timer variable
timer_var = Timer() #timer variable
global count # times enter button is pressed
count = 0
global up_button_count #times up or down button is pressed
up_button_count = 0
global day #day to next push
day = 0
#global now_date
#now_date = 0
global next_push_date
next_push_date = []
global hour_of_day # at what time the next push occurs
hour_of_day = 0

# some variables to work with the actual time and the target time to activate the sistem
global actual_date
global actual_hour
global actual_day
global actual_month

global target_hour
global target_day
global target_month


#Servo
servoPin = PWM(Pin(11)) #Servo pin declaration
servoPin.freq(50) #Sevo frequency set

def servo(degrees):
    # limit degrees beteen 0 and 180
    if degrees > 180: degrees=170 # safe range to operate
    if degrees < 20: degrees=20 #It should be zero, but due mechanical issues we change it to 20
    # set max and min duty
    maxDuty=9000
    minDuty=1000
    # new duty is between min and max duty in proportion to its value
    newDuty=minDuty+(maxDuty-minDuty)*(degrees/180)
    # servo PWM value is set
    servoPin.duty_u16(int(newDuty))

#RTC
i2c_rtc = I2C(1,scl = Pin(15),sda = Pin(14),freq = 100000) 

#LCD
i2c = I2C(0, sda=Pin(16), scl=Pin(17), freq=400000)
I2C_ADDR = i2c.scan()[0]
lcd = I2cLcd(i2c, I2C_ADDR, 2, 16)

#buttons
enter_button = machine.Pin(6, machine.Pin.IN, machine.Pin.PULL_DOWN)
up_button = machine.Pin(7, machine.Pin.IN, machine.Pin.PULL_DOWN)
down_button = machine.Pin(8, machine.Pin.IN, machine.Pin.PULL_DOWN)

def show_time ():  #get the time from the RTC module
    global now_date

    def month_name(month): #Translate the month number into letters
        global now_date

        if month == 1:
            return "Jan"
        elif month == 2:
            return "Feb"
        elif month == 3:
            return "Mar"
        elif month == 4:
            return "Apr"
        elif month == 5:
            return "May"
        elif month == 6:
            return "Jun"    
        elif month == 7:
            return "Jul"
        elif month == 8:
            return "Aug"
        elif month == 9:
            return "Sep"
        elif month == 10:
            return "Oct"
        elif month == 11:
            return "Nov"
        elif month == 12:
            return "Dec"

    rtc = DS1307(i2c_rtc)
    now_date = rtc.datetime() #get the date
    lcd_date = [] # create a list for the values we need

    lcd_date.insert(0,now_date[2])
    lcd_date.insert(1,month_name(now_date[1])) 

    return lcd_date


def month_name(month): #Translate the month number into letters
        global now_date

        if month == 1:
            return "Jan"
        elif month == 2:
            return "Feb"
        elif month == 3:
            return "Mar"
        elif month == 4:
            return "Apr"
        elif month == 5:
            return "May"
        elif month == 6:
            return "Jun"    
        elif month == 7:
            return "Jul"
        elif month == 8:
            return "Aug"
        elif month == 9:
            return "Sep"
        elif month == 10:
            return "Oct"
        elif month == 11:
            return "Nov"
        elif month == 12:
            return "Dec"

# Thread tha takes care of the LCD info shown and menu navigation

def show_lcd_thread():
    global count
    global up_button_count
    global next_push_date
    global hour_of_day
    
    old_up_button_count = up_button_count # keep track of the value 

    while True:
        try:
            if count == 0:              #If no user interaction, screen off
                lcd.clear()
                lcd.backlight_off()
                lcd.display_off()
                #if count !=0:
                    #break
                for i in range (20):   #listen for a button press
                    utime.sleep(1)
                    if count != 0:
                        break
            elif count == 1: #1 Push show the current info
                lcd.clear()
                lcd.display_on()
                lcd.backlight_on()
                lcd.putstr("Date " + str(show_time()) +"\nNext " + str(next_push_date[0:2]))
                for i in range(120):  #listen for a button press, keeping the message on the screen
                    utime.sleep(1)
                    if count != 1:
                        break
                    screen_off(i)
                    #elif i == 119:
                    #    count = 0
            elif count == 2: # After 2 pushes Let you choose the day for the activation
                next_push_date = []   #empties the list from previous info
                up_button_count = actual_date[2]  # Set the actual day on the screen 
                old_up_button_count = up_button_count #keep track of the value within the loop
                lcd.clear()
                lcd.putstr("Next Activation?\nDay: " + str(up_button_count))
                lcd.show_cursor()
                lcd.blink_cursor_on()
                for i in range(120):  #listen for a button press, keeping the message on the screen
                    utime.sleep(0.5)
                    if up_button_count != old_up_button_count:  #This refreshes the screen if there is a change
                        lcd_choose_day(up_button_count) # updates the info in the screen if there has been a change
                        old_up_button_count = up_button_count
                    if count != 2: 
                            break
                    screen_off(i)
                    
            elif count == 3:
                #lcd.clear()
                next_push_date.insert(0,up_button_count)  #saves the previous selection in a list for later use
                up_button_count = actual_date[1]
                old_up_button_count = up_button_count
                lcd.clear()
                lcd.putstr("Next Activation?\nMonth: " + str(month_name(up_button_count)))
                for i in range(120):
                    utime.sleep(0.5)
                    if up_button_count != old_up_button_count:
                        lcd_choose_month(month_name(up_button_count))
                        old_up_button_count = up_button_count
                    if count != 3: 
                            break
                    screen_off(i)

            elif count == 4:
                lcd.clear()
                next_push_date.insert(1,month_name(up_button_count))
                up_button_count = actual_date[4]
                old_up_button_count = up_button_count
                lcd.putstr("What time (H24):\n" + str(up_button_count) + ":00 Hours")
                for i in range(120):
                    utime.sleep(0.5)
                    if up_button_count != old_up_button_count:
                        lcd_choose_hour(up_button_count)                    
                        old_up_button_count = up_button_count
                    if count != 4: 
                            break
                    screen_off(i)
            elif count == 5: #After all selections, save the info and reset the count for new inputs from the user
                lcd.clear()
                lcd.blink_cursor_off()
                lcd.hide_cursor()            
                next_push_date.insert(2,up_button_count)
                lcd.putstr("Next activation:\n"+ str(next_push_date))
                create_action_backup() #saves the info in a text file just in case of losing ac power
                #print(next_push_date) #test
                #print('antes') #test
                for i in range (5):
                    utime.sleep(1)
                    count = 0
                    
                        
            elif count > 5: #If error or bounced button, count reset to zero
                count = 0
        
        except:
            machine.reset() #in case of an exception on execution, reset the system
        
def lcd_choose_day (day): #Cleaner way to display de info
    lcd.clear()
    lcd.putstr("Next Activation?\nDay: " + str(day))
    
def lcd_choose_month (month): #Cleaner way to display de info
    lcd.clear()
    lcd.putstr("Next Activation?\nMonth: " + str(month)) 

def lcd_choose_hour (hour): #Cleaner way to display de info
    lcd.clear()
    lcd.putstr("What time (H24):\n" + str(hour) + ":00 Hours")
    
def screen_off(i): #If screen is idle for too long without user input, screen off reseting the count
    global count
    if i == 119:
        count = 0
    
# button handlers for the 3 buttons
def button_enter(Pin): 
    global button_pushed
    global count

    count += 1
    button_pushed = True
    
def button_up(pin):
    global up_button_count

    up_button_count += 1
    #print("button up pushed")
    
def button_down(pin):
    global up_button_count
    
    up_button_count -=1
    #print("button down pushed")
    
def debounce_enter(pin):
    # Start or replace a timer for 200ms, and trigger on_pressed.
    timer_var.init(mode=Timer.ONE_SHOT, period=200, callback=button_enter)
    
def debounce_up(pin):
    # Start or replace a timer for 200ms, and trigger on_pressed.
    timer_var.init(mode=Timer.ONE_SHOT, period=200, callback=button_up)
    
def debounce_down(pin):
    # Start or replace a timer for 200ms, and trigger on_pressed.
    timer_var.init(mode=Timer.ONE_SHOT, period=200, callback=button_down)

# Start the LCD thread
_thread.start_new_thread(show_lcd_thread,())

# Set the buttons interruptions
enter_button.irq(debounce_enter, Pin.IRQ_RISING) #We only debounce the enter button as it is the critical one
up_button.irq(debounce_up, Pin.IRQ_RISING)
down_button.irq(debounce_down, Pin.IRQ_RISING)

# Create a file to store the next timed action in case ac power is lost
def create_action_backup():
    global next_push_date
    
    with open("next_action.txt","w") as filehandle:
        for list_item in next_push_date:
            filehandle.write('%s\n' % list_item)
    
# Recover the date for the next action from a txt file and format
# it as a list to be used
def read_action_backup():
    global next_push_date
    
    with open('next_action.txt','r') as filehandle:
        #print("in read action backup")
        #print (next_push_date)
        for line in filehandle:
            #remove linebreak which is the last character of the string
            current_place = line[:-1]
            if (current_place.isdigit()):
                #add item to the list
                next_push_date.append(int(current_place))
            else:
             #add item to the list
                next_push_date.append(current_place)
            #print(next_push_date)
            #print('despues')
            
if 'next_action.txt' in os.listdir():
    read_action_backup()
    

while True:
    try:
        #print("test")
        utime.sleep(1)
        #print(count)
        #print(up_button_count)
        #print(next_push_date)
        
    #calculate the date and extract the useful info in a list

        rtc = DS1307(i2c_rtc)
        actual_date  = rtc.datetime()
        short_actual_date = []
        short_actual_date.insert(0,actual_date[2]) #day
        short_actual_date.insert(1,month_name(actual_date[1])) #month    
        short_actual_date.insert(2,actual_date[4]) #hour
        
        #print(short_actual_date)#test
        #print(next_push_date)#test
        
        if next_push_date == short_actual_date:
            servo(46)
            utime.sleep(0.5)
            servo(0)
            utime.sleep(2)
            servo(46)
            utime.sleep(0.5)
            servo(0)
            next_push_date = []
            os.remove('next_action.txt')
        else:
            print("not great")
    
    except:
        machine.reset() #in case of an exception on execution, reset the system




