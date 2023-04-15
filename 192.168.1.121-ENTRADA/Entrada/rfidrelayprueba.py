#!/usr/bin/env python

import RPi.GPIO as GPIO
import SimpleMFRC522
from squid import *
#from button import Button
import pickle

led = Squid(17, 18, 27)
#button = Button(5)
button = 5
#loop = Button(6)
loop = 6

GPIO.setmode(GPIO.BOARD)
GPIO.setup(button, GPIO.IN)
GPIO.setup(loop, GPIO.IN)

#GPIO.output(in1, False)
#GPIO.output(in2, False)

reader = SimpleMFRC522.SimpleMFRC522()

mode = 'LISTEN'
allowed_tags = []

def handle_listen_mode():
    global mode, allowed_tags
    led.set_color(GREEN)
    print('mode')
    
    id = reader.read_id_no_block()
    
    if GPIO.input(button):
    #if button.is_pressed():
        print("pressed")
    if button.is_released():
        print("release")
    if loop.is_pressed():
        print("loop")
        flash(RED, 5, 0.1)
    else :
        if id:
            
                print(id)
                flash(RED, 2, 0.1)
        
        
def unlock_door():
    print("Door UNLOCKED")
    flash(GREEN, 10, 0.5)
    print("Door LOCKED")
    
def flash(color, times, delay):
    for i in range(0, times):
        led.set_color(color)
        time.sleep(delay)
        led.set_color(OFF)
        time.sleep(delay) 
        

try:
    while True:
        if mode == "LISTEN":
            handle_listen_mode()
       
finally:
    print("cleaning up")
    GPIO.cleanup()
