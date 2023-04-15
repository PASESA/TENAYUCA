import RPi.GPIO as GPIO
import SimpleMFRC522
import os

reader = SimpleMFRC522.SimpleMFRC522()
buffor = 0

while continue_reading:
    try:
        id, text = reader.read()
        if(buffor != id):
                print (id)
                udp_send(id) 
                buffor = id
    finally:
            time.sleep(0.5)
