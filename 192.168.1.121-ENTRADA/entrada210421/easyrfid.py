#import RPi.GPIO as GPIO

import RPi.GPIO as io
import time
loop = 5
boton = 6
in3 = 13                      # en las variables in1, in2, in3
barrera = 17
out1 = 22
out2 = 18
out3 = 27                    # en las variables out1, out2
io.setmode(io.BCM)              # modo in/out pin del micro
io.setwarnings(False)           # no señala advertencias de pin ya usados
io.setup(loop,io.IN)             # configura en el micro las entradas
io.setup(boton,io.IN)             # configura en el micro las entradas
io.setup(in3,io.IN)             # configura en el micro las entradas
io.setup(barrera,io.OUT)           # configura en el micro las salidas
io.setup(out1,io.OUT)           # configura en el micro las salidas
io.setup(out2,io.OUT)
io.setup(out3,io.OUT)  
line=''
io.output(barrera,0)
io.output(out1,0)
io.output(out2,0)
io.output(out3,0)

while True:
        if io.input(loop):
                
                io.output(out1,1)
                print("no HAY Auto")                
        else:
                
                io.output(out1,0)                
                print("SI HAY Auto")              

               
                time.sleep (1)
                import SimpleMFRC522
                reader = SimpleMFRC522.SimpleMFRC522()
                id = reader.read_id_no_block()
                if id:
                        print(id)
                        time.sleep(1)
                        break
                                                                      
                if io.input(boton):
                        print("relesead boton")
                        io.output(out2,1)
                                          #io.output(barrera,0)
                else:
                        print("pressed boton")
                        io.output(out2,0)
                                                                  
 
