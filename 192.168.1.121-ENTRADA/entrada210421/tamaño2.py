from tkinter import *
raiz = Tk()
mi_Frame = Frame()
mi_Frame.pack()
mi_Label = Label(mi_Frame, text="Yo soy un Label") #Creación del Label
mi_Label.pack()
mi_Label.config(bg="white") #Cambiar color de fondo
mi_Label.config(font=('Arial', 62)) #Cambiar tipo y tamaño de fuente
raiz.mainloop()
