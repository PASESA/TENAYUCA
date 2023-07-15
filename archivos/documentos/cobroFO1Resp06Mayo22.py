from datetime import datetime, date, time, timedelta
formato = "%H:%M:%S"
PensionadoOpen=1
from escpos.printer import *
import qrcode
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb
from tkinter import scrolledtext as st
from tkinter import font
from tkinter import *
from tkinter import simpledialog
import re

import operacion
import time
import xlsxwriter
from PIL import ImageTk, Image
import os
import serial
import RPi.GPIO as io
#out1 = 17
barrera = 17
io.setmode(io.BCM)              # modo in/out pin del micro
io.setwarnings(False)           # no señala advertencias de pin ya usados
io.setup(barrera,io.OUT)           # configura en el micro las salidas
io.output(barrera,1)
class FormularioOperacion:
    def __init__(self):
        #creamos un objeto que esta en el archivo operacion dentro la clase Operacion
        self.operacion1=operacion.Operacion()
        self.ventana1=tk.Tk()
        self.ventana1.title("MONTERREY COBRO")
        self.cuaderno1 = ttk.Notebook(self.ventana1)
        self.cuaderno1.config(cursor="")         # Tipo de cursor
        self.ExpedirRfid()
        self.consulta_por_folio()
        #self.calcular_cambio()
        self.listado_completo()
        self.Alta_Pensionado()
        self.cuaderno1.grid(column=0, row=0, padx=5, pady=5)
        self.ventana1.mainloop()
###########################Inicia Pagina1##########################

    def ExpedirRfid(self):
        self.pagina1 = ttk.Frame(self.cuaderno1)
        self.cuaderno1.add(self.pagina1, text="Expedir Boleto")
        #enmarca los controles LabelFrame
        self.labelframe1=ttk.LabelFrame(self.pagina1, text="Dar Entrada")
        self.labelframe1.grid(column=1, row=0, padx=0, pady=0)
        self.Adentroframe=ttk.LabelFrame(self.pagina1, text="Autos DENTRO")
        self.Adentroframe.grid(column=2, row=0, padx=0, pady=0)
        self.MaxId=tk.StringVar()
        self.entryMaxId=ttk.Entry(self.labelframe1, width=10, textvariable=self.MaxId, state="readonly")
        self.entryMaxId.grid(column=1, row=0, padx=4, pady=4)
        self.lbltitulo=ttk.Label(self.labelframe1, text="FOLIO")
        self.lbltitulo.grid(column=0, row=0, padx=0, pady=0)
        #####tomar placas del auto
        self.Placa=tk.StringVar()
        self.entryPlaca=tk.Entry(self.labelframe1, width=10, textvariable=self.Placa)
        self.entryPlaca.grid(column=1, row=1, padx=4, pady=4)
        self.lblPlaca=ttk.Label(self.labelframe1, text="COLOCAR PLACAS")
        self.lblPlaca.grid(column=0, row=1, padx=0, pady=0)

        self.labelhr=ttk.Label(self.labelframe1, text="HORA ENTRADA")
        self.labelhr.grid(column=0, row=2, padx=0, pady=0)

        self.scrolledtext=st.ScrolledText(self.Adentroframe, width=20, height=3)
        self.scrolledtext.grid(column=1,row=0, padx=4, pady=4)

        self.boton1=tk.Button(self.labelframe1, text="Generar Entrada", command=self.agregarRegistroRFID, width=13, height=3, anchor="center", background="red")
        self.boton1.grid(column=1, row=4, padx=4, pady=4)
        self.Autdentro=tk.Button(self.Adentroframe, text="Boletos sin Cobro", command=self.Autdentro, width=15, height=1, anchor="center")
        self.Autdentro.grid(column=2, row=0, padx=4, pady=4)
        self.boton2=tk.Button(self.pagina1, text="Salir del programa", command=quit, width=15, height=1, anchor="center", background="red")
        self.boton2.grid(column=0, row=0, padx=4, pady=4)
        #llamar a operacion y meter en Entrada la hora en el momento actual y un numero de corte 0
        #panel.pack(side = "bottom", fill = "both", expand = "yes")
    def Autdentro(self):
        respuesta=self.operacion1.Autos_dentro()
        self.scrolledtext.delete("1.0", tk.END)
        for fila in respuesta:
            self.scrolledtext.insert(tk.END, "Entrada num: "+str(fila[0])+"\nEntro: "+str(fila[1])+"\n\n")
    def agregarRegistroRFID(self):
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$impresion    $$$$$$$$$$$$$$$$$$$
        MaxFolio=str(self.operacion1.MaxfolioEntrada())
        MaxFolio = MaxFolio.strip("[(,)]")
        n1 = MaxFolio
        n2 = "1"
        masuno = int(n1)+int(n2)
        masuno = str(masuno)
        self.MaxId.set(masuno)
        fechaEntro = datetime.today()
        horaentrada = str(fechaEntro)
        horaentrada=horaentrada[:18]
        self.labelhr.configure(text=(horaentrada, "Entró"))
        corteNum = 0
        placa=str(self.Placa.get(), )
        datos=(fechaEntro, corteNum, placa)
        # hacer la foto de codigo qr
        #img = qrcode.make("2 de septiembre")
        fSTR=str(fechaEntro)
        imgqr=(fSTR + masuno)
        #img = qrcode.make(fechaEntro)
        img = qrcode.make(imgqr)
        # Obtener imagen con el tamaño indicado
        reducida = img.resize((100, 75))
        # Mostrar imagen reducida.show()
        # Guardar imagen obtenida con el formato JPEG
        reducida.save("reducida.png")
        f = open("reducida.png", "wb")
        img.save(f)
        f.close()
        #aqui lo imprimimos
        p = Usb(0x04b8, 0x0202, 0)
        #p = Usb(0x04b8, 0x0e15, 0)#esta es la impresora con sus valores que se obtienen con lsusb
        p.set("center")
        p.text("BOLETO DE ENTRADA\n")
        folioZZ=('FOLIO 000' + masuno)
        p.text(folioZZ+'\n')
        p.text('Entro: '+horaentrada+'\n')
        p.text('Placas '+placa+'\n')
        p.set(align="left")
        p.image("LOGO1.jpg")
        p.cut()
        p.image("LOGO1.jpg")
        p.text("--------------------------------------\n")
        p.set(align="center")
        p.text("BOLETO DE ENTRADA\n")
        folioZZ=('FOLIO 000' + masuno)
        p.text('Entro: '+horaentrada+'\n')
        p.text('Placas '+placa+'\n')
        p.text(folioZZ+'\n')
        p.image("AutoA.png")
        p.set(align = "center")
        p.image("reducida.png")
        p.image("LOGO8.jpg")
        p.text("            Le Atiende:               \n")
        p.text("--------------------------------------\n")
        p.cut()
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$impresion fin$$$$$$$$$$$$$$$$
        self.operacion1.altaRegistroRFID(datos)
        self.Placa.set('')
#########################fin de pagina1 inicio pagina2#########################
    def consulta_por_folio(self):
        self.pagina2 = ttk.Frame(self.cuaderno1)
        self.cuaderno1.add(self.pagina2, text=" Módulo de Cobro")
        #en el frame
        self.labelframe2=ttk.LabelFrame(self.pagina2, text="Autos")
        self.labelframe2.grid(column=0, row=0, padx=5, pady=10)
        self.label1=ttk.Label(self.labelframe2, text="Lector QR")
        self.label1.grid(column=0, row=0, padx=4, pady=4)
        self.label3=ttk.Label(self.labelframe2, text="Entro:")
        self.label3.grid(column=0, row=1, padx=4, pady=4)
        self.label4=ttk.Label(self.labelframe2, text="Salio:")
        self.label4.grid(column=0, row=2, padx=4, pady=4)
        #en otro frame
        self.labelframe3=ttk.LabelFrame(self.pagina2, text="Datos del COBRO")
        self.labelframe3.grid(column=1, row=0, padx=5, pady=10)
        self.lbl1=ttk.Label(self.labelframe3, text="Hr Salida")
        self.lbl1.grid(column=0, row=1, padx=4, pady=4)
        self.lbl2=ttk.Label(self.labelframe3, text="TiempoTotal")
        self.lbl2.grid(column=0, row=2, padx=4, pady=4)
        self.lbl3=ttk.Label(self.labelframe3, text="Importe")
        self.lbl3.grid(column=0, row=3, padx=4, pady=4)

        self.labelPerdido=ttk.LabelFrame(self.pagina2, text="Perdido")
        self.labelPerdido.grid(column=2,row=1,padx=5, pady=10)
        self.lblFOLIO=ttk.Label(self.labelPerdido, text=" FOLIO PERDIDO")
        self.lblFOLIO.grid(column=0, row=1, padx=4, pady=4)
        self.PonerFOLIO=tk.StringVar()
        self.entryPonerFOLIO=tk.Entry(self.labelPerdido, width=15, textvariable=self.PonerFOLIO)
        self.entryPonerFOLIO.grid(column=1, row=1)
        self.boton2=tk.Button(self.labelPerdido, text="B./SIN cobro", command=self.BoletoDentro, width=10, height=2, anchor="center")
        self.boton2.grid(column=0, row=0)
        self.boton3=tk.Button(self.labelPerdido, text="Boleto Perdido", command=self.BoletoPerdido, width=10, height=2, anchor="center")
        self.boton3.grid(column=0, row=2)
        self.scrolledtxt=st.ScrolledText(self.labelPerdido, width=28, height=7)
        self.scrolledtxt.grid(column=1,row=0, padx=10, pady=10)
        self.labelpromo=ttk.LabelFrame(self.pagina2, text="Promociones")
        self.labelpromo.grid(column=2, row=0, padx=5, pady=10)
        self.promolbl=ttk.Label(self.labelpromo, text="Leer el  QR de Promocion")
        self.promolbl.grid(column=0, row=0, padx=4, pady=4)
        self.promolbl1=ttk.Label(self.labelpromo, text="Codigo QR")
        self.promolbl1.grid(column=0, row=1, padx=4, pady=4)
        self.promolbl2=ttk.Label(self.labelpromo, text="Tipo Prom")
        self.promolbl2.grid(column=0, row=2, padx=4, pady=4)
        self.labelcuantopagas=ttk.LabelFrame(self.pagina2, text='cual es el pago')
        self.labelcuantopagas.grid(column=0,row=1, padx=5, pady=10)
        self.cuantopagas=ttk.Label(self.labelcuantopagas, text="la cantidad entregada")
        self.cuantopagas.grid(column=0, row=0, padx=4, pady=4)
        self.importees=ttk.Label(self.labelcuantopagas, text="el importe es")
        self.importees.grid(column=0, row=1, padx=4, pady=4)
        self.cambio=ttk.Label(self.labelcuantopagas, text="el cambio es")
        self.cambio.grid(column=0, row=2, padx=4, pady=4)
        self.cuantopagasen=tk.StringVar()
        self.entrycuantopagasen=tk.Entry(self.labelcuantopagas, width=15, textvariable=self.cuantopagasen)
        #self.entrycuantopagasen.bind('<Return>',self.calcular_cambio)
        self.entrycuantopagasen.grid(column=1, row=0)
        self.elimportees=tk.StringVar()
        self.entryelimportees=tk.Entry(self.labelcuantopagas, width=15, textvariable=self.elimportees, state="readonly")
        self.entryelimportees.grid(column=1, row=1)
        self.elcambioes=tk.StringVar()
        self.entryelcambioes=tk.Entry(self.labelcuantopagas, width=15, textvariable=self.elcambioes, state="readonly")
        self.entryelcambioes.grid(column=1, row=2)
        self.label11=ttk.Label(self.labelframe3, text="DIAS")
        self.label11.grid(column=1, row=4, padx=1, pady=1)
        self.label12=ttk.Label(self.labelframe3, text="HORAS")
        self.label12.grid(column=1, row=5, padx=1, pady=1)
        self.label7=ttk.Label(self.labelframe3, text="MINUTOS")
        self.label7.grid(column=1, row=6, padx=1, pady=1)
        self.label8=ttk.Label(self.labelframe3, text="SEGUNDOS")
        self.label8.grid(column=1, row=7, padx=1, pady=1)
        self.label9=ttk.Label(self.labelframe3, text="TOTAL COBRO")
        self.label9.grid(column=1, row=8, padx=1, pady=1)
        self.label15=ttk.Label(self.pagina2, text="Viabilidad de COBRO")
        self.label15.grid(column=1, row=2, padx=0, pady=0)
        #se crea objeto para ver pedir el folio la etiqueta con texto
        self.folio=tk.StringVar()
        self.entryfolio=tk.Entry(self.labelframe2, textvariable=self.folio)
        self.entryfolio.bind('<Return>',self.consultar)#con esto se lee automatico y se va a consultar
        self.entryfolio.grid(column=1, row=0, padx=4, pady=4)
        #se crea objeto para mostrar el dato de la  Entrada solo lectura
        self.descripcion=tk.StringVar()
        self.entrydescripcion=ttk.Entry(self.labelframe2, textvariable=self.descripcion, state="readonly")
        self.entrydescripcion.grid(column=1, row=1, padx=4, pady=4)
        #se crea objeto para mostrar el dato la Salida solo lectura
        self.precio=tk.StringVar()
        self.entryprecio=ttk.Entry(self.labelframe2, textvariable=self.precio, state="readonly")
        self.entryprecio.grid(column=1, row=2, padx=4, pady=4)
        #se crea objeto para MOSTRAR LA HORA DEL CALCULO
        self.copia=tk.StringVar()
        self.entrycopia=tk.Entry(self.labelframe3, width=20, textvariable=self.copia, state = "readonly")
        self.entrycopia.grid(column=1, row=1)
        #SE CREA UN OBJETO caja de texto IGUAL A LOS DEMAS Y MUESTRA EL TOTAL DEL TIEMPO
        self.ffeecha=tk.StringVar()
        self.entryffeecha=tk.Entry(self.labelframe3, width=20, textvariable=self.ffeecha, state= "readonly")
        self.entryffeecha.grid(column=1, row=2)
        #SE CREA UN OBJETO caja de texto IGUAL A LOS DEMAS para mostrar el importe y llevarlo a guardar en BD
        self.importe=tk.StringVar()
        self.entryimporte=tk.Entry(self.labelframe3, width=20, textvariable=self.importe, state= "readonly")
        self.entryimporte.grid(column=1, row=3)
        #creamos un objeto para obtener la lectura de la PROMOCION
        self.promo=tk.StringVar()
        self.entrypromo=tk.Entry(self.labelpromo, width=20, textvariable=self.promo)
        self.entrypromo.grid(column=1, row=1)
        #este es donde pongo el tipo de PROMOCION
        self.PrTi=tk.StringVar()
        self.entryPrTi=tk.Entry(self.labelpromo, width=20, textvariable=self.PrTi, state= "readonly")
        self.entryPrTi.grid(column=1, row=2)
        #botones
        #self.boton1=tk.Button(self.labelframe2, text="Consultar", command=self.consultar, width=20, height=5, anchor="center")
        #self.boton1.grid(column=1, row=4)
        self.boton2=tk.Button(self.labelpromo, text="Cliente OficeMax", command=self.CalculaPromocion, width=12, height=3, anchor="center")
        self.boton2.grid(column=1, row=4)
        self.btnTezo=tk.Button(self.labelpromo, text="Valet Durango", command=self.CalculaPromocionTezo, width=12, height=3, anchor="center")
        self.btnTezo.grid(column=1, row=5)
        self.btnTezo=tk.Button(self.labelpromo, text="Net Works", command=self.CalculaPromocionTezoEvento, width=12, height=3, anchor="center")
        self.btnTezo.grid(column=0, row=4)                   
        #self.boton3=tk.Button(self.pagina2, text="COBRAR ", command=self.GuardarCobro, width=20, height=5, anchor="center", background="Cadetblue")
        #self.boton3.grid(column=1, row=1)
        #self.boton4=tk.Button(self.labelframe3, text="IMPRIMIR", command=self.Comprobante, width=10, height=2, anchor="center", background="Cadetblue")
        #self.boton4.grid(column=0, row=4)
        self.bcambio=tk.Button(self.labelcuantopagas, text="Cobro", command=self.calcular_cambio, width=10, height=2, anchor="center", background="red")
        self.bcambio.grid(column=0, row=4)
        
        ####PENSIONADOS
        self.labelPensionado=ttk.LabelFrame(self.pagina2, text="SALIDA PENSIONADO")
        self.labelPensionado.grid(column=1, row=1, padx=5, pady=10)
        self.labelTarjeta=ttk.Label(self.labelPensionado, text="Num. Tarjeta:")
        self.labelTarjeta.grid(column=0, row=2, padx=0, pady=0)
        self.NumTarjeta2=tk.StringVar()
        self.entryNumTarjeta2=tk.Entry(self.labelPensionado, width=15, textvariable=self.NumTarjeta2)
        self.entryNumTarjeta2.grid(column=1, row=2, padx=4, pady=4)
        self.botonPensinados=tk.Button(self.labelPensionado, text="Salida", command=self.PensionadosSalida, width=10, height=1, anchor="center")
        self.botonPensinados.grid(column=1, row=3, padx=4, pady=4)  
        
    def BoletoDentro(self):
        respuesta=self.operacion1.Autos_dentro()
        self.scrolledtxt.delete("1.0", tk.END)
        for fila in respuesta:
            self.scrolledtxt.insert(tk.END, "Folio num: "+str(fila[0])+"\nEntro: "+str(fila[1])+"\nPlacas: "+str(fila[2])+"\n\n")
    def BoletoPerdido(self):
       datos=str(self.PonerFOLIO.get(), )
       datos=int(datos)
       datos=str(datos)
       self.folio.set(datos)
       datos=(self.folio.get(), )
       respuesta=self.operacion1.consulta(datos)
       if len(respuesta)>0:
           self.descripcion.set(respuesta[0][0])
           self.precio.set(respuesta[0][1])
           self.CalculaPermanencia()#nos vamos a la funcion de calcular permanencia
           fecha = datetime.today()
           fecha1= fecha.strftime("%Y-%m-%d %H:%M:%S")
           fechaActual= datetime.strptime(fecha1, '%Y-%m-%d %H:%M:%S')
           date_time_str=str(self.descripcion.get())
           date_time_obj= datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
           date_time_mod = datetime.strftime(date_time_obj, '%Y/%m/%d/%H/%M/%S')
           date_time_mod2 = datetime.strptime(date_time_mod, '%Y/%m/%d/%H/%M/%S')
           ffeecha = fechaActual - date_time_mod2
           #self.label11.configure(text=(ffeecha.days, "dias"))
           segundos_vividos = ffeecha.seconds
           horas_dentro, segundos_vividos = divmod(segundos_vividos, 3600)
           #self.label12.configure(text=(horas_dentro, "horas"))
           minutos_dentro, segundos_vividos = divmod(segundos_vividos, 60)
           if horas_dentro <= 24:
                importe = 200+((ffeecha.days)*720 + (horas_dentro * 30))
                #importe = 200
           if horas_dentro > 24 or ffeecha.days >= 1:
                importe = 200+((ffeecha.days)*720 + (horas_dentro * 30))
           self.importe.set(importe)
           self.label9.configure(text =(importe, "cobro"))
           self.PrTi.set("Per")
           self.Comprobante()
           p = Usb(0x04b8, 0x0202, 0)
           #p = Usb(0x04b8, 0x0e15, 0)#esta es la impresora con sus valores que se obtienen con lsusb
           p.text('Boleto Perdido\n')
           FoliodelPerdido = str(self.PonerFOLIO.get(),)
           p.text('Folio boleto cancelado: '+FoliodelPerdido+'\n')
           fecha = datetime.today()
           fechaNota = datetime.today()
           fechaNota= fechaNota.strftime("%b-%d-%A-%Y %H:%M:%S")
           horaNota = str(fechaNota)
           p.set(align="left")
           p.set('Big line\n', font='b')
           p.text('Fecha: '+horaNota+'\n')
           EntradaCompro = str(self.descripcion.get(),)
           p.text('El auto entro: '+EntradaCompro+'\n')
           SalioCompro = str(self.copia.get(),)
           p.text('El auto salio: '+SalioCompro+'\n')
           self.GuardarCobro()
           self.PonerFOLIO.set("")
           p.cut()
           self.promo.set("")
           self.PonerFOLIO.set("")
       else:
           self.descripcion.set('')
           self.precio.set('')
           mb.showinfo("Información", "No existe un auto con dicho código")
    def consultar(self,event):
        datos=str(self.folio.get(), )
        if len(datos) > 20:#con esto revisamos si lee el folio o la promocion
            datos=datos[26:]
            datos=int(datos)
            datos=str(datos)
            self.folio.set(datos)
            datos=(self.folio.get(), )
            respuesta=self.operacion1.consulta(datos)
            if len(respuesta)>0:
                self.descripcion.set(respuesta[0][0])
                self.precio.set(respuesta[0][1])
                self.CalculaPermanencia()#nos vamos a la funcion de calcular permanencia
            else:
                self.descripcion.set('')
                self.precio.set('')
                mb.showinfo("Información", "No existe un auto con dicho código")
        else:
            mb.showinfo("Promocion", "leer primero el folio")
            self.folio.set("")
    def CalculaPermanencia(self):# funcion que  CALCULA LA PERMANENCIA DEL FOLIO SELECCIONADO
        salida = str(self.precio.get(), )#deveria ser salida en lugar de precio pero asi estaba el base
        if len(salida)>5:#None tiene 4 letras si es mayor a 5 es que tiene ya la fecha
            self.label15.configure(text=("Este Boleto ya Tiene cobro"))
            self.elcambioes.set("")
            self.elimportees.set("")
            self.cuantopagasen.set("")
            self.descripcion.set('')
            self.precio.set(salida)
            self.copia.set("")
            self.importe.set("")
            self.ffeecha.set("")
            self.folio.set("")
            self.label7.configure(text=(""))
            self.label8.configure(text =(""))
            self.label9.configure(text =(""))
            #self.label10.configure(text=(""))
            self.label11.configure(text=(""))
            self.label12.configure(text=(""))
            #self.elimportees.configure(text=(""))
            self.entryfolio.focus()
        else:
            self.PrTi.set("Normal")
            self.label15.configure(text="Lo puedes COBRAR")
            fecha = datetime.today()
            fecha1= fecha.strftime("%Y-%m-%d %H:%M:%S")
            fechaActual= datetime.strptime(fecha1, '%Y-%m-%d %H:%M:%S')
            self.copia.set(fechaActual)
            date_time_str=str(self.descripcion.get())
            date_time_obj= datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
            date_time_mod = datetime.strftime(date_time_obj, '%Y/%m/%d/%H/%M/%S')
            date_time_mod2 = datetime.strptime(date_time_mod, '%Y/%m/%d/%H/%M/%S')
            ffeecha = fechaActual - date_time_mod2
            self.label11.configure(text=(ffeecha.days, "dias"))
            segundos_vividos = ffeecha.seconds
            horas_dentro, segundos_vividos = divmod(segundos_vividos, 3600)
            self.label12.configure(text=(horas_dentro, "horas"))
            minutos_dentro, segundos_vividos = divmod(segundos_vividos, 60)
            self.label7.configure(text=(minutos_dentro, "minutos"))
            #calcular la diferencia de segundos
            seg1 = ffeecha.seconds
            #print ("dif = seg1 = ", seg1)
            seg2 = ffeecha.seconds/60
            #print ("dif/60 = seg2 = ", seg2)
            seg3 = int(seg2)
            #print ("entero y redondear seg3 = ", seg3)
            seg4 = seg2-seg3
            #print ("seg2 - seg 3 = seg4 = ", seg4)
            seg5 = seg4*60
            #print ("seg5 =", seg5)
            seg6 = round(seg5)
            #print  ("segundos dentro ===> ", seg6)
            self.label8.configure(text =(seg6, "segundos"))
            #self.label9.configure(text =(ffeecha, "tiempo dentro"))
            self.ffeecha.set(ffeecha)
            if minutos_dentro < 15 and minutos_dentro  >= 0:
                minutos = 1
            if minutos_dentro < 30 and minutos_dentro  >= 15:
                minutos = 2
            if minutos_dentro < 45 and minutos_dentro  >= 30:
                minutos = 3
            if minutos_dentro <= 59 and minutos_dentro  >= 45:
                minutos = 4
            if ffeecha.days == 0 and horas_dentro == 0:
               importe = 28
               self.importe.set(importe)
               #self.elimportees.set(importe)
               self.label9.configure(text =(importe, "cobro"))
               self.entrypromo.focus()
            else:
                #if minutos <= 2:    
                        importe = ((ffeecha.days)*250 + (horas_dentro * 28)+(minutos)*7)
                        self.importe.set(importe)
                        self.label9.configure(text =(importe, "Cobrar"))
                        #self.calcular_cambio()
                        self.entrypromo.focus()
#                if minutos == 3:    
#                        importe = ((ffeecha.days)*864 + (horas_dentro * 36)+30)
#                        self.importe.set(importe)
#                        self.label9.configure(text =(importe, "Cobrar"))
#                        #self.calcular_cambio()
#                        self.entrypromo.focus() 
#                if minutos > 3:    
#                        importe = ((ffeecha.days)*864 + (horas_dentro * 36)+(minutos)*9)
#                        self.importe.set(importe)
#                        self.label9.configure(text =(importe, "Cobrar"))
#                        #self.calcular_cambio()
#                        self.entrypromo.focus()                                  
    def calcular_cambio(self):
        elimporte=str(self.importe.get(), )
        self.elimportees.set(elimporte)
        valorescrito=str(self.cuantopagasen.get(),)
        elimporte=float(elimporte)
        valorescrito=int(valorescrito)
        #mb.showinfo("Imp", elimporte)
        cambio=valorescrito-elimporte
        cambio=str(cambio)
        #mb.showinfo("CMbn", cambio)
        self.elcambioes.set(cambio)
        self.Comprobante()#manda a llamar el comprobante y lo imprime
        self.GuardarCobro()#manda a llamar guardar cobro para cobrarlo y guardar registro
        io.output(barrera,0)
        time.sleep(1)
        io.output(barrera,1)

    def Comprobante(self):
        p = Usb(0x04b8, 0x0202, 0)
        #p = Usb(0x04b8, 0x0e15, 0)#esta es la impresora con sus valores que se obtienen con lsusb
        p.text("        Comprobante de pago\n")
        placa=str(self.Placa.get(), )
        # hacer la foto de codigo qr
        #img = qrcode.make("2 de septiembre")
        EntradaCompro = str(self.descripcion.get(),)
        SalioCompro = str(self.copia.get(),)
        #img = qrcode.make(fechaEntro)
        img = qrcode.make(EntradaCompro + SalioCompro)
        # Obtener imagen con el tamaño indicado
        reducida = img.resize((100, 75))
        # Mostrar imagen reducida.show()
        # Guardar imagen obtenida con el formato JPEG
        reducida.save("reducida.png")
        f = open("reducida.png", "wb")
        img.save(f)
        f.close()
        p.image("LOGO1.jpg")
        #Compro de comprobante
        p.set('left')
        ImporteCompro=str(self.importe.get(),)
        p.text("El importe es $"+ImporteCompro+"\n")
        EntradaCompro = str(self.descripcion.get(),)
        p.text('El auto entro: '+EntradaCompro+'\n')
        SalioCompro = str(self.copia.get(),)
        p.text('El auto salio: '+SalioCompro+'\n')
        TiempoCompro = str(self.ffeecha.get(),)
        p.text('El auto permanecio: '+TiempoCompro+'\n')
        folioactual=str(self.folio.get(), )
        p.text('El folio del boleto es: '+folioactual+'\n')
        #p.text('Le atendio: ')
        p.cut()
        # ~ ImporteCompro=str(self.importe.get(),)
        # ~ p.text('           CONTRA \n')        
        # ~ p.text("El importe es $"+ImporteCompro+"\n")
        # ~ EntradaCompro = str(self.descripcion.get(),)
        # ~ p.text('El auto entro: '+EntradaCompro+'\n')
        # ~ SalioCompro = str(self.copia.get(),)
        # ~ p.text('El auto salio: '+SalioCompro+'\n')
        # ~ TiempoCompro = str(self.ffeecha.get(),)
        # ~ p.text('El auto permanecio: '+TiempoCompro+'\n')
        # ~ folioactual=str(self.folio.get(), )
        # ~ #p.set(height=2,align='left')
        # ~ p.text('El folio del boleto es: '+folioactual+'\n')
        # ~ #p.text('PAGADO ')
        # ~ p.cut()
        # ~ p.text('           CHOFER \n')        
        # ~ #p.text("El importe es $"+ImporteCompro+"\n")
        # ~ EntradaCompro = str(self.descripcion.get(),)
        # ~ p.text('El auto entro: '+EntradaCompro+'\n')
        # ~ SalioCompro = str(self.copia.get(),)
        # ~ p.text('El auto salio: '+SalioCompro+'\n')
        # ~ TiempoCompro = str(self.ffeecha.get(),)
        # ~ p.text('El auto permanecio: '+TiempoCompro+'\n')
        # ~ folioactual=str(self.folio.get(), )
        # ~ p.set(height=2,align='left')
        # ~ p.text('El folio del boleto es: '+folioactual+'\n')
        # ~ #p.text('PAGADO ')
        # ~ p.cut()
        
    def GuardarCobro(self):
        salida = str(self.precio.get(), )#deveria ser salida en lugar de precio pero asi estaba el base

        if len(salida)>5:
            self.label15.configure(text=("con salida, INMODIFICABLE"))
            mb.showinfo("Información", "Ya Tiene Salida")
            self.descripcion.set('')
            self.precio.set('')
            self.copia.set("")
            self.importe.set("")
            self.ffeecha.set("")
            self.folio.set("")
            self.label7.configure(text=(""))
            self.label8.configure(text =(""))
            self.label9.configure(text =(""))
            self.label11.configure(text=(""))
            self.label12.configure(text=(""))
            self.label15.configure(text=(""))
            self.entryfolio.focus()
        else:
            #self.Comprobante()
            self.label15.configure(text=(salida, "SI se debe modificar"))
            importe1 =str(self.importe.get(),)
            #mb.showinfo("impte1", importe1)
            folio1= str(self.folio.get(),)
            valorhoy = str(self.copia.get(),)
            fechaActual1 = datetime.strptime(valorhoy, '%Y-%m-%d %H:%M:%S' )
            fechaActual= datetime.strftime(fechaActual1,'%Y-%m-%d %H:%M:%S' )
            ffeecha1= str(self.ffeecha.get(),)
            valor=str(self.descripcion.get(),)
            fechaOrigen = datetime.strptime(valor, '%Y-%m-%d %H:%M:%S')
            promoTipo = str(self.PrTi.get(),)
            vobo = "lmf"#este
            datos=(vobo, importe1, ffeecha1, fechaOrigen, fechaActual, promoTipo, folio1)
            self.operacion1.guardacobro(datos)
            self.descripcion.set('')
            self.precio.set('')
            self.copia.set("")
            self.label7.configure(text=(""))
            self.label8.configure(text =(""))
            self.label9.configure(text =(""))
            self.label11.configure(text=(""))
            self.label12.configure(text=(""))
            self.label15.configure(text=(""))
            self.importe.set("")
            self.ffeecha.set("")
            self.folio.set("")
            self.PrTi.set("")
            #self.elcambioes.set("")
            #self.elimportees.set("")
            #self.cuantopagasen.set("")
            self.entryfolio.focus()#se posiciona en leer qr
    def CalculaPromocion(self):
########## Promocion ofice
           fecha = datetime.today()
           fecha1= fecha.strftime("%Y-%m-%d %H:%M:%S")
           fechaActual= datetime.strptime(fecha1, '%Y-%m-%d %H:%M:%S')
           date_time_str=str(self.descripcion.get())
           date_time_obj= datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
           date_time_mod = datetime.strftime(date_time_obj, '%Y/%m/%d/%H/%M/%S')
           date_time_mod2 = datetime.strptime(date_time_mod, '%Y/%m/%d/%H/%M/%S')
           ffeecha = fechaActual - date_time_mod2
           segundos_vividos = ffeecha.seconds
           horas_dentro, segundos_vividos = divmod(segundos_vividos, 3600)
           minutos_dentro, segundos_vividos = divmod(segundos_vividos, 60)
           if horas_dentro < 1:
               importe = 5
               self.importe.set(importe)
           importe = str(self.importe.get(), ) 
           importe = int(importe)
           #mb.showinfo("liverpool",importe) 
           if horas_dentro >= 1:
                importe = str(self.importe.get(), )
                #mb.showinfo("liverpool",importe) 
                importe = int(importe)   
                importe=(importe - 23)
                #importe = ((ffeecha.days)*720 + (horas_dentro * 30)+(minutos_dentro)*1)
           self.importe.set(importe)
           self.label9.configure(text =(importe, "cobro"))
           self.PrTi.set("OMax")
           #mb.showinfo("liverpool",importe)
           self.promo.set("")
    def CalculaPromocionTezo(self):
########## Promocion Durango
           fecha = datetime.today()
           fecha1= fecha.strftime("%Y-%m-%d %H:%M:%S")
           fechaActual= datetime.strptime(fecha1, '%Y-%m-%d %H:%M:%S')
           date_time_str=str(self.descripcion.get())
           date_time_obj= datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
           date_time_mod = datetime.strftime(date_time_obj, '%Y/%m/%d/%H/%M/%S')
           date_time_mod2 = datetime.strptime(date_time_mod, '%Y/%m/%d/%H/%M/%S')
           ffeecha = fechaActual - date_time_mod2
           segundos_vividos = ffeecha.seconds
           horas_dentro, segundos_vividos = divmod(segundos_vividos, 3600)
           minutos_dentro, segundos_vividos = divmod(segundos_vividos, 60)
           if horas_dentro < 12:
               importe = 60
               self.importe.set(importe)
           importe = str(self.importe.get(), ) 
           importe = int(importe)
           #mb.showinfo("liverpool",importe) 
           if horas_dentro >= 2:
                importe = str(self.importe.get(), )
                #mb.showinfo("liverpool",importe) 
                importe = int(importe)   
                importe=(importe - 72)+50
                #importe = ((ffeecha.days)*720 + (horas_dentro * 30)+(minutos_dentro)*1)
           self.importe.set(importe)
           self.label9.configure(text =(importe, "cobro"))
           self.PrTi.set("Netw")
           #mb.showinfo("liverpool",importe)
           self.promo.set("")
    def CalculaPromocionTezoEvento(self):
########## Promocion Liverpool
           fecha = datetime.today()
           fecha1= fecha.strftime("%Y-%m-%d %H:%M:%S")
           fechaActual= datetime.strptime(fecha1, '%Y-%m-%d %H:%M:%S')
           date_time_str=str(self.descripcion.get())
           date_time_obj= datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
           date_time_mod = datetime.strftime(date_time_obj, '%Y/%m/%d/%H/%M/%S')
           date_time_mod2 = datetime.strptime(date_time_mod, '%Y/%m/%d/%H/%M/%S')
           ffeecha = fechaActual - date_time_mod2
           segundos_vividos = ffeecha.seconds
           horas_dentro, segundos_vividos = divmod(segundos_vividos, 3600)
           minutos_dentro, segundos_vividos = divmod(segundos_vividos, 60)
           if horas_dentro < 12:
               importe = 60
               self.importe.set(importe)
           importe = str(self.importe.get(), ) 
           importe = int(importe)
           #mb.showinfo("liverpool",importe) 
           if horas_dentro >= 12:
                importe = str(self.importe.get(), )
                #mb.showinfo("liverpool",importe) 
                importe = int(importe)   
                importe=(importe - 180)+60
                #importe = ((ffeecha.days)*720 + (horas_dentro * 30)+(minutos_dentro)*1)
           self.importe.set(importe)
           self.label9.configure(text =(importe, "cobro"))
           self.PrTi.set("Lvpool")
           #mb.showinfo("liverpool",importe)
           self.promo.set("")
    ###PENSIONADOS
    def PensionadosSalida(self):
       numtarjeta=str(self.NumTarjeta2.get(), )
       #print(numtarjeta)
       if len(numtarjeta) == 0:
           mb.showwarning("IMPORTANTE", "Debe Leer el Numero de Tarjeta")
           return False
       else:
            tarjeta=int(numtarjeta)
            #print(tarjeta)
            respuesta=self.operacion1.ValidarTarj(tarjeta)
            #print(respuesta)
            if len(respuesta) == 0:
                mb.showwarning("IMPORTANTE", "No existe Pensionado para ese Num de Tarjeta")
                self.NumTarjeta2.set("")               
                self.entryNumTarjeta2.focus()
                return False
            else :
                for fila in respuesta:
                    Existe=fila[0]
                    Estatus=fila[1]
                    print(Existe)
                    if Existe == None :
                        mb.showwarning("IMPORTANTE", "No existe Pensionado para ese Num de Tarjeta")
                        self.NumTarjeta2.set("")               
                        self.entryNumTarjeta2.focus()
                        return False
                    elif Estatus == None:
                        mb.showwarning("IMPORTANTE", "Pensionado sin registro de Entrada")
                        self.NumTarjeta2.set("")               
                        self.entryNumTarjeta2.focus()
                        return False
                    elif Estatus == "Afuera":
                        mb.showwarning("IMPORTANTE", "El Pensionado de con ese Num de Tarjeta, ya esta Afuera")
                        self.NumTarjeta2.set("")               
                        self.entryNumTarjeta2.focus()
                        return False  
                    else:        
                        Salida=datetime.today()
                        datos=(Salida, 'Afuera', Existe)
                        datos1=('Afuera', Existe)
                        #sql="INSERT INTO PagosPens(id_cliente, num_tarjeta, Fecha_pago, Fecha_vigencia, Mensualidad, Monto) values (%s,%s,%s,%s,%s,%s)"
                        self.operacion1.UpdMovsPens(datos)
                        self.operacion1.UpdPens2(datos1)
                        self.NumTarjeta2.set("")               
                        self.entryNumTarjeta2.focus()
                        mb.showinfo("Pago de Pension",'Se registra SALIDA del auto')
                        #io.output(out3,1)#con un "1" se apaga el led
                        io.output(barrera,0)#con un "0" abre la barrera
                        time.sleep (1)
                        io.output(barrera,1)
           
###################### Fin de Pagina2 Inicio Pagina3 ###############################
    def listado_completo(self):
        self.pagina3 = ttk.Frame(self.cuaderno1)
        self.cuaderno1.add(self.pagina3, text="Módulo de Corte")
        self.labelframe1=ttk.LabelFrame(self.pagina3, text="Autos")
        self.labelframe1.grid(column=0, row=0, padx=1, pady=1)
        self.labelframe2=ttk.LabelFrame(self.pagina3, text="Generar Corte")
        self.labelframe2.grid(column=1, row=0, padx=0, pady=0)
        self.labelframe3=ttk.LabelFrame(self.pagina3, text="Consulta Cortes Anteriores")
        self.labelframe3.grid(column=0, row=1, padx=0, pady=0)

        self.labelframe4=ttk.LabelFrame(self.pagina3, text="Cuadro Comparativo")
        self.labelframe4.grid(column=1, row=1, padx=0, pady=0)
        self.labelframe5=ttk.LabelFrame(self.pagina3, text="Reporte de Cortes")
        self.labelframe5.grid(column=1, row=2, padx=1, pady=1)       
        self.lblSal=ttk.Label(self.labelframe4, text="Salida de Autos")
        self.lblSal.grid(column=3, row=1, padx=1, pady=1)
        self.lblS=ttk.Label(self.labelframe4, text="Entrada de Autos")
        self.lblS.grid(column=3, row=2, padx=1, pady=1)
        self.lblAnterior=ttk.Label(self.labelframe4, text="Autos del Turno anterior")
        self.lblAnterior.grid(column=3, row=3, padx=1, pady=1)
        self.lblEnEstac=ttk.Label(self.labelframe4, text="Autos en Estacionamiento")
        self.lblEnEstac.grid(column=3, row=4, padx=1, pady=1)
        self.lblC=ttk.Label(self.labelframe4, text="Boletos Cobrados:")
        self.lblC.grid(column=0, row=1, padx=1, pady=1)
        self.lblE=ttk.Label(self.labelframe4, text="Boletos Expedidos:")
        self.lblE.grid(column=0, row=2, padx=1, pady=1)
        self.lblA=ttk.Label(self.labelframe4, text="Boletos Turno Anterior:")
        self.lblA.grid(column=0, row=3, padx=1, pady=1)
        self.lblT=ttk.Label(self.labelframe4, text="Boletos Por Cobrar:")
        self.lblT.grid(column=0, row=4, padx=1, pady=1)
        self.BoletosCobrados=tk.StringVar()
        self.entryBoletosCobrados=tk.Entry(self.labelframe4, width=5, textvariable=self.BoletosCobrados, state= "readonly")
        self.entryBoletosCobrados.grid(column=1, row=1)
        self.BEDespuesCorte=tk.StringVar()
        self.entryBEDespuesCorte=tk.Entry(self.labelframe4, width=5, textvariable=self.BEDespuesCorte, state= "readonly")
        self.entryBEDespuesCorte.grid(column=1, row=2)
        self.BAnteriores=tk.StringVar()
        self.entryBAnteriores=tk.Entry(self.labelframe4, width=5, textvariable=self.BAnteriores, state= "readonly")
        self.entryBAnteriores.grid(column=1, row=3)
        self.BDentro=tk.StringVar()
        self.entryBDentro=tk.Entry(self.labelframe4, width=5, textvariable=self.BDentro, state= "readonly")
        self.entryBDentro.grid(column=1, row=4)
        self.SalidaAutos=tk.StringVar()
        self.entrySalidaAutos=tk.Entry(self.labelframe4, width=5, textvariable=self.SalidaAutos, state= "readonly")
        self.entrySalidaAutos.grid(column=2, row=1)
        self.SensorEntrada=tk.StringVar()
        self.entrySensorEntrada=tk.Entry(self.labelframe4, width=5, textvariable=self.SensorEntrada, state= "readonly", borderwidth=5)
        self.entrySensorEntrada.grid(column=2, row=2)
        self.Autos_Anteriores=tk.StringVar()
        self.entryAutos_Anteriores=tk.Entry(self.labelframe4, width=5, textvariable=self.Autos_Anteriores, state= "readonly")
        self.entryAutos_Anteriores.grid(column=2, row=3)
        self.AutosEnEstacionamiento=tk.StringVar()
        self.entryAutosEnEstacionamiento=tk.Entry(self.labelframe4, width=5, textvariable=self.AutosEnEstacionamiento, state= "readonly", borderwidth=5)
        self.entryAutosEnEstacionamiento.grid(column=2, row=4)
        self.boton6=tk.Button(self.labelframe4, text="Consulta Bol-Sensor", command=self.Puertoycontar, width=15, height=3, anchor="center")
        self.boton6.grid(column=1, row=0, padx=1, pady=1)

        self.FrmCancelado=ttk.LabelFrame(self.pagina3, text="Boleto Cancelado")
        self.FrmCancelado.grid(column=0, row=2, padx=0, pady=0)
        self.labelCorte=ttk.Label(self.labelframe2, text="El Total del CORTE es:")
        self.labelCorte.grid(column=0, row=1, padx=0, pady=0)
        self.label2=ttk.Label(self.labelframe2, text="La Fecha de CORTE es:")
        self.label2.grid(column=0, row=2, padx=1, pady=1)
        self.label3=ttk.Label(self.labelframe2, text="El CORTE Inicia ")
        self.label3.grid(column=0, row=3, padx=1, pady=1)
        self.label4=ttk.Label(self.labelframe2, text="El Numero de CORTE es:")
        self.label4.grid(column=0, row=4, padx=1, pady=1)
        self.label5=ttk.Label(self.labelframe3, text="CORTE a Consultar :")
        self.label5.grid(column=0, row=1, padx=1, pady=1)
        self.label6=ttk.Label(self.labelframe3, text="Fecha y hora del CORTE")
        self.label6.grid(column=0, row=2, padx=1, pady=1)

        self.lblCancelado=ttk.Label(self.FrmCancelado, text="COLOCAR FOLIO")
        self.lblCancelado.grid(column=0, row=1, padx=4, pady=4)
        self.FolioCancelado=tk.StringVar()
        self.entryFOLIOCancelado=tk.Entry(self.FrmCancelado, width=15, textvariable=self.FolioCancelado)
        self.entryFOLIOCancelado.grid(column=1, row=1, padx=4, pady=4)
        self.boton7=tk.Button(self.FrmCancelado, text="B./SIN cobro", command=self.BoletoDentro2, width=15, height=3, anchor="center")
        self.boton7.grid(column=0, row=0, padx=1, pady=1)
        #self.boton8=tk.Button(self.FrmCancelado, text="desglose", command=self.desglose_cobrados, width=15, height=3, anchor="center")
        #self.boton8.grid(column=1, row=3, padx=1, pady=1)

        self.btnCancelado=tk.Button(self.FrmCancelado, text="Cancelar Boleto ", command=self.BoletoCancelado, width=10, height=2, anchor="center")
        self.btnCancelado.grid(column=0, row=2)
        self.scrolledtxt2=st.ScrolledText(self.FrmCancelado, width=28, height=7)
        self.scrolledtxt2.grid(column=1,row=0, padx=1, pady=1)
        self.ImporteCorte=tk.StringVar()
        self.entryImporteCorte=tk.Entry(self.labelframe2, width=20, textvariable=self.ImporteCorte, state= "readonly", borderwidth=5)
        self.entryImporteCorte.grid(column=1, row=1)
        self.FechaCorte=tk.StringVar()
        self.entryFechaCorte=tk.Entry(self.labelframe2, width=20, textvariable=self.FechaCorte, state= "readonly")
        self.entryFechaCorte.grid(column=1, row=2)
        self.FechUCORTE=tk.StringVar()
        self.entryFechUCORTE=tk.Entry(self.labelframe2, width=20, textvariable=self.FechUCORTE, state= "readonly")
        self.entryFechUCORTE.grid(column=1, row=3)
#        self.CortesAnteri=tk.StringVar()
#        self.CortesAnteri=tk.Entry(self.labelframe3, width=20, textvariable=self.CortesAnteri)
#        self.CortesAnteri.grid(column=1, row=1)
        self.CortesAnteri=tk.StringVar()
        self.entryCortesAnteri=tk.Entry(self.labelframe3, width=20, textvariable=self.CortesAnteri)
        self.entryCortesAnteri.grid(column=1, row=1)
        
        self.boton1=ttk.Button(self.labelframe1, text="Todas las Entradas", command=self.listar)
        self.boton1.grid(column=0, row=0, padx=4, pady=4)
        self.boton2=ttk.Button(self.labelframe1, text="Entradas sin corte", command=self.listar1)
        self.boton2.grid(column=0, row=2, padx=4, pady=4)
        self.boton3=tk.Button(self.labelframe2, text="Calcular Corte", command=self.Calcular_Corte, width=15, height=1)
        self.boton3.grid(column=2, row=0, padx=4, pady=4)
        self.boton4=tk.Button(self.labelframe2, text="Generar Corte", command=self.Guardar_Corte, width=15, height=1, anchor="center", background="red")
        self.boton4.grid(column=2, row=4, padx=4, pady=4)
        self.boton5=tk.Button(self.labelframe3, text="Imprimir salidas  Corte", command=self.desglose_cobrados, width=15, height=3, anchor="center")
        self.boton5.grid(column=1, row=2, padx=4, pady=4)    
        self.scrolledtext1=st.ScrolledText(self.labelframe1, width=30, height=4)
        self.scrolledtext1.grid(column=0,row=1, padx=1, pady=1)
        
        self.label7=ttk.Label(self.labelframe5, text="Mes :")
        self.label7.grid(column=0, row=0, padx=1, pady=1)
        self.label8=ttk.Label(self.labelframe5, text="Ano :")
        self.label8.grid(column=0, row=2, padx=1, pady=1)
        self.comboMesCorte = ttk.Combobox(self.labelframe5, width=6, justify=tk.RIGHT, state="readonly")
        self.comboMesCorte["values"] = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
        self.comboMesCorte.current(0)
        self.comboMesCorte.grid(column=1, row=0, padx=1, pady=1)
        self.AnoCorte=tk.IntVar()
        Ano= datetime.now().date().year
        self.AnoCorte.set(Ano)
        self.entryAnoCorte=tk.Entry(self.labelframe5, width=7, textvariable=self.AnoCorte, justify=tk.RIGHT)
        self.entryAnoCorte.grid(column=1, row=2)       
        self.boton6=tk.Button(self.labelframe5, text="Reporte de Corte", command=self.Reporte_Corte, width=15, height=1, anchor="center", background="red")
        self.boton6.grid(column=3, row=2, padx=4, pady=4)        
    def BoletoDentro2(self):
        respuesta=self.operacion1.Autos_dentro()
        self.scrolledtxt2.delete("1.0", tk.END)
        for fila in respuesta:
            self.scrolledtxt2.insert(tk.END, "Folio num: "+str(fila[0])+"\nEntro: "+str(fila[1])+"\nPlacas: "+str(fila[2])+"\n\n")
    def desglose_cobrados(self):
        Numcorte=str(self.CortesAnteri.get(), )
        Numcorte=int(Numcorte)
        Numcorte=str(Numcorte)
        io.output(out1,0)
        time.sleep(1)
        io.output(out1,1)
        respuesta=self.operacion1.desglose_cobrados(Numcorte)
        self.scrolledtxt2.delete("1.0", tk.END)
        p = Usb(0x04b8, 0x0202, 0)
        #p = Usb(0x04b8, 0x0e15, 0)#esta es la impresora con sus valores que se obtienen con lsusb
        p.text("El Numero de corte es "+Numcorte+'\n')
        for fila in respuesta:
            self.scrolledtxt2.insert(tk.END, "cobro: "+str(fila[0])+"\nImporte: $"+str(fila[1])+"\nCuantos: "+str(fila[2])+"\n\n")
            p.text('Tipo de cobro :')
            p.text(str(fila[0]))
            p.text('\n')
            p.text('Importe :')
            p.text(str(fila[1]))
            p.text('\n')
            p.text('Cuantos ')
            p.text(str(fila[2]))
            p.text('\n')
        else:
            p.cut()
    def BoletoCancelado(self):
       datos=str(self.FolioCancelado.get(), )
       datos=int(datos)
       datos=str(datos)
       self.folio.set(datos)
       datos=(self.folio.get(), )
       respuesta=self.operacion1.consulta(datos)
       if len(respuesta)>0:
           self.descripcion.set(respuesta[0][0])
           self.precio.set(respuesta[0][1])
           self.CalculaPermanencia()#nos vamos a la funcion de calcular permanencia
           fecha = datetime.today()
           fecha1= fecha.strftime("%Y-%m-%d %H:%M:%S")
           fechaActual= datetime.strptime(fecha1, '%Y-%m-%d %H:%M:%S')
           date_time_str=str(self.descripcion.get())
           date_time_obj= datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
           date_time_mod = datetime.strftime(date_time_obj, '%Y/%m/%d/%H/%M/%S')
           date_time_mod2 = datetime.strptime(date_time_mod, '%Y/%m/%d/%H/%M/%S')
           ffeecha = fechaActual - date_time_mod2
            #self.label11.configure(text=(ffeecha.days, "dias"))
           segundos_vividos = ffeecha.seconds
           horas_dentro, segundos_vividos = divmod(segundos_vividos, 3600)
        #    self.label12.configure(text=(horas_dentro, "horas"))
           minutos_dentro, segundos_vividos = divmod(segundos_vividos, 60)
           if horas_dentro <= 24:
                importe = 0
           if horas_dentro > 24 or ffeecha.days >= 1:
                importe =0
           self.importe.set(importe)
           self.label9.configure(text =(importe, "cobro"))
           self.PrTi.set("CDO")
           self.promo.set("")
           p = Usb(0x04b8, 0x0202, 0)
           #p = Usb(0x04b8, 0x0e15, 0)#esta es la impresora con sus valores que se obtienen con lsusb
           p.text('Boleto Cancelado\n')
           FoliodelCancelado = str(self.FolioCancelado.get(),)
           p.text('Folio boleto cancelado: '+FoliodelCancelado+'\n')
           fecha = datetime.today()
           fechaNota = datetime.today()
           fechaNota= fechaNota.strftime("%b-%d-%A-%Y %H:%M:%S")
           horaNota = str(fechaNota)
           p.set(align="left")
           p.set('Big line\n', font='b')
           p.text('Fecha: '+horaNota+'\n')
           EntradaCompro = str(self.descripcion.get(),)
           p.text('El auto entro: '+EntradaCompro+'\n')
           SalioCompro = str(self.copia.get(),)
           p.text('El auto salio: '+SalioCompro+'\n')
           self.GuardarCobro()
           self.FolioCancelado.set("")
           p.cut()

       else:
           self.descripcion.set('')
           self.precio.set('')
           mb.showinfo("Información", "No existe un auto con dicho código")
    def listar(self):
        respuesta=self.operacion1.recuperar_todos()
        self.scrolledtext1.delete("1.0", tk.END)
        for fila in respuesta:
            self.scrolledtext1.insert(tk.END, "Entrada num: "+str(fila[0])+"\nEntro: "+str(fila[1])+"\nSalio: "+str(fila[2])+"\n\n")
    def listar1(self):
        respuesta=self.operacion1.recuperar_sincobro()
        self.scrolledtext1.delete("1.0", tk.END)
        #respuesta=str(respuesta)
        for fila in respuesta:
            self.scrolledtext1.insert(tk.END, "Entrada num: "+str(fila[0])+"\nEntro: "+str(fila[1])+"\nSalio: "+str(fila[2])+"\nImporte: "+str(fila[3])+"\n\n")
            p = Usb(0x04b8, 0x0202, 0)
            #p = Usb(0x04b8, 0x0e15, 0)#esta es la impresora con sus valores que se obtienen con lsusb
            p.text('Entrada Num :')
            p.text(str(fila[0]))
            p.text('\n')
            p.text('Entro :')
            p.text(str(fila[1]))
            p.text('\n')
            p.text('Salio :')
            p.text(str(fila[2]))
            p.text('\n')
            p.text('importe :')
            p.text(str(fila[3]))
            p.text('\n')
        else:
            p.cut()
    def Calcular_Corte(self):
        respuesta=self.operacion1.corte()
        self.ImporteCorte.set(respuesta)
        ##obtengamo la fechaFin del ultimo corte
        ultiCort1=str(self.operacion1.UltimoCorte())
        #mb.showinfo("msj uno",ultiCort1)
        startLoc = 20
        endLoc = 43
        ultiCort1=(ultiCort1)[startLoc: endLoc]
        ultiCort1 = ultiCort1.strip('),')
        #mb.showinfo("msj uno",ultiCort1)
        #mb.showinfo("msj uno",str(len(ultiCort1)))
        if len(ultiCort1) <= 18:
                             #mb.showinfo("msj dos",ultiCort1)
                             ultiCort1= datetime.strptime(ultiCort1, '%Y, %m, %d, %H, %M')
        else:
            ultiCort1= datetime.strptime(ultiCort1, '%Y, %m, %d, %H, %M, %S')
            #mb.showinfo("msj tres",ultiCort1)
        ultiCort1 = datetime.strftime(ultiCort1, '%Y/%m/%d/%H/%M/%S')
        ultiCort1 = datetime.strptime(ultiCort1, '%Y/%m/%d/%H/%M/%S')
        self.FechUCORTE.set(ultiCort1)# donde el label no esta bloqueada
        ###ahora obtenemos la fecha del corte ha realizar
        fecha = datetime.today()
        fecha1= fecha.strftime("%Y-%m-%d %H:%M:%S")
        fechaActual= datetime.strptime(fecha1, '%Y-%m-%d %H:%M:%S')
        self.FechaCorte.set(fechaActual)#donde el label esta bloqueado
    def Guardar_Corte(self):
        self.Puertoycontar()
        ##la fecha final de este corte que es la actual
        fechaDECorte = str(self.FechaCorte.get(),)
        fechaDECorte = datetime.strptime(fechaDECorte, '%Y-%m-%d %H:%M:%S' )
        ######la fecha del inicial obtiene de labase de datos
        fechaInicio1 = str(self.FechUCORTE.get(),)
        fechaInicio2 = datetime.strptime(fechaInicio1, '%Y-%m-%d %H:%M:%S')
        fechaInicio = fechaInicio2
        ######el importe se obtiene de la suma
        ImpCorte2 =str(self.ImporteCorte.get(),)
        Im38=ImpCorte2.strip('(,)')
        AEE = 0#str(self.AutosEnEstacionamiento.get(),)
        maxnumid=str(self.operacion1.MaxfolioEntrada())
        maxnumid = "".join([x for x in maxnumid if x.isdigit()])#con esto solo obtenemos los numeros
        maxnumid=int(maxnumid)
        maxnumid=str(maxnumid)
        pasa = str(self.BDentro.get(),)
        NumBolQued = pasa.strip('(),')
        datos=(Im38, fechaInicio, fechaDECorte,AEE,maxnumid,NumBolQued)
        self.operacion1.GuarCorte(datos)
        maxnum1=str(self.operacion1.Maxfolio_Cortes())
        maxnum = "".join([x for x in maxnum1 if x.isdigit()])#con esto solo obtenemos los numeros
        maxnum=int(maxnum)
        maxnum=str(maxnum)
        vobo = "cor"#este es para que la instruccion no marque error
        ActEntradas = (maxnum, vobo )
        self.label4.configure(text=("Numero de corte",maxnum))
        p = Usb(0x04b8, 0x0202, 0)
        #p = Usb(0x04b8, 0x0e15, 0)#esta es la impresora con sus valores que se obtienen con lsusb
        
        p.text(" Est Monterrey 75 CORTE Num "+maxnum+"\n")
        p.text('IMPORTE: $ '+Im38+'\n')
        #p.text('IMPORTE: $ '+ImpCorte2+'\n')
        ultiCort1=str(self.FechUCORTE.get(),)
        ultiCort4= datetime.strptime(ultiCort1, '%Y-%m-%d %H:%M:%S')
        ultiCort5 = datetime.strftime(ultiCort4, '%A %d %m %Y a las %H:%M:%S')
        p.text('Inicio:')
        p.text(ultiCort5)
        p.text('\n')
        valorFEsteCorte = str(self.FechaCorte.get(),)
        fechaDECorte = datetime.strptime(valorFEsteCorte, '%Y-%m-%d %H:%M:%S' )
        fechaDECorte = datetime.strftime(fechaDECorte, '%A %d %m %Y a las %H:%M:%S' )
        p.text('Final :')
        p.text(str(fechaDECorte))
        p.text('\n')
        MaxFolio=str(self.operacion1.MaxfolioEntrada())
        MaxFolio = MaxFolio.strip("[(,)]")
        BEDespuesCorteImpre = str(self.BEDespuesCorte.get(),)
        BEDespuesCorteImpre = BEDespuesCorteImpre.strip("[(,)]")
        IniFolio =int(MaxFolio)-int(BEDespuesCorteImpre)
        IniFolio = str(IniFolio)
        p.text("Folio "+IniFolio+" al inicio del turno\n")
        p.text("Folio "+MaxFolio+" al final del turno\n")                        
        BolCobrImpresion=str(self.BoletosCobrados.get(),)
        p.text("Boletos Cobrados: "+BolCobrImpresion+"\n")
        #SalidasSen =  int(self.SalidaAutos.get(),)
        #SalidasSen =  str(SalidasSen)
        #p.text("Salidas Sensor: "+SalidasSen+"\n")

        p.text('Boletos Expedidos: '+BEDespuesCorteImpre+'\n')
        #EntradasSen = int(self.SensorEntrada.get(),)
        #EntradasSen =  str(EntradasSen)
        #p.text('Entradas Sensor: '+EntradasSen+'\n')
        BAnterioresImpr=str(self.BAnteriores.get(),)#######
        p.text("Boletos Turno Anterior: "+BAnterioresImpr+"\n")
        #AutosAnteriores = int(self.Autos_Anteriores.get(),)
        #AutosAnteriores = str(AutosAnteriores)
        #p.text('Sensor Turno Anterior: '+AutosAnteriores+'\n')
        BDentroImp = str(self.BDentro.get(),)
        p.text('Boletos por Cobrar: '+BDentroImp+'\n')
        AutosEnEstacImpre = str(self.AutosEnEstacionamiento.get(),)
        #p.text('Autos en estacionamiento por sensor: '+AutosEnEstacImpre+'\n')
        p.text('------------------------------')
        p.text('\n')
        #Bandera = o
        self.ImporteCorte.set("")
        #p.cut()
        self.operacion1.ActualizarEntradasConcorte(ActEntradas)
        vobo='ant'
        self.operacion1.NocobradosAnt(vobo)
        ponercorte =int(maxnum)
        #mb.showinfo("primero",ponercorte)
        self.CortesAnteri.set(ponercorte)
        #self.desglose_cobrados()
        Numcorte=str(self.CortesAnteri.get(), )
        Numcorte=int(Numcorte)
        Numcorte=str(Numcorte)
        #mb.showinfo("segundo", Numcorte)
        #io.output(out1,0)
        #time.sleep(1)
        #io.output(out1,1)
        respuesta=self.operacion1.desglose_cobrados(Numcorte)
        self.scrolledtxt2.delete("1.0", tk.END)
        #mb.showinfo("respuesta", respuesta)
        p = Usb(0x04b8, 0x0202, 0)
        #p = Usb(0x04b8, 0x0e15, 0)#esta es la impresora con sus valores que se obtienen con lsusb
        p.text("Cantidad e Importes "+'\n')
        p.text("Cantidad - Tarifa - valor C/U - Total "+'\n')
        for fila in respuesta:
            self.scrolledtxt2.insert(tk.END, str(fila[0])+" Boletos con tarifa "+str(fila[1])+"\n"+"valor c/u $"+str(fila[2])+" Total $"+str(fila[3])+"\n\n")
            p.text('   ')
            p.text(str(fila[0]))
            p.text('   -  ')
            p.text(str(fila[1]))
            p.text(' -  $')
            #p.text('valor c/u $')
            p.text(str(fila[2]))
            p.text('  -  $')
            p.text(str(fila[3]))
            p.text('\n')
        else:
            p.text(BolCobrImpresion+' Boletos           Suma total $'+Im38+'\n')    
            p.cut()
        #ser = serial.Serial('/dev/ttyAMA0', 9600)
        #Enviamos el caracter por serial, codificado en Unicode
        #entrada='c'
        #ser.write(str(entrada).encode())
    def Reporte_Corte(self):
        contrasena = simpledialog.askinteger("Contrasena", "Capture su Contrasena:",
                                 parent=self.labelframe4) # minvalue=8, maxvalue=8
        if contrasena is not None:
            if contrasena == 12345678 :
                #mb.showinfo("Contrasena Correcta ", contrasena)
                try:
                    mes=self.comboMesCorte.get()
                    Ano=int(self.entryAnoCorte.get(), )
                    #mb.showinfo("msj uno",mes)
                    #mb.showinfo("msj dos",Ano)
                    if Ano is None :
                        mb.showwarning("IMPORTANTE", "Debe capturar el Ano del reporte")
                        return False
                    elif Ano <= 0 :
                        mb.showwarning("IMPORTANTE", " debe ser un numero positivo mayor a cero")
                        return False
                    else :
                        Libro = '/media/pi/rootfs/home/pi/Documents/Cobro/REPORTE/Rpte Corte '+ str(mes)+'-'+str(Ano)+'  '+str(datetime.now().date())+'.xlsx' #+'/' '/home/pi/Documents/electrofloculacion/belen/Prueba/RPTCORTE.xlsx'
                        #mb.showinfo("msj uno",mes)
                        #mb.showinfo("msj dos",Ano)
                        datos=(mes, Ano)
                        #Obtenemos Fecha (Inicialy Final) del mes que solicita el reporte
                        CorteMax=self.operacion1.Cortes_Max(datos)
                        CorteMin=self.operacion1.Cortes_Min(datos)
                        print(CorteMin)
                        print(CorteMax)
                        for fila in CorteMax:
                            UltFecha=fila[0] 
                            UltCorte=fila[1]
                        for fila in CorteMin:
                            IniFecha=fila[0]
                            IniCorte=fila[1]
                        #Obtenemos Fecha Inicial y Final del Folio de Cortes del Mes que se solicita el reporte
                        datos=(IniCorte)
                        CorteIni=self.operacion1.Cortes_Folio(datos)
                        for fila in CorteIni:
                            CorteIni2=fila[0]
                        #mb.showinfo("msj uno",UltFecha)
                        print(CorteIni2)
                        datos=(UltCorte)
                        #mb.showinfo("msj uno",CorteIni2)
                        CorteFin=self.operacion1.Cortes_Folio(datos)
                        for fila in CorteFin:
                            CorteFin2=fila[1]
                        print(CorteFin2)                        
                        #Obtnemos los Registros entre estos dos Folios para el cuerpo del reporte       
                        datos=(CorteIni2, CorteFin2)
                        #datos=(IniCorte, UltCorte)
                        Registros=self.operacion1.Registros_corte(datos)
                        TotalesCorte=self.operacion1.Totales_corte(datos)
                        #mb.showinfo("msj dos",'Un paso antes de Resumen Promo')
                        ResumenPromo=self.operacion1.Resumen_promo(datos)# def Resumen_promo(self, datos1):
                        #mb.showinfo("msj dos", ResumenPromo)#'Excelente paso Resumen Promo'
                        workbook = xlsxwriter.Workbook(Libro)
                        worksheet = workbook.add_worksheet('CORTE')
                        #Definimos Encabezado Principal
                        #Obtnemos imagen del Encabezado
                        worksheet.insert_image('A3', '/media/pi/rootfs/home/pi/Documents/Cobro/LOGO.jpg',{'x_scale': 0.95, 'y_scale': 0.95}) #Insert de Logo (imagen.png)
                        #Definimos Formatos de celda del encabezado
                        cell_format0 = workbook.add_format()
                        cell_format0 = workbook.add_format({'bold': True,'align':'right'})
                        cell_format1 = workbook.add_format()
                        cell_format1 = workbook.add_format({'bold': True,'align':'right','num_format':'$#,##0.00', 'bg_color':'#D9D9D9'})
                        cell_format2 = workbook.add_format() #{'num_format': 'dd/mm/yy'}
                        cell_format2.set_num_format('dd/mm/yy h:mm:ss')  # Format string.                
                        cell_format3 = workbook.add_format()
                        cell_format3 = workbook.add_format({'bold': True, 'align':'center','size': 15})
                        cell_format4 = workbook.add_format()
                        cell_format4 = workbook.add_format({'bold': True, 'align':'center'})
                        cell_format5 = workbook.add_format()
                        cell_format5 = workbook.add_format({'align':'right','num_format':'$#,##0.00'})
                        cell_format6 = workbook.add_format()
                        cell_format6= workbook.add_format({'align':'right','num_format':'#,##0'})                        
                        #Colocamos Resumen x Promoci[on en Encabezado
                        worksheet.write('E2', 'PROM', cell_format4)
                        worksheet.write('F2', 'CANT.', cell_format4)
                        worksheet.write('G2', 'TOTAL X PROMCION', cell_format4)                        
                        row=2
                        col=4
                        for fila in ResumenPromo:
                            #print(str(fila[0]))
                            worksheet.write(row, col,   fila[1]) #Nombre de la Promo A12
                            worksheet.write(row, col+1, fila[0],cell_format6) #Numero de Folios por Promocion B12
                            worksheet.write(row, col+2, fila[3],cell_format5) #Monto Total por Promocion C12
                            row += 1
                        #Colocamos Totales del Encabezado
                        row=row+1
                        worksheet.write('C3', 'REPORTE DE CORTE', cell_format3) #Aqui debe ir el nombre de la sucursal pero de d[onde lo obtengo?
                        worksheet.write('E'+str(row), 'TOTAL:',cell_format4)
                        worksheet.write('F'+str(row+1), 'PERIODO',cell_format4)
                        worksheet.write('F'+str(row+2), 'Inicio')#f5
                        worksheet.write('F'+str(row+3), 'Fin')#f6
                        worksheet.write('F'+str(row+4), 'Cortes')#f7
                        worksheet.write('F'+str(row+5), 'Suma del Periodo:', cell_format0)#f8
                        worksheet.write('G'+str(row+2), IniFecha, cell_format2)#g5
                        worksheet.write('G'+str(row+3), UltFecha, cell_format2)#g6
                        for fila in TotalesCorte:
                            worksheet.write('G'+str(row), fila[0], cell_format5)#Total de Cobros en resumen
                            worksheet.write('F'+str(row), fila[3], cell_format6)#Total de Folios en Resumen
                            worksheet.write('G'+str(row+5), fila[0], cell_format1)# Total de cobros Encabezado
                            worksheet.write('G'+str(row+4),str(fila[2]) +" al "+ str(fila[1]))
                        #mb.showinfo("msj Totale",str(fila[2]))                        
                        #Definimos Formato y Ancho de Fila Encabezado del cuerpo del reporte      
                        cell_format = workbook.add_format({'bold': True, 'align':'center', 'text_wrap':True, 'border':1, 'pattern':1, 'bg_color':'#D9D9D9'}) #808080      
                        worksheet.set_row(row+7, 34, cell_format)
                        #Definimos anchos de Columna del cuerpo del reporte
                        worksheet.set_column(0, 0, 10)
                        worksheet.set_column(1, 2, 30)
                        worksheet.set_column(3, 4, 14)
                        worksheet.set_column(5, 5, 13)
                        worksheet.set_column(6, 6, 30)
                        worksheet.set_column(7, 7, 10)
                        #Definimos Nombres de columnas del cuerpo del reporte
                        worksheet.write('A'+str(row+8), 'FOLIO')
                        worksheet.write('B'+str(row+8), 'FECHA Y HORA ENT')
                        worksheet.write('C'+str(row+8), 'FECHA Y HORA SAL')
                        worksheet.write('D'+str(row+8), 'TIEMPO')
                        worksheet.write('E'+str(row+8), 'PRECIO')
                        worksheet.write('F'+str(row+8), 'CORTES')
                        worksheet.write('G'+str(row+8), 'DESCRIPCION')
                        worksheet.write('H'+str(row+8), 'PROM')
                        #Definimos Formatos de celda para datos del cuerpo del reporte
                        cell_format7 = workbook.add_format() #{'num_format': 'hh:mm:ss'}
                        cell_format7 = workbook.add_format({'align':'right','num_format':'h:mm:ss'})
                        row=row+8
                        col=0
                        for fila in Registros:
                             #MontoTt= fila[0]
                            worksheet.write(row, col,   fila[0]) #Folio A12
                            worksheet.write(row, col+1, fila[1],cell_format2) #Fecha Hora Entrada B12
                            worksheet.write(row, col+2, fila[2],cell_format2) #Fecha Hora Salida C12
                            worksheet.write(row, col+3, fila[3],cell_format7) #Tiempo D12
                            worksheet.write(row, col+4, fila[4],cell_format5) #Precio E12
                            worksheet.write(row, col+5, fila[5]) #Cortes F12
                            worksheet.write(row, col+6, fila[6]) #Descripcion G12
                            worksheet.write(row, col+7, fila[7]) #Promociones H12
                            row += 1
                        #mb.showinfo("msj Registros",fila[0])
                        workbook.close()       
                        mb.showinfo("Reporte de Corte",'Reporte Guardado')     
                except:
                    #print('lo que escribiste no es un entero')
                    mb.showwarning("IMPORTANTE", "Ha ocurrido un error: Revise los datos capturados")                        
            else:
                mb.showwarning("ERROR", 'Contrasena Incorrecta')
                
    def Puertoycontar(self):
        #ser = serial.Serial('/dev/ttyAMA0', 9600)
        #Enviamos el caracter por serial, codificado en Unicode
        #entrada='e'
        #ser.write(str(entrada).encode())
        #Leemos lo que hay en el puerto y quitamos lo que no queremos
        #sArduino = str(ser.readline())
        #sArduino = "" .join([x for x in sArduino if x.isdigit()])#esto es para solo poner numeros
        #CuantosEntradas=str(self.operacion1.EntradasSensor())
        #sArduino = 1
        #CuantosEntradas = CuantosEntradas.strip('(),')
        #self.SensorEntrada.set(CuantosEntradas)
        #entrada='a'
        #ser.write(str(entrada).encode())
        #Leemos lo que hay en el puerto y quitamos lo que no queremos
        #sArduino = str(ser.readline())
        #sArduino = "" .join([x for x in sArduino if x.isdigit()])#esto es para solo poner num
        #CuantosSalidas=str(self.operacion1.SalidasSensor())
        #sArduino =1
        #CuantosSalidas = CuantosSalidas.strip('(),')
        #self.SalidaAutos.set(CuantosSalidas)
        #EntradasSen = int(self.SensorEntrada.get(),)
        #SalidasSen =  int(self.SalidaAutos.get(),)
        CuantosBoletosCobro=str(self.operacion1.CuantosBoletosCobro())
        CuantosBoletosCobro = CuantosBoletosCobro.strip('(),')
        self.BoletosCobrados.set(CuantosBoletosCobro)
        BEDCorte=str(self.operacion1.BEDCorte())
        BEDCorte = BEDCorte.strip('(),')
        self.BEDespuesCorte.set(BEDCorte)
        BAnteriores=str(self.operacion1.BAnteriores())
        BAnteriores = BAnteriores.strip('(),')
        self.BAnteriores.set(BAnteriores)
        MaxFolioCorte=str(self.operacion1.Maxfolio_Cortes())
        MaxFolioCorte=MaxFolioCorte.strip('(),')
        QuedadosBol=str(self.operacion1.Quedados_Sensor(MaxFolioCorte))
        QuedadosBol=QuedadosBol.strip('(),')
        self.BAnteriores.set(QuedadosBol)
        maxNumidIni=str(self.operacion1.MaxnumId())
        maxNumidIni = "".join([x for x in maxNumidIni if x.isdigit()])#con esto solo obtenemos los numeros
        maxNumidIni=int(maxNumidIni)
        maxFolioEntradas= str(self.operacion1.MaxfolioEntrada())
        maxFolioEntradas = "".join([x for x in maxFolioEntradas if x.isdigit()])#con esto solo obtenemos los numero
        maxFolioEntradas=int(maxFolioEntradas)
        BEDCorte=maxFolioEntradas-maxNumidIni
        BEDCorte=str(BEDCorte)
        self.BEDespuesCorte.set(BEDCorte)
        CuantosAutosdentro=str(self.operacion1.CuantosAutosdentro())
        MaxFolioCorte=str(self.operacion1.Maxfolio_Cortes())
        MaxFolioCorte=MaxFolioCorte.strip('(),')
        dentroCorte=str(self.operacion1.Quedados_Sensor(MaxFolioCorte))
        CuantosAutosdentro = CuantosAutosdentro.strip('(),')
        dentroCorte = dentroCorte.strip('(),')
        self.BDentro.set(CuantosAutosdentro)
        self.Autos_Anteriores.set(dentroCorte)
        #AutosAnteriores = int(self.Autos_Anteriores.get(),)
        #Cuantos_hay_dentro = ((AutosAnteriores + EntradasSen) - SalidasSen)
        #self.AutosEnEstacionamiento.set(Cuantos_hay_entro)
        
###################### Fin de Pagina2 Inicio Pagina3 ###############################
    def Alta_Pensionado(self):
        self.pagina4 = ttk.Frame(self.cuaderno1)
        self.cuaderno1.add(self.pagina4, text="Modulo Pensionados")
        #enmarca los controles LabelFrame 
        self.labelframe1=ttk.LabelFrame(self.pagina4, text="Pensionados")
        self.labelframe1.grid(column=0, row=0, padx=5, pady=10)
        self.lbltitulo=ttk.Label(self.labelframe1, text="--Datos del Pensionado--")
        self.lbltitulo.grid(column=0, row=0, padx=8, pady=8)
        self.lbldatos0=ttk.Label(self.labelframe1, text="Num. Tarjeta:")
        self.lbldatos0.grid(column=0, row=1, padx=4, pady=4)       
        self.lbldatos1=ttk.Label(self.labelframe1, text="Nombre Empresa:")
        self.lbldatos1.grid(column=0, row=2, padx=4, pady=4)
        self.lbldatos2=ttk.Label(self.labelframe1, text="Nombre Contacto:")
        self.lbldatos2.grid(column=0, row=3, padx=4, pady=4)
        self.lbldatos3=ttk.Label(self.labelframe1, text="Apellido Contacto:")
        self.lbldatos3.grid(column=0, row=4, padx=4, pady=4)
        self.lbldatos4=ttk.Label(self.labelframe1, text="Telefono:")
        self.lbldatos4.grid(column=0, row=5, padx=4, pady=4)
        self.lbldatos5=ttk.Label(self.labelframe1, text="Telefono Opcional:")
        self.lbldatos5.grid(column=0, row=6, padx=4, pady=4)

        self.NumTarjeta=tk.StringVar()
        self.entryNumTarjeta=ttk.Entry(self.labelframe1, width=18, textvariable=self.NumTarjeta)#state="readonly"
        #self.entryNumTarjeta.bind('<Return>',self.Validar)#con esto se lee automatico y se va a consultar
        self.entryNumTarjeta.grid(column=1, row=1)
        self.PenNombre=tk.StringVar()
        self.entryPenNombre=ttk.Entry(self.labelframe1, width=18, textvariable=self.PenNombre)
        self.entryPenNombre.grid(column=1, row=2)
        self.PenApellPat=tk.StringVar()
        self.entryPenApellPat=ttk.Entry(self.labelframe1, width=18, textvariable=self.PenApellPat)
        self.entryPenApellPat.grid(column=1, row=3)
        self.PenApellMat=tk.StringVar()
        self.entryPenApellMat=ttk.Entry(self.labelframe1, width=18, textvariable=self.PenApellMat)
        self.entryPenApellMat.grid(column=1, row=4)
        self.PenTelefonoObli=tk.StringVar()
        self.entryPenTelefonoObli=ttk.Entry(self.labelframe1, width=18, textvariable=self.PenTelefonoObli)
        self.entryPenTelefonoObli.grid(column=1, row=5)
        self.PenTelefonoOpc=tk.StringVar()
        self.entryTelefonoOpc=ttk.Entry(self.labelframe1, width=18, textvariable=self.PenTelefonoOpc)
        self.entryTelefonoOpc.grid(column=1, row=6)
        
        ######Direccion del Pensionado
        self.lbldatos6=ttk.Label(self.labelframe1, text="--Direccion del Pensionado--")
        self.lbldatos6.grid(column=2, row=0, padx=8, pady=8)
        self.lbldatos7=ttk.Label(self.labelframe1, text="Calle y Numero:")
        self.lbldatos7.grid(column=2, row=1, padx=4, pady=4) 
        self.lbldatos8=ttk.Label(self.labelframe1, text="Colonia:")
        self.lbldatos8.grid(column=2, row=2, padx=4, pady=4)
        self.lbldatos9=ttk.Label(self.labelframe1, text="Ciudad/Estado:")
        self.lbldatos9.grid(column=2, row=3, padx=4, pady=4) 
        self.lbldatos10=ttk.Label(self.labelframe1, text="C.P.:")
        self.lbldatos10.grid(column=2, row=4, padx=4, pady=4) 

        self.PenCalle=tk.StringVar()
        self.entryPenCalle=ttk.Entry(self.labelframe1, width=18, textvariable=self.PenCalle)
        self.entryPenCalle.grid(column=3, row=1, padx=4, pady=4)
        self.PenColonia=tk.StringVar()
        self.entryPenColonia=ttk.Entry(self.labelframe1, width=18, textvariable=self.PenColonia)
        self.entryPenColonia.grid(column=3, row=2, padx=4, pady=4)
        self.PenCiudad=tk.StringVar()
        self.entryPenCiudad=ttk.Entry(self.labelframe1, width=18, textvariable=self.PenCiudad)
        self.entryPenCiudad.grid(column=3, row=3, padx=4, pady=4)
        self.PenCP=tk.StringVar()
        self.entryPenCP=ttk.Entry(self.labelframe1, width=10, textvariable=self.PenCP)
        self.entryPenCP.grid(column=3, row=4, padx=4, pady=4)
        
        ######Datos del Auto
        self.lbldatos11=ttk.Label(self.labelframe1, text="--Datos del Auto--")
        self.lbldatos11.grid(column=0, row=8, padx=8, pady=8)
        self.lbldatos12=ttk.Label(self.labelframe1, text="Placas:")
        self.lbldatos12.grid(column=0, row=9, padx=4, pady=4) 
        self.lbldatos13=ttk.Label(self.labelframe1, text="Modelo:")
        self.lbldatos13.grid(column=0, row=10, padx=4, pady=4)
        self.lbldatos14=ttk.Label(self.labelframe1, text="Color:")
        self.lbldatos14.grid(column=0, row=11, padx=4, pady=4)

        self.Placas=tk.StringVar()
        self.entryPlacas=ttk.Entry(self.labelframe1, width=15, textvariable=self.Placas)
        self.entryPlacas.grid(column=1, row=9)
        self.AutoMod=tk.StringVar()
        self.entryAutoMod=ttk.Entry(self.labelframe1, width=15, textvariable=self.AutoMod)
        self.entryAutoMod.grid(column=1, row=10)
        self.AutoColor=tk.StringVar()
        self.entryAutoColor=ttk.Entry(self.labelframe1, width=15, textvariable=self.AutoColor)
        self.entryAutoColor.grid(column=1, row=11)
        
        #####Datos del Cobro
        self.lbldatos11=ttk.Label(self.labelframe1, text="--Datos del Cobro--")
        self.lbldatos11.grid(column=2, row=8, padx=8, pady=8)
        self.lbldatos12=ttk.Label(self.labelframe1, text="Monto x Mes:")
        self.lbldatos12.grid(column=2, row=9, padx=4, pady=4) 
        self.lbldatos13=ttk.Label(self.labelframe1, text="Cortesia:")
        self.lbldatos13.grid(column=2, row=10, padx=4, pady=4)
        self.lbldatos14=ttk.Label(self.labelframe1, text="Tolerancia:")
        self.lbldatos14.grid(column=2, row=11, padx=4, pady=4)
        
        self.Montoxmes=tk.StringVar()
        self.entryMontoxmes=ttk.Entry(self.labelframe1, width=15, textvariable=self.Montoxmes)
        self.entryMontoxmes.grid(column=3, row=9)
        self.comboCortesia = ttk.Combobox(self.labelframe1, width=5, justify=tk.LEFT, state="readonly")
        self.comboCortesia["values"] = ["Si", "No"]
        self.comboCortesia.current(1)
        self.comboCortesia.grid(column=3, row=10, padx=1, pady=1)
        self.Tole=tk.StringVar()
        self.entryTole=ttk.Entry(self.labelframe1, width=15, textvariable=self.Tole)
        self.entryTole.grid(column=3, row=11)
        
        #####Botones de Accion: Alta
        self.boton1=tk.Button(self.labelframe1, text="Nuevo Pensionado", command=self.Guarda_Pensionado, width=12, height=1, anchor="center")#, background="red"
        self.boton1.grid(column=0, row=20, padx=4, pady=4)
        self.boton3=tk.Button(self.labelframe1, text="Consultar", command=self.Consulta_Pensionado, width=12, height=1, anchor="center")#, background="red"
        self.boton3.grid(column=1, row=20, padx=4, pady=4)        
        self.boton4=tk.Button(self.labelframe1, text="Guardar Cambios", command=self.Modificar_Pensionado, width=12, height=1, anchor="center")#, background="red"
        self.boton4.grid(column=2, row=20, padx=4, pady=4)
        self.lbldatos21=ttk.Label(self.labelframe1, text="***CLAVE***")
        self.lbldatos21.grid(column=3, row=19, padx=4, pady=4)
        self.Clave=tk.StringVar()
        self.entryClave=ttk.Entry(self.labelframe1, width=8, textvariable=self.Clave, show="*")#, justify=tk.RIGHT
        self.entryClave.grid(column=3, row=20, padx=4, pady=4)
                
        ######Pago, Vigencia y Numero de tarjeta
        self.labelframe3=ttk.LabelFrame(self.pagina4, text="Pago Pension")
        self.labelframe3.grid(column=0, row=1, padx=5, pady=10)
        self.lbldatos20=ttk.Label(self.labelframe3, text="Num. Tarjeta:")
        self.lbldatos20.grid(column=0, row=1, padx=4, pady=4)              
        self.lbldatos16=ttk.Label(self.labelframe3, text="Monto Mensual:")#informativo
        self.lbldatos16.grid(column=0, row=2, padx=4, pady=4)
        self.lbldatos17=ttk.Label(self.labelframe3, text="Mensualidades a Pagar:")
        self.lbldatos17.grid(column=0, row=3, padx=4, pady=4)
        self.lbldatosTotal2=ttk.Label(self.labelframe3, text="")#Informativo
        self.lbldatosTotal2.grid(column=0, row=4, padx=4, pady=4)           
        self.lbldatosTotal=ttk.Label(self.labelframe3, text="")#Informativo
        self.lbldatosTotal.grid(column=1, row=4, padx=4, pady=4)                         
        self.lbldatosCortesia=ttk.Label(self.labelframe3, text="")#Informativo
        self.lbldatosCortesia.grid(column=3, row=1, padx=4, pady=4)                 
        self.lbldatos18=ttk.Label(self.labelframe3, text="Vigencia:")#Informativo
        self.lbldatos18.grid(column=3, row=2, padx=4, pady=4)         
        self.lbldatos19=ttk.Label(self.labelframe3, text="Estatus:")#informativo
        self.lbldatos19.grid(column=3, row=3, padx=4, pady=4)         
        
        self.NumTarjeta3=tk.StringVar()
        self.entryNumTarjeta3=ttk.Entry(self.labelframe3, width=15, textvariable=self.NumTarjeta3)#state="readonly"
        self.entryNumTarjeta3.bind('<Return>',self.ConsulPagoPen)#con esto se lee automatico y se va a consultar
        self.entryNumTarjeta3.grid(column=1, row=1) #ConsulPagoPen
                
        self.Monto=tk.StringVar()
        self.entryMonto=ttk.Entry(self.labelframe3, width=10, textvariable=self.Monto, state="readonly")
        self.entryMonto.grid(column=1, row=2)
        self.comboMensual = ttk.Combobox(self.labelframe3, width=8, justify=tk.RIGHT, state="readonly")
        self.comboMensual["values"] = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
        self.comboMensual.bind('<Return>',self.CalculaPagoPen)#Calcula el monto a pagar
        self.comboMensual.current(0)
        self.comboMensual.grid(column=1, row=3, padx=1, pady=1)
        self.Vigencia=tk.StringVar()
        self.entryVigencia=ttk.Entry(self.labelframe3, width=15, textvariable=self.Vigencia, state="readonly")
        self.entryVigencia.grid(column=4, row=2)
        self.Estatus=tk.StringVar()
        self.entryEstatus=ttk.Entry(self.labelframe3, width=15, textvariable=self.Estatus, state="readonly")#Informativo
        self.entryEstatus.grid(column=4, row=3, padx=4, pady=4)
        #####Botones de Accion: Pagar
        self.boton2=tk.Button(self.labelframe3, text="Cobrar Pension", command=self.Cobro_Pensionado, width=12, height=1, anchor="center", background="red")#, background="red"
        self.boton2.grid(column=4, row=10, padx=4, pady=4)

        ######Muestra de Pensionados Adentro
        self.labelframe4=ttk.LabelFrame(self.pagina4, text="Consulta")
        self.labelframe4.grid(column=1, row=0, padx=5, pady=10)
        self.lbldatos22=ttk.Label(self.labelframe4, text="---Pensionados Adentro---")
        self.lbldatos22.grid(column=0, row=1, padx=4, pady=4)
        self.scrolledPen=st.ScrolledText(self.labelframe4, width=28, height=7)
        self.scrolledPen.grid(column=0,row=2, padx=10, pady=10)
        self.lbldatosTotPen=ttk.Label(self.labelframe4, text="")
        self.lbldatosTotPen.grid(column=0, row=4, padx=4, pady=4)        

        self.boton5=tk.Button(self.labelframe4, text="Consultar", command=self.PenAdentro, width=12, height=1, anchor="center")#, background="red"
        self.boton5.grid(column=0, row=6, padx=4, pady=4)
        
        ######Reportes de Pensionados
        self.labelframe5=ttk.LabelFrame(self.pagina4, text="Reportes")
        self.labelframe5.grid(column=1, row=1, padx=5, pady=10)
        self.lbldatos24=ttk.Label(self.labelframe5, text="---Reportes Pensionados ---")
        self.lbldatos24.grid(column=0, row=1, padx=4, pady=4)


        self.boton6=tk.Button(self.labelframe5, text="REPORTE", command=self.Cobro_Pensionado, width=12, height=1, anchor="center")#, background="red"
        self.boton6.grid(column=0, row=4, padx=4, pady=4)
        
        
        #self.Adentroframe=ttk.LabelFrame(self.pagina1, text="Autos DENTRO")
        #self.Adentroframe.grid(column=2, row=0, padx=0, pady=0)
        #self.MaxId=tk.StringVar()
        #self.entryMaxId=ttk.Entry(self.labelframe1, width=10, textvariable=self.MaxId, state="readonly")
        #self.entryMaxId.grid(column=1, row=0, padx=4, pady=4)

    def Guarda_Pensionado(self):
        contrasena= str(self.entryClave.get(), )
        if len(contrasena) == 0:
           mb.showwarning("IMPORTANTE", "Debe capturar la CLAVE para ejecutar las acciones")
        elif contrasena == "P4s3":
            try:     
                ##Generales
                numtarjeta=str(self.NumTarjeta.get(),) #self.NumTarjeta=tk.StringVar()
                Nombre=str(self.PenNombre.get(), )
                ApellidoPat=str(self.PenApellPat.get(), )
                ApellidoMat=str(self.PenApellMat.get(), )
                Telefono1=str(self.PenTelefonoObli.get(), )
                Telefono2=str(self.PenTelefonoOpc.get(), )
                fechaAlta=date.today()
                ##Direccion
                Calle=str(self.PenCalle.get(), )
                Colonia=str(self.PenColonia.get(), )
                Ciudad=str(self.PenCiudad.get(), )
                CP=str(self.PenCP.get(), )
                ##Auto
                Placa=str(self.Placas.get(), )
                Modelo=str(self.AutoMod.get(), )
                Color=str(self.AutoColor.get(), )
                ##Pago
                cortesia=str(self.comboCortesia.get(), )
                montomes=str(self.Montoxmes.get(), )
                if cortesia == "Si" :
                    montoxmes = 1 ###Si el Pensionado tiene cortesia, no es necesario el monto a cobrar
                elif cortesia == "No" and len(montomes) == 0:
                    mb.showwarning("IMPORTANTE", "Debe capturar el Monto Mensual")
                    self.entryMontoxme.focus()
                    return False
                else:
                    montoxmes = int(self.Montoxmes.get(), )
                tolerancia=int(self.Tole.get(), )
                #mb.showwarning("IMPORTANTE", str(len(numtarjeta)))            
                if len(numtarjeta) == 0 :
                    mb.showwarning("IMPORTANTE", "Debe Leer el Numero de Tarjeta")
                    return False
                elif len(Nombre) == 0 :
                    mb.showwarning("IMPORTANTE", "Debe capturar el Nombre del pensionado")
                    return False
                elif len(ApellidoPat) == 0 :
                    mb.showwarning("IMPORTANTE", "Debe capturar el Apellido paterno del pensionado")
                    return False
                elif len(Telefono1) == 0 :
                    mb.showwarning("IMPORTANTE", "Debe capturar Numero Telefonico del pensionado")
                    return False
                elif len(Calle) == 0 :
                    mb.showwarning("IMPORTANTE", "Debe capturar el dato de Calle")
                    return False
                elif len(Colonia) == 0 :
                    mb.showwarning("IMPORTANTE", "Debe capturar el dato de Colonia")
                    return False
                elif len(Ciudad) == 0 :
                    mb.showwarning("IMPORTANTE", "Debe capturar el dato de Ciudad")
                    return False
                elif len(CP) == 0 :
                    mb.showwarning("IMPORTANTE", "Debe capturar el Codigo Postal")
                    return False
                elif len(Placa) == 0 :
                    mb.showwarning("IMPORTANTE", "Debe capturar el numero de Placa del auto")        
                    return False
                elif len(Modelo) == 0 :
                    mb.showwarning("IMPORTANTE", "Debe capturar el Modelo de auto")
                    return False
                elif montoxmes <= 0 :
                    mb.showwarning("IMPORTANTE", "Debe capturar un Monto mayor a Cero")
                    return False
                elif tolerancia is None :
                    mb.showwarning("IMPORTANTE", "Debe capturar La Tolerancia a dar al Pensionado")
                    return False
                elif tolerancia < 0 :
                    mb.showwarning("IMPORTANTE", "Debe capturar La Tolerancia a dar al Pensionado debe ser mayor a cero")
                    return False
                else :
                    #print("paso")
                    tarjeta=int(numtarjeta)
                    #print(str(tarjeta))
                    Existe=self.operacion1.ValidarRFID(tarjeta)
                    #mb.showwarning("IMPORTANTE", Existe)
                    if len(Existe) != 0 :
                        mb.showwarning("IMPORTANTE", "Numero de tarjeta ya asignado")
                        self.NumTarjeta.set("")
                        self.entryNumTarjeta.focus()
                        return False
                    else:
                        datos=(numtarjeta, Nombre, ApellidoPat, ApellidoMat, fechaAlta, Telefono1, Telefono2, Ciudad, Colonia, CP, Calle, Placa, Modelo, Color, montoxmes, cortesia, tolerancia)
                        #mb.showwarning("GUARDO")
                        self.operacion1.AltaPensionado(datos)
                        self.NumTarjeta.set("")
                        self.PenNombre.set("")
                        self.PenApellPat.set("")
                        self.PenApellMat.set("")
                        self.PenTelefonoObli.set("")
                        self.PenTelefonoOpc.set("")
                        self.PenCalle.set("")
                        self.PenColonia.set("")
                        self.PenCiudad.set("")
                        self.PenCP.set("")
                        self.Placas.set("")
                        self.AutoMod.set("")
                        self.AutoColor.set("")
                        self.Vigencia.set("")
                        self.Estatus.set("")
                        self.Montoxmes.set("")
                        self.comboCortesia.current(0)
                        self.Tole.set("")
                        self.Clave.set("")
                        self.entryNumTarjeta.focus()
                        mb.showinfo("Alta de Pensionados",'Pensionado Guardado') 
            except:
                mb.showwarning("IMPORTANTE", "Ha ocurrido un error: Revise los datos capturados")
        else:
            mb.showwarning("ERROR", 'CLAVE Incorrecta')
        
    def Consulta_Pensionado(self):                
        contrasena= str(self.entryClave.get(), )
        if len(contrasena) == 0:
            mb.showwarning("IMPORTANTE", "Debe capturar la CLAVE para ejecutar las acciones")
        elif contrasena == "P4s3":
                ##Generales
            numtarjeta=str(self.NumTarjeta.get(), )#self.NumTarjeta=tk.StringVar()
            #mb.showwarning("IMPORTANTE", numtarjeta)
            try:
                if len(numtarjeta) == 0 :
                    mb.showwarning("IMPORTANTE", "Debe Leer primero el Numero de Tarjeta")
                    self.PenNombre.set("")
                    self.PenApellPat.set("")
                    self.PenApellMat.set("")
                    self.PenTelefonoObli.set("")
                    self.PenTelefonoOpc.set("")
                    self.PenCalle.set("")
                    self.PenColonia.set("")
                    self.PenCiudad.set("")
                    self.PenCP.set("")
                    self.Placas.set("")
                    self.AutoMod.set("")
                    self.AutoColor.set("")
                    self.Vigencia.set("")
                    self.Estatus.set("")
                    self.Montoxmes.set("")
                    self.comboCortesia.current(0)
                    self.Tole.set("")
                    self.Clave.set("")
                    self.entryNumTarjeta.focus()            
                    return False
                else :
                    tarjeta=int(numtarjeta)
                    Existe=self.operacion1.ValidarRFID(tarjeta)
                    #print(Existe)
                    #mb.showwarning("IMPORTANTE", Existe)
                    if Existe == None :
                        mb.showwarning("IMPORTANTE", "No existe Cliente para ese Num de Tarjeta")
                        self.NumTarjeta.set("")               
                        self.entryNumTarjeta.focus()
                        return False
                    else:
                        global PensionadoOpen #reasignamos valor a la Variable global
                        PensionadoOpen=Existe #Cachamos el Id_cliente por si se hacen modificaciones
                        respuesta=self.operacion1.ConsultaPensionado(Existe)
                        #print("Pensionado dese Consulta") #print(PensionadoOpen)
                        #Nom_cliente, Apell1_cliente, Apell2_cliente, Telefono1, Telefono2, Ciudad, Colonia, CP, Calle_num, Placas, Modelo_auto, Color_auto, Fecha_vigencia, Estatus
                        for fila in respuesta:
                            #self.NumTarjeta.set(numtarjeta)
                            self.PenNombre.set(str(fila[0]))
                            self.PenApellPat.set(str(fila[1]))
                            self.PenApellMat.set(str(fila[2]))
                            self.PenTelefonoObli.set(str(fila[3]))
                            self.PenTelefonoOpc.set(str(fila[4]))
                            self.PenCiudad.set(str(fila[5]))
                            self.PenCalle.set(str(fila[8]))
                            self.PenColonia.set(str(fila[6]))                  
                            self.PenCP.set(str(fila[7]))
                            self.Placas.set(str(fila[9]))
                            self.AutoMod.set(str(fila[10]))
                            self.AutoColor.set(str(fila[11]))
                            self.Vigencia.set(str(fila[12]))
                            self.Estatus.set(str(fila[14]))
                            self.Montoxmes.set(str(fila[15]))
                            if str(fila[16]) == "Si":
                                self.comboCortesia.current(0)
                            else:
                                self.comboCortesia.current(1)
                            self.Tole.set(str(fila[17]))
                            self.Clave.set("")
                            self.entryNumTarjeta.focus()
            except:
                mb.showwarning("IMPORTANTE", "Ha ocurrido un error: Revise los datos capturados")
        else:
            mb.showwarning("ERROR", 'CLAVE Incorrecta')
    ###IMPORTANTE: SE PUEDE MODIFICAR EL # DE TARJETA, ASÍ QUE DESDE QUE SE CONSULTA ASIGNAR A UNA VARIBLE
            ##GLOBAL EL ID DEL CLIENTE PARA GUARDAR LOS CAMBIOS. POR SI CAMBIAN EL NUMERO DE TARJETA
    def Modificar_Pensionado(self):                
        contrasena= str(self.entryClave.get(), )
        if len(contrasena) == 0:
           mb.showwarning("IMPORTANTE", "Debe capturar la CLAVE para ejecutar las acciones")
        elif contrasena == "P4s3":
            try:     
                ##Generales
                numtarjeta=str(self.NumTarjeta.get(),) #self.NumTarjeta=tk.StringVar()
                Nombre=str(self.PenNombre.get(), )
                ApellidoPat=str(self.PenApellPat.get(), )
                ApellidoMat=str(self.PenApellMat.get(), )
                Telefono1=str(self.PenTelefonoObli.get(), )
                Telefono2=str(self.PenTelefonoOpc.get(), )
                fechaCambio=date.today()
                ##Direccion
                Calle=str(self.PenCalle.get(), )
                Colonia=str(self.PenColonia.get(), )
                Ciudad=str(self.PenCiudad.get(), )
                CP=str(self.PenCP.get(), )
                ##Auto
                Placa=str(self.Placas.get(), )
                Modelo=str(self.AutoMod.get(), )
                Color=str(self.AutoColor.get(), )
                ##Pago
                cortesia=str(self.comboCortesia.get(), )
                montomes=str(self.Montoxmes.get(), )
                if cortesia == "Si" :
                    montoxmes = 1 ###Si el Pensionado tien cortesia, no es necesario el monto a cobrar
                elif cortesia == "No" and len(montomes) == 0:
                    mb.showwarning("IMPORTANTE", "Debe capturar el Monto Mensual")
                    self.entryMontoxme.focus()
                    return False
                else:
                    montoxmes = int(self.Montoxmes.get(), )
                tolerancia=int(self.Tole.get(), )
                #mb.showwarning("IMPORTANTE", str(len(numtarjeta)))            
                if len(numtarjeta) == 0 :
                    mb.showwarning("IMPORTANTE", "Debe Leer el Numero de Tarjeta")
                    return False
                elif len(Nombre) == 0 :
                    mb.showwarning("IMPORTANTE", "Debe capturar el Nombre del pensionado")
                    return False
                elif len(ApellidoPat) == 0 :
                    mb.showwarning("IMPORTANTE", "Debe capturar el Apellido paterno del pensionado")
                    return False
                elif len(Telefono1) == 0 :
                    mb.showwarning("IMPORTANTE", "Debe capturar Numero Telefonico del pensionado")
                    return False
                elif len(Calle) == 0 :
                    mb.showwarning("IMPORTANTE", "Debe capturar el dato de Calle")
                    return False
                elif len(Colonia) == 0 :
                    mb.showwarning("IMPORTANTE", "Debe capturar el dato de Colonia")
                    return False
                elif len(Ciudad) == 0 :
                    mb.showwarning("IMPORTANTE", "Debe capturar el dato de Ciudad")
                    return False
                elif len(CP) == 0 :
                    mb.showwarning("IMPORTANTE", "Debe capturar el Codigo Postal")
                    return False
                elif len(Placa) == 0 :
                    mb.showwarning("IMPORTANTE", "Debe capturar el numero de Placa del auto")
                    return False
                elif len(Modelo) == 0 :
                    mb.showwarning("IMPORTANTE", "Debe capturar el Modelo de auto")
                    return False
                elif montoxmes <= 0 :
                    mb.showwarning("IMPORTANTE", "Debe capturar un Monto mayor a Cero")
                    return False
                elif tolerancia is None :
                    mb.showwarning("IMPORTANTE", "Debe capturar La Tolerancia a dar al Pensionado")
                    return False
                elif tolerancia < 0 :
                    mb.showwarning("IMPORTANTE", "Debe capturar La Tolerancia a dar al Pensionado debe ser mayor a cero")
                    return False
                else :
                    #print("Pensionado dese Modificar") #print(PensionadoOpen)
                    datos=(numtarjeta, Nombre, ApellidoPat, ApellidoMat, Telefono1, Telefono2, Ciudad, Colonia, CP, Calle, Placa, Modelo, Color, montoxmes, cortesia, tolerancia, fechaCambio, PensionadoOpen)
                    #mb.showwarning("GUARDO")
                    self.operacion1.ModificarPensionado(datos)
                    self.NumTarjeta.set("")
                    self.PenNombre.set("")
                    self.PenApellPat.set("")
                    self.PenApellMat.set("")
                    self.PenTelefonoObli.set("")
                    self.PenTelefonoOpc.set("")
                    self.PenCalle.set("")
                    self.PenColonia.set("")
                    self.PenCiudad.set("")
                    self.PenCP.set("")
                    self.Placas.set("")
                    self.AutoMod.set("")
                    self.AutoColor.set("")
                    self.Vigencia.set("")
                    self.Estatus.set("")
                    self.Montoxmes.set("")
                    self.comboCortesia.current(0)
                    self.Tole.set("")
                    self.Clave.set("")
                    self.entryNumTarjeta.focus()
                    #global PensionadoOpen #reasignamos valor a la Variable global 
                    #PensionadoOpen=0
                    mb.showinfo("Modificar Información",'Los Cambios al pensionado se han guardado') 
            except:
                mb.showwarning("IMPORTANTE", "Ha ocurrido un error: Revise los datos capturados")
        else:
            mb.showwarning("ERROR", 'CLAVE Incorrecta')
    
    def ConsulPagoPen(self,event):
        numtarjeta=str(self.NumTarjeta3.get(), )
        #print("entro")
        if len(numtarjeta) == 0 :
            mb.showwarning("IMPORTANTE", "Debe Leer el Numero de Tarjeta")
        else :
            tarjeta=int(numtarjeta)
            #print(numtarjeta)
            Existe=self.operacion1.ValidarRFID(tarjeta)
            if len(Existe) == 0 :
                mb.showwarning("IMPORTANTE", "No existe Cliente para ese Num de Tarjeta")
                self.NumTarjeta3.set("")               
                self.entryNumTarjeta3.focus()
                return False
            else:
                respuesta=self.operacion1.ConsultaPensionado(Existe)
                #Nom_cliente 0, Apell1_cliente 1, Apell2_cliente 2, Telefono1 3, Telefono2 4, Ciudad 5, Colonia 6,
                #CP 7, Calle_num 8, Placas 9, Modelo_auto 10, Color_auto 11, Fecha_vigencia 12, Estatus 13,
                #Vigencia 14, Monto 15, Cortesia 16, Tolerancia 17
                for fila in respuesta:
                    self.lbldatosCortesia.configure(text=" ")
                    self.lbldatosTotal.configure(text=" ")
                    self.lbldatosTotal2.configure(text=" ")
                    self.comboMensual.current(0)
                    VigAct=fila[12]
                    Estatus=fila[14]
                    monto=fila[15]
                    cortesia=fila[16]
                    self.Vigencia.set(VigAct)
                    self.Estatus.set(Estatus)
                    #print(cortesia)
                    if cortesia == "Si" :
                        self.Monto.set("")
                        self.lbldatosCortesia.configure(text="         Cliente con CORTESIA")
                        self.lbldatosTotal2.configure(text="COBRAR PENSION: ")
                        self.lbldatosTotal.configure(text="Para renovar la Cortesía")
                    else : 
                        self.Monto.set(monto)
                        self.lbldatosTotal2.configure(text="IMPORTANTE: ")
                        self.lbldatosTotal.configure(text="ELIJA LAS MENSUALIDADES A PAGAR")
                    self.comboMensual.focus()

    def CalculaPagoPen(self,event):
        monto=str(self.Monto.get(), )
        mes=int(self.comboMensual.get(), )
        if len(monto) == 0:
            mb.showwarning("IMPORTANTE", "El Pensionado cuenta con Cortesía")
        else:
            self.lbldatosCortesia.configure(text=" ")
            self.lbldatosTotal.configure(text=" ")
            self.lbldatosTotal2.configure(text=" ")
            monto=int(monto)
            pago=monto*mes #Calculando monto a pagar
            print(pago)
            self.lbldatosTotal.configure(text="TOTAL A PAGAR:   "+str(pago))
            

    def Cobro_Pensionado(self):
        numtarjeta=str(self.NumTarjeta3.get(), )#self.NumTarjeta=tk.StringVar()
        #mb.showwarning("IMPORTANTE", numtarjeta)
        try:
            #Generales
            mes=int(self.comboMensual.get(), )
            fechaPago=date.today()
            print(mes)
            if len(numtarjeta) == 0 :
                mb.showwarning("IMPORTANTE", "Debe Leer el Numero de Tarjeta")
                self.comboMensual.current(0)
                self.entryNumTarjeta.focus()            
                return False
            else :
                print("entro")
                tarjeta=int(numtarjeta)
                Existe=self.operacion1.ValidarRFID(tarjeta)
                #mb.showwarning("IMPORTANTE", Existe)
                if len(Existe) == 0 :
                    mb.showwarning("IMPORTANTE", "No existe Cliente para ese Num de Tarjeta")
                    self.NumTarjeta.set("")               
                    self.entryNumTarjeta.focus()
                    return False
                else:
                    respuesta=self.operacion1.ConsultaPensionado(Existe)
                    #Nom_cliente 0, Apell1_cliente 1, Apell2_cliente 2, Telefono1 3, Telefono2 4, Ciudad 5, Colonia 6,
                    #CP 7, Calle_num 8, Placas 9, Modelo_auto 10, Color_auto 11, Fecha_vigencia 12, Estatus 13,
                    #Vigencia 14, Monto 15, Cortesia 16, Tolerancia 17
                    for fila in respuesta:
                        VigAct=fila[12]
                        #VigActShow= datetime.strptime(VigAct, '%Y-%m-%d')
                        Estatus=fila[14]
                        monto=fila[15]
                        cortesia=fila[16]
                        self.Vigencia.set(VigAct)
                        self.Estatus.set(Estatus)
                        self.entryNumTarjeta.focus()
                    #Calculando la Nueva Vigencia apartir del dia de Pago
                    #mb.showwarning("IMPORTANTE", VigAct)
                    dias= 30*mes
                    pago=monto*mes #Calculando monto a pagar
                    if cortesia == "Si" :
                        pago=0
                    if VigAct == None:
                        NvaVigencia= date.today() + timedelta(days = dias) #Primer pago del Pensionado
                    elif VigAct <= datetime.today():
                        NvaVigencia= date.today() + timedelta(days = dias) #Cuando la Vigencia ya vencio
                    else :                  
                        NvaVigencia= VigAct + timedelta(days = dias) #Cuando la Vigencia, sigue vigente
                    #mb.showwarning("IMPORTANTE", NvaVigencia)
                    datos=(Existe, tarjeta, fechaPago, NvaVigencia, mes, pago)
                    datos1=('Activo', NvaVigencia, pago, Existe)
                    #sql="INSERT INTO PagosPens(id_cliente, num_tarjeta, Fecha_pago, Fecha_vigencia, Mensualidad, Monto) values (%s,%s,%s,%s,%s,%s)"
                    self.operacion1.CobrosPensionado(datos)
                    self.operacion1.UpdPensionado(datos1)
                    self.lbldatosCortesia.configure(text=" ")
                    self.lbldatosTotal.configure(text=" ")
                    self.lbldatosTotal2.configure(text=" ")
                    self.Monto.set("")
                    self.Vigencia.set("")
                    self.Estatus.set("")
                    self.comboMensual.current(0)
                    self.NumTarjeta3.set("")
                    self.entryNumTarjeta3.focus()
                    mb.showinfo("Pago de Pension",'Pago de pension realizado')
        except:
            mb.showwarning("IMPORTANTE", "Ha ocurrido un error: Revise los datos capturados")
            self.Monto.set("")
            self.comboMensual.current(0)
            self.Vigencia.set("")
            self.Estatus.set("")
            self.NumTarjeta3.set("")
            self.entryNumTarjeta3.focus()
            
    def PenAdentro(self):
        respuesta=self.operacion1.TreaPenAdentro()
        self.scrolledPen.delete("1.0", tk.END)
        cont=1
        for fila in respuesta:
            self.scrolledPen.insert(tk.END, str(cont)+") "+str(fila[0])+"-"+str(fila[1])+"\n\n")
            cont=cont+1
        self.lbldatosTotPen.configure(text="PENSIONADOS ADENTRO: "+str(cont-1))
        
                
                
aplicacion1=FormularioOperacion()