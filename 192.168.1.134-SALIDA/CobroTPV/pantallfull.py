from datetime import datetime, date
from tkinter import messagebox as mb
from tkinter import *
import tkinter as tk
import operacion
#import subprocess


class Fullscreen_Example:
    def __init__(self):
        
        self.operacion1=operacion.Operacion()    
        self.window = tk.Tk()
        self.window.title("Registro Inicio de Turno")        
        self.window.attributes('-fullscreen', True)  
        self.fullScreenState = False
        self.window.bind("<F11>", self.toggleFullScreen)
        self.window.bind("<Escape>", self.quitFullScreen)
        self.labelframe1=tk.LabelFrame(self.window, text="Inicio de Turno")
        self.labelframe1.grid(column=1, row=0, padx=0, pady=0)
        #self.Adentroframe=tk.LabelFrame(self.window, text="Autos DENTRO")
        #self.Adentroframe.grid(column=2, row=0, padx=0, pady=0)
        self.Nombre=tk.StringVar()
        self.entryNombre=tk.Entry(self.labelframe1, width=10, textvariable=self.Nombre)#, state="readonly")
        self.entryNombre.grid(column=1, row=0, padx=4, pady=4)
        self.Contraseña=tk.StringVar()
        self.entryContraseña=tk.Entry(self.labelframe1, width=10, textvariable=self.Contraseña, show=
        "*", justify=tk.RIGHT)
        self.entryContraseña.grid(column=1, row=1, padx=4, pady=4)
        self.Turno=tk.StringVar()
        self.entryTurno=tk.Entry(self.labelframe1, width=10, textvariable=self.Turno)#, state="readonly")
        self.entryTurno.grid(column=1, row=2, padx=4, pady=4)                
        self.lblNombre=tk.Label(self.labelframe1, text="Nombre")
        self.lblNombre.grid(column=0, row=0, padx=0, pady=0)
        self.lblContraseña=tk.Label(self.labelframe1, text="Contraseña")
        self.lblContraseña.grid(column=0, row=1, padx=0, pady=0)
        self.lblTurno=tk.Label(self.labelframe1, text="Turno")
        self.lblTurno.grid(column=0, row=2, padx=0, pady=0)
        self.lblHorario1=tk.Label(self.labelframe1, text="1 ero de 7am a 3 pm.")
        self.lblHorario1.grid(column=2, row=0, padx=0, pady=0)
        self.lblHorario2=tk.Label(self.labelframe1, text="2 o de 3pm a 10 pm.")
        self.lblHorario2.grid(column=2, row=1, padx=0, pady=0)
        self.lblHorario3=tk.Label(self.labelframe1, text="3 ero de 10pm a 7 am.")
        self.lblHorario3.grid(column=2, row=2, padx=0, pady=0)
        self.lblValidar=tk.Label(self.labelframe1, text="Valido/Invalido")
        self.lblValidar.grid(column=1, row=3, padx=0, pady=0)
        self.boton1=tk.Button(self.labelframe1, text="Salir ", command=self.quitF, width=10, height=1, anchor="center", background="red")
        self.boton1.grid(column=2, row=3, padx=4, pady=4)
        self.boton2=tk.Button(self.labelframe1, text="Entrar", command=self.abrirPrograma, width=10, height=1, anchor="center", background="green")
        self.boton2.grid(column=0, row=3, padx=4, pady=4)                                                                                                                                
        self.window.mainloop()
        
    def abrirPrograma(self):
        usuario = str(self.Nombre.get(), )   
        contrasena = str(self.Contraseña.get(), )
        turno = str(self.Turno.get(), )
        inicio = datetime.today()
        ##Validar que los campós no esten vacios
        ##Obtener datos del usuario, validamos usuario y contrasena
        if ((len(contrasena) == 0) or (len(usuario) == 0)):
            mb.showwarning("IMPORTANTE", "Capturar: La CLAVE para ejecutar las acciones")
        elif (len(turno) == 0):
            mb.showwarning("IMPORTANTE", "Capturar: TURNO PARA CONTINUAR")
        else:
            datos = (usuario)
            respuesta = self.operacion1.ConsultaUsuario(datos) 
            print("respuesta: ",respuesta)
            
            if respuesta:
                for fila in respuesta :
                   idusuario = str(fila[0])
                   Clave = str(fila[1])
                   nombre = str(fila[2])     
                if contrasena == Clave:    
                   actual =(idusuario, usuario, inicio, nombre, turno) 
                   self.operacion1.ActuaizaUsuario(actual)
                   ##Cerrar la ventana
                   self.quitF()
                   from cobroFONLow import FormularioOperacion       
                   FormularioOperacion(self)
                   

                else:
                  mb.showwarning("IMPORTANTE", "La Contraseña no coincide, volver a capturarla")
                  self.Contraseña.set("")               
                  self.entryContraseña.focus()
                  ##limpiar el text de contraseña y poner el foco en ella.
                  ##Asteriscos en la contraseña  
            else:
                mb.showwarning("IMPORTANTE", "El usuario no existe")
                self.Nombre.set("")
                self.Contraseña.set("")
                self.Turno.set("")               
                self.entryNombre.focus() 
              
       # result=subprocess.getoutput('/home/pi/Documents/cobroid.py')    
    def toggleFullScreen(self, event):
        self.fullScreenState = not self.fullScreenState
        self.window.attributes("-fullscreen", self.fullScreenState)
        self.entryNombre.focus() 

    def quitFullScreen(self, event):
        self.fullScreenState = False
        self.window.attributes("-fullscreen", self.fullScreenState)
    def quitF(self):
        self.window.destroy()
        print('salir')

if __name__ == '__main__':
    app = Fullscreen_Example()  
