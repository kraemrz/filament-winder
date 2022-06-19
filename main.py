from machine import Pin, I2C, PWM
from utime import sleep
from lcd_api import LcdApi
from i2c_lcd import I2cLcd
import _thread
import stepper_motor
import speaker

# PIN SETUP
#speaker=Pin9
#IN4 = Pin10
#IN3 = Pin11
#IN2 = Pin12
#IN1 = Pin13
left_btn = Pin(14, Pin.IN, Pin.PULL_DOWN)
right_btn = Pin(15, Pin.IN, Pin.PULL_DOWN)
reset_btn = Pin(15, Pin.IN, Pin.PULL_DOWN)
one_turn_sensor = Pin(17, Pin.IN, Pin.PULL_DOWN)
reset_led = Pin(18, Pin.OUT)
winder_motor_sensor = Pin(19, Pin.IN)
winder_motor_relay = Pin(20, Pin.OUT)

# SCREEN SETUP
I2C_ADDR     = 0x27
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)

# VARIBLES
menu = ("Set max steps", "Steps/revolution", "Test winder", "Save")
number_steps = 35 # SETS MAX RIGHT POSITION OF STEPPER (MENU 0)
steps_per_turn = 4 # SETS HOW MANY STEPS STEPPER MAKES AFTER 1 TURN (MENU 1)
spare  = 0 # spare
LCD_pos = 3 # KEEPS TRACK OF POSITION IN LCD DISPLAY
save = 0 # SAVE PARAMETERS
stop = 0 # EXIT BACK TO PARAMETERS
list_pos = 2
spool_size = [36, 56, 76, 200]# 500g, 750g, 1000g, 3000g SPOOL

def LCD_text_update(pos0, pos1, row1, pos3, pos4, row2):
    lcd.clear()
    lcd.move_to(pos0, pos1)
    lcd.putstr(row1)
    lcd.move_to(pos3, pos4)
    lcd.putstr(row2)
    
LCD_text_update(0, 0, "Main menu:", 0, 1, "Click down btn")

# MOVES DOWN IN LCD MENU        
def menu_down(LCD_pos):
    if LCD_pos == 0:
        LCD_text_update(0, 0, '>'+menu[LCD_pos], 0, 1,  menu[LCD_pos+1])
        LCD_pos+=1
        sleep(0.3)
    elif LCD_pos == 1:
        LCD_text_update(0, 0, '>'+menu[LCD_pos], 0, 1,  menu[LCD_pos+1])
        LCD_pos+=1
        sleep(0.3)
    elif LCD_pos == 2:
        LCD_text_update(0, 0, '>'+menu[LCD_pos], 0, 1,  menu[LCD_pos+1])
        LCD_pos += 1
        sleep(0.3)
    elif LCD_pos == 3:
        LCD_text_update(0, 0, '>'+menu[LCD_pos], 0, 1,  menu[0])
        LCD_pos = 0
        sleep(0.3)

# DISPLAYS NUMBER OF STEPS (MENU 0)
# CHANGE TO SIZE OF SPOOL, 0.5KG, 1KG, 3KG SPOOL
def stepper_steps(number_steps):
    if number_steps == spool_size[0]:
        LCD_text_update(2, 0, "Spool size:", 2, 1, "0.5kg spool")
    elif number_steps == spool_size[1]:
        LCD_text_update(2, 0, "Spool size:", 2, 1, "0.75kg spool")
    elif number_steps == spool_size[2]:
        LCD_text_update(2, 0, "Spool size:", 2, 1, "1.0kg spool")
    elif number_steps == spool_size[3]:
        LCD_text_update(2, 0, "Spool size:", 2, 1, "3.0kg spool")

# DISPLAYS HOW MANY STEPS EACH TURN (MENU 1)
def steps_per_rev(steps_per_turn):
    stp_trn = str(steps_per_turn)+" /rev"
    LCD_text_update(0, 0, "steps/rev:", 4, 1, stp_trn)
    
# RUNS WINDER MOTOR IN TEST MODE CONTINUOUSLY (MENU 2)
def start_winder_motor():
    LCD_text_update(2, 0, "start relay", 2, 1, "for winder")

def winder_motor_test():
    stop = 0
    while stop == 0:
        if left_btn.value() == 0:
            LCD_text_update(2, 0, "start", 2, 1, "winder")
            continue
        elif left_btn.value() == 1:
            stop = 1
            LCD_text_update(2, 0, "stop relay", 2, 1, "for winder")
           
def winder():
    while True:    
        if winder_motor_sensor.value():
            winder_motor_relay.value(1)
            sleep(0.5)# CHANGE TO 5
            winder_motor_relay.value(0)

_thread.start_new_thread(winder, ())

while save == 0:

    if left_btn.value():
        if LCD_pos == 3:
            LCD_pos = 0
        else:
            LCD_pos+=1
        menu_down(LCD_pos)
    
    if reset_btn.value():
        
        # MENU 0
        if LCD_pos == 0:
            if list_pos == 3:
                list_pos = 0
            else:
                list_pos+=1
            stepper_steps(spool_size[list_pos])
            sleep(0.3)
        
        # MENU 1    
        elif LCD_pos == 1:
            sleep(0.3)
            steps_per_rev(steps_per_turn)
        
        #MENU 2
        elif LCD_pos == 2:
            winder_motor_test()
        
        #MENU 3 (SAVE)
        elif LCD_pos == 3:
            
            speaker.starts()
            save = 1
            stop = 0            
            LCD_text_update(4, 0, "Running", 4, 1, "program")
            counter = 0
            while stop == 0:
                if one_turn_sensor.value() == 0:
                    if counter != number_steps:
                        while counter != number_steps:
                            if one_turn_sensor.value() == 0:
                                print('sensor påverkad counting up')
                                stepper_motor.right(steps_per_turn)
                                counter+=steps_per_turn
                                cnt_stp = "Cnt: "+str(counter) + " stp: " + str(number_steps)
                                LCD_text_update(0, 0, "STARTED", 0, 1, cnt_stp)
                                sleep(0.5) # CHANGE TO 5
                            elif reset_btn.value():
                                save = 0
                                counter = number_steps
                                print("STOPP")
                                LCD_text_update(0, 0, "STOP", 0, 0, "STOPP")
                                speaker.stops()
                                sleep(0.3)
                                LCD_text_update(0, 0, "Main menu:", 0, 0, "Click down btn")
                                stop = 1
                            else:
                                continue
                    elif counter == number_steps:
                        while counter != 0:#
                            if one_turn_sensor.value() == 0:
                                print('sensor påverkad counting down')
                                stepper_motor.left(steps_per_turn)
                                counter-=steps_per_turn
                                cnt_stp = "Cnt: "+str(counter) + " stp: " + str(number_steps)
                                LCD_text_update(0, 0, "STARTED", 0, 1, cnt_stp)
                                sleep(0.5) # CHANGE TO 5
                            elif reset_btn.value():
                                counter = 0
                                save = 0
                                print("STOPP")
                                LCD_text_update(0, 0, "STOP", 0, 0, "STOPP")
                                speaker.stops()
                                sleep(0.3)
                                LCD_text_update(0, 0, "Main menu:", 0, 0, "Click down btn")
                                stop = 1
                            else:
                                continue
            
        # MENU 4
        elif LCD_pos == 4:
            pass