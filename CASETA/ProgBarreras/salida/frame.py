# -*- coding: utf-8 -*-
import tkinter # Python 3.3.1
principal = tkinter.Tk()
principal.title("Frame")
# elementos
etiqueta1 = tkinter.Label(principal, text="Formulario de registro: ")

marco1 = tkinter.Frame(principal, bd=5, relief="groove")

etiqueta2 = tkinter.Label(marco1, text="Nombre:")
entrada1 = tkinter.Entry(marco1, width=18)

etiqueta3 = tkinter.Label(marco1, text="Apellido:")
entrada2 = tkinter.Entry(marco1, width=18)

etiqueta4 = tkinter.Label(marco1, text="País:")
entrada3 = tkinter.Entry(marco1, width=18)

etiqueta5 = tkinter.Label(marco1, text="Ciudad:")
entrada4 = tkinter.Entry(marco1, width=18)
enviar=tkinter.Button(marco1, text="Enviar")
# Posicionamiento
etiqueta1.grid(row=0, column=1, pady=5)
marco1.grid(padx=10, pady=10, row=1, column=1)
etiqueta2.grid(row=0, column=1)
entrada1.grid(row=0, column=2, padx=10)
etiqueta3.grid(row=1, column=1)
entrada2.grid(row=1, column=2)
etiqueta4.grid(row=2, column=1)
entrada3.grid(row=2, column=2)
etiqueta5.grid(row=3, column=1)
entrada4.grid(row=3, column=2)
enviar.grid(row=4, column=2, pady=8)
principal.mainloop()
