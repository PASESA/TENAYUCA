
from datetime import datetime, date, time, timedelta
from dateutil.relativedelta import relativedelta
formato = "%H:%M:%S"
PensionadoOpen=1
AutoPago=1
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
import traceback
import operacion
import time
import xlsxwriter
import os
import serial
TipoPromocion = 1


###--###
p = Usb(0x04b8, 0x0e15, 0)
penalizacion_con_importe = True



class FormularioOperacion:
    def __init__(self):
        #creamos un objeto que esta en el archivo operacion dentro la clase Operacion
        self.operacion1=operacion.Operacion()
        self.ventana1=tk.Tk()
        self.ventana1.title("TENAYUCA COBRO")
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

        self.scrolledtext=st.ScrolledText(self.Adentroframe, width=28, height=7)
        self.scrolledtext.grid(column=1,row=0, padx=4, pady=4)

        self.boton1=tk.Button(self.labelframe1, text="Generar Entrada", command=self.agregarRegistroRFID, width=13, height=3, anchor="center", background="red")
        self.boton1.grid(column=1, row=4, padx=4, pady=4)
        self.Autdentro=tk.Button(self.Adentroframe, text="Boletos sin Cobro", command=self.Autdentro, width=15, height=1, anchor="center")
        self.Autdentro.grid(column=2, row=0, padx=4, pady=4)
        self.boton2=tk.Button(self.pagina1, text="Salir del programa", command=self.Cerrar_Programa, width=15, height=1, anchor="center", background="red")
        self.boton2.grid(column=0, row=0, padx=4, pady=4)

    def Autdentro(self):   
        respuesta=self.operacion1.Autos_dentro()
        self.scrolledtext.delete("1.0", tk.END)
        for fila in respuesta:
            self.scrolledtext.insert(tk.END, "Entrada num: "+str(fila[0])+"\nEntro: "+str(fila[1])[:-3]+"\n\n")

    def agregarRegistroRFID(self):
        #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$impresion    $$$$$$$$$$$$$$$$$$$
        MaxFolio=str(self.operacion1.MaxfolioEntrada())
        MaxFolio = MaxFolio.strip("[(,)]")
        n1 = MaxFolio
        n2 = "1"
        masuno = int(n1)+int(n2)
        masuno = str(masuno)
        self.MaxId.set(masuno)

        folio_cifrado = self.operacion1.cifrar_folio(folio = masuno)
        print(f"Folio cifrado: {folio_cifrado}")

        #Generar QR
        self.operacion1.generar_QR(folio_cifrado)

        fechaEntro = datetime.today()
        fechaEntro = fechaEntro - timedelta(minutes = 1, seconds = fechaEntro.second)

        horaentrada = str(fechaEntro)
        horaentrada=horaentrada[:19]
        self.labelhr.configure(text=(horaentrada[:-3], "Entró"))
        corteNum = 0
        placa=str(self.Placa.get(), )
        datos=(fechaEntro, corteNum, placa)

        p.image("LOGO1.jpg")
        p.text("--------------------------------------\n")
        p.set(align="center")
        p.text("BOLETO DE ENTRADA\n")
        folioZZ=('FOLIO 000' + masuno)
        p.text('Entro: '+horaentrada[:-3]+'\n')
        p.text('Placas '+placa+'\n')
        p.text(folioZZ+'\n')
        p.set(align = "center")
        p.image("reducida.png")
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
        self.FOLIO_QR=ttk.LabelFrame(self.pagina2, text="FOLIO_QR")
        self.FOLIO_QR.grid(column=0, row=0, padx=5, pady=10, sticky=tk.NW)

        self.labelframe2=ttk.LabelFrame(self.FOLIO_QR, text="Autos")
        self.labelframe2.grid(column=0, row=0, padx=5, pady=10, sticky=tk.NW)
        self.label1=ttk.Label(self.labelframe2, text="Lector QR")
        self.label1.grid(column=0, row=0, padx=4, pady=4)
        self.label3=ttk.Label(self.labelframe2, text="Entro:")
        self.label3.grid(column=0, row=1, padx=4, pady=4)
        self.label4=ttk.Label(self.labelframe2, text="Salio:")
        self.label4.grid(column=0, row=2, padx=4, pady=4)


        self.labelpromo=ttk.LabelFrame(self.FOLIO_QR, text="Leer el QR de Promocion")
        self.labelpromo.grid(column=0, row=1, padx=5, pady=10, sticky=tk.NW)
        self.promolbl1=ttk.Label(self.labelpromo, text="Codigo QR")
        self.promolbl1.grid(column=0, row=0, padx=4, pady=4)
        self.promolbl2=ttk.Label(self.labelpromo, text="Tipo Prom")
        self.promolbl2.grid(column=0, row=1, padx=4, pady=4)


        self.labelcuantopagas=ttk.LabelFrame(self.FOLIO_QR, text='cual es el pago')
        self.labelcuantopagas.grid(column=0,row=2, padx=5, pady=10, sticky=tk.NW)
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


        #en otro frame
        self.labelframe3_principal=ttk.LabelFrame(self.pagina2, text="Datos del COBRO")
        self.labelframe3_principal.grid(column=1, row=0, pady=10, sticky=tk.NW)

        self.labelframe3=ttk.LabelFrame(self.labelframe3_principal, text="Tiempo y Salida")
        self.labelframe3.grid(column=0, row=0, padx=5, pady=10, sticky=tk.NW)
        self.lbl1=ttk.Label(self.labelframe3, text="Hr Salida")
        self.lbl1.grid(column=0, row=1, padx=4, pady=4)
        self.lbl2=ttk.Label(self.labelframe3, text="TiempoTotal")
        self.lbl2.grid(column=0, row=2, padx=4, pady=4)
        self.lbl3=ttk.Label(self.labelframe3, text="Importe")
        self.lbl3.grid(column=0, row=3, padx=4, pady=4)


        self.IImporte = ttk.Label(self.labelframe3, text="") #Creación del Label
        self.IImporte.config(width =4)
        self.IImporte.config(background="white") #Cambiar color de fondo
        self.IImporte.config(font=('Arial', 48)) #Cambiar tipo y tamaño de fuente
        self.IImporte.grid(column=1, row=4, padx=0, pady=0)   


        #se crea objeto para MOSTRAR LA HORA DEL CALCULO
        self.copia=tk.StringVar()
        self.entrycopia=tk.Entry(self.labelframe3, width=15, textvariable=self.copia, state = "readonly")
        self.entrycopia.grid(column=1, row=1)
        #SE CREA UN OBJETO caja de texto IGUAL A LOS DEMAS Y MUESTRA EL TOTAL DEL TIEMPO
        self.ffeecha=tk.StringVar()
        self.ffeecha_auxiliar=tk.StringVar()
        self.entryffeecha=tk.Entry(self.labelframe3, width=15, textvariable=self.ffeecha_auxiliar, state= "readonly")
        self.entryffeecha.grid(column=1, row=2)
        #SE CREA UN OBJETO caja de texto IGUAL A LOS DEMAS para mostrar el importe y llevarlo a guardar en BD
        self.importe=tk.StringVar()
        self.entryimporte=tk.Entry(self.labelframe3, width=15, textvariable=self.importe, state= "readonly")
        self.entryimporte.grid(column=1, row=3)


        self.scrol_datos_boleto_cobrado=st.ScrolledText(self.labelframe3_principal, width=28, height=7)
        self.scrol_datos_boleto_cobrado.grid(column=0, row=1, padx=5, pady=10)


        self.labelPerdido_principal=ttk.LabelFrame(self.pagina2, text="")
        self.labelPerdido_principal.grid(column=2,row=0, pady=10, sticky=tk.NW)

        self.labelPerdido=ttk.LabelFrame(self.labelPerdido_principal, text="Boleto Perdido/Dañado")
        self.labelPerdido.grid(column=0,row=0,padx=5, pady=10, sticky=tk.NW)


        self.label_frame_folio=ttk.LabelFrame(self.labelPerdido, text="FOLIO")
        self.label_frame_folio.grid(column=0,row=0,padx=5, pady=10, sticky=tk.NW)


        self.lblFOLIO=ttk.Label(self.label_frame_folio, text="INGRESE FOLIO", font=("Arial", 11))
        self.lblFOLIO.grid(column=0, row=0, sticky=tk.NW,padx=5, pady=5)

        self.PonerFOLIO=tk.StringVar()
        self.entryPonerFOLIO=tk.Entry(self.label_frame_folio, width=15, textvariable=self.PonerFOLIO, font=("Arial", 11))
        self.entryPonerFOLIO.grid(column=1, row=0, sticky=tk.NW,padx=5, pady=5)


        self.label_botones_boletos_perdido=ttk.LabelFrame(self.labelPerdido, text="BOLETO DAÑADO/PERDIDO")
        self.label_botones_boletos_perdido.grid(column=0,row=1,padx=5, pady=10, sticky=tk.NW)

        self.boton_boleto_dañado=tk.Button(self.label_botones_boletos_perdido, text="Boleto Dañado", command=self.BoletoDañado, width=10, height=3, anchor="center", font=("Arial", 10))
        self.boton_boleto_dañado.grid(column=0, row=1, sticky=tk.NE, padx=10, pady=5)

        self.boton3=tk.Button(self.label_botones_boletos_perdido, text="Boleto Perdido\nCON FOLIO", command=self.BoletoPerdido_conFolio, width=10, height=3, anchor="center", font=("Arial", 10))
        self.boton3.grid(column=1, row=1, sticky=tk.NE, padx=10, pady=5)

        self.boton3=tk.Button(self.label_botones_boletos_perdido, text="Boleto Perdido\nSIN FOLIO", command=self.BoletoPerdido_sinFolio, width=10, height=3, anchor="center", font=("Arial", 10))
        self.boton3.grid(column=2, row=1, sticky=tk.NE, padx=10, pady=5)




        self.labelPerdido2=ttk.LabelFrame(self.labelPerdido_principal, text="Boletos sin cobro")
        self.labelPerdido2.grid(column=0,row=1,padx=5, pady=10, sticky=tk.NW)

        self.boton2=tk.Button(self.labelPerdido2, text="B./SIN cobro", command=self.BoletoDentro, width=10, height=2, anchor="center")
        self.boton2.grid(column=0, row=0)

        self.scrolledtxt=st.ScrolledText(self.labelPerdido2, width=28, height=7)
        self.scrolledtxt.grid(column=1,row=0, padx=10, pady=10)





        self.label15=ttk.Label(self.pagina2, text="Viabilidad de COBRO")
        self.label15.grid(column=1, row=2, padx=0, pady=0)
        #se crea objeto para ver pedir el folio la etiqueta con texto
        self.folio=tk.StringVar()
        self.entryfolio=tk.Entry(self.labelframe2, textvariable=self.folio)
        self.entryfolio.bind('<Return>',self.consultar)#con esto se lee automatico y se va a consultar
        self.entryfolio.grid(column=1, row=0, padx=4, pady=4)
        #se crea objeto para mostrar el dato de la  Entrada solo lectura
        self.descripcion=tk.StringVar()
        self.entrydescripcion=ttk.Entry(self.labelframe2, textvariable=self.descripcion, state="readonly",  width=15)
        self.entrydescripcion.grid(column=1, row=1, padx=4, pady=4, sticky=tk.NW)
        #se crea objeto para mostrar el dato la Salida solo lectura
        self.precio=tk.StringVar()
        self.entryprecio=ttk.Entry(self.labelframe2, textvariable=self.precio, state="readonly",  width=15)
        self.entryprecio.grid(column=1, row=2, padx=4, pady=4, sticky=tk.NW)

        #creamos un objeto para obtener la lectura de la PROMOCION
        self.promo=tk.StringVar()
        self.entrypromo=tk.Entry(self.labelpromo, textvariable=self.promo)
        self.entrypromo.bind('<Return>',self.CalculaPromocion)#con esto se lee automatico
        self.entrypromo.grid(column=1, row=0, padx=4, pady=4)           
        #este es donde pongo el tipo de PROMOCION
        self.PrTi=tk.StringVar()
        self.entryPrTi=tk.Entry(self.labelpromo, width=20, textvariable=self.PrTi, state= "readonly")
        self.entryPrTi.grid(column=1, row=1)
        #botones


        self.bcambio=tk.Button(self.labelcuantopagas, text="Cobro", command=self.calcular_cambio, width=10, height=2, anchor="center", background="red")
        self.bcambio.grid(column=0, row=4)
        


    def BoletoDentro(self):
        respuesta=self.operacion1.Autos_dentro()
        self.scrolledtxt.delete("1.0", tk.END)
        for fila in respuesta:
            self.scrolledtxt.insert(tk.END, "Folio num: "+str(fila[0])+"\nEntro: "+str(fila[1])[:-3]+"\nPlacas: "+str(fila[2])+"\n\n")


    def BoletoPerdido_conFolio(self):
        """
        Esta función se encarga de manejar el cobro de un boleto perdido con folio.

        Verifica si se ha ingresado un número de folio para el boleto perdido y realiza las operaciones correspondientes.
        Calcula la permanencia del vehículo y el importe a cobrar.
        Establece el concepto del boleto como "Per" de perdido.

        :param self: Objeto de la clase que contiene los atributos y métodos necesarios.

        :return: None
        """

        datos = self.PonerFOLIO.get()

        if len(datos) == 0:
            mb.showerror("Error", "Ingrese un folio")
            return None

        self.folio.set(datos)
        datos = self.folio.get()

        # Consultar los datos correspondientes al folio
        respuesta = self.operacion1.consulta(datos)
        if len(respuesta) > 0:
            # Establecer la descripción y precio basados en la respuesta
            self.descripcion.set(respuesta[0][0])
            self.precio.set(respuesta[0][1])
            self.Placa.set(respuesta[0][6])

            # Calcular la permanencia
            self.CalculaPermanencia()

            # Obtener la fecha y hora actual
            fecha = datetime.today()

            # Convertir la fecha y hora actual a formato deseado
            fecha1 = fecha.strftime("%Y-%m-%d %H:%M:%S")
            fechaActual = datetime.strptime(fecha1, '%Y-%m-%d %H:%M:%S')

            # Convertir la descripción a un objeto de fecha y hora
            date_time_str = str(self.descripcion.get())
            date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')

            # Modificar el formato de la fecha y hora
            date_time_mod = datetime.strftime(date_time_obj, '%Y/%m/%d/%H/%M/%S')
            date_time_mod2 = datetime.strptime(date_time_mod, '%Y/%m/%d/%H/%M/%S')

            # Calcular la diferencia entre la fecha actual y la fecha del boleto perdido
            ffeecha = fechaActual - date_time_mod2

            # Calcular los segundos vividos
            segundos_vividos = ffeecha.seconds

            # Calcular las horas y minutos dentro del límite de 24 horas
            horas_dentro, segundos_vividos = divmod(segundos_vividos, 3600)
            minutos_dentro, segundos_vividos = divmod(segundos_vividos, 60)


            if penalizacion_con_importe:

                # Calcular el importe basado en las horas y días de permanencia
                if horas_dentro <= 24:
                    importe = 200 + ((ffeecha.days) * 720 + (horas_dentro * 20))
                if horas_dentro > 24 or ffeecha.days >= 1:
                    importe = 200 + ((ffeecha.days) * 720 + (horas_dentro * 20))

            else:
                importe = 200

            # Establecer el importe y mostrarlo en la etiqueta label9
            self.importe.set(importe)
            self.IImporte.config(text=self.importe.get())

            # Realizar otras operaciones y configuraciones
            self.PrTi.set("Per")

            self.promo.set("")
            self.PonerFOLIO.set("")
        else:
            # Limpiar campos y mostrar mensaje de error
            self.descripcion.set('')
            self.precio.set('')
            mb.showinfo("Información", "No existe un auto con dicho código")


    def BoletoPerdido_sinFolio(self):
        """
        Esta función se encarga de imprimir un boleto perdido sin un número de folio especificado.

        Verifica si se ha confirmado la impresión del boleto perdido.
        Genera un boleto nuevo para poder cobrar boletos que han sido extraviados.
        Agrega el registro del pago a la base de datos.

        :return: None
        """
        Boleto_perdido = mb.askokcancel("Advertencia", f"¿Esta seguro de imprimir un boleto perdido?")
    
        if Boleto_perdido:
            MaxFolio=str(self.operacion1.MaxfolioEntrada())
            MaxFolio = MaxFolio.strip("[(,)]")
            n1 = MaxFolio
            n2 = "1"
            masuno = int(n1)+int(n2)
            masuno = str(masuno)
            self.MaxId.set(masuno)

            fechaEntro = datetime.today()
            fechaEntro = fechaEntro - timedelta(minutes = 1, seconds = fechaEntro.second)
            horaentrada = str(fechaEntro)
        
            horaentrada=horaentrada[:19]
            corteNum = 0
            placa="BoletoPerdido"
            datos=(fechaEntro, corteNum, placa)

            #aqui lo imprimimos

            p.image("LOGO1.jpg")
            p.text("--------------------------------------\n")
            p.set(align = "center")
            p.text("B O L E T O  P E R D I D O\n")
            p.set(align="center")
            p.text("BOLETO DE ENTRADA\n")
            folioZZ=('FOLIO 000' + masuno)
            p.text('Entro: '+horaentrada[:-3]+'\n')
            p.text('Placas '+placa+'\n')
            p.text(folioZZ+'\n')
            p.set(align = "center")
            p.text("B O L E T O  P E R D I D O\n")
            p.text("--------------------------------------\n")
            p.cut()

            #Agregar registro del pago a la base de datos
            self.operacion1.altaRegistroRFID(datos)
            self.Placa.set('')

        else: return None



    def consultar(self, event):
        # Vaciar campo de importe
        self.IImporte.config(text="")

        # Obtener folio
        datos=str(self.folio.get())

        # Si la caja de texto esta vacia no realiza ninguna operación
        if len(datos) == 0:pass

        #Verificar si lee el folio o la promocion
        elif len(datos) < 20:
            folio = self.operacion1.descifrar_folio(folio_cifrado = datos)
            self.folio.set(folio)
            folio = self.folio.get()
            print(f"\nFolio descifrado: {folio}")

            respuesta=self.operacion1.consulta(folio)
            if len(respuesta)>0:
                self.descripcion.set(respuesta[0][0])
                self.precio.set(respuesta[0][1])
                self.Placa.set(respuesta[0][6])
                self.CalculaPermanencia()#nos vamos a la funcion de calcular permanencia

            else:
                self.descripcion.set('')
                self.precio.set('')
                self.folio.set("")
                mb.showinfo("Información", "No existe un auto con dicho código")

        else:
            mb.showinfo("Promocion", "leer primero el folio")
            self.folio.set("")
            self.entryfolio.focus()


    def CalculaPermanencia(self):
        """
        Esta función calcula la permanencia del folio seleccionado.

        Realiza diferentes cálculos basados en la información del boleto y actualiza los valores correspondientes.

        :param self: Objeto de la clase que contiene los atributos y métodos necesarios.

        :return: None
        """

        self.IImporte.config(text="")

        # Obtiene el valor de salida (debería ser 'salida' en lugar de 'precio')
        salida = str(self.precio.get())

        if len(salida) > 5:
            # Si el valor de salida tiene más de 5 caracteres, significa que ya tiene la fecha y ha sido cobrado
            self.label15.configure(text=("Este Boleto ya Tiene cobro"))

            # Realiza una consulta con el folio seleccionado para obtener información adicional del boleto
            respuesta = self.operacion1.consulta({self.folio.get()})

            # Imprime en una caja de texto la información del boleto cuando ya ha sido cobrado
            self.scrol_datos_boleto_cobrado.delete("1.0", tk.END)
            for fila in respuesta:
                self.scrol_datos_boleto_cobrado.insert(
                    tk.END,
                    f"Folio: {fila[2]}\nEntró: {str(fila[0])[:-3]}\nSalió: {str(fila[1])[:-3]}\nTiempo: {str(fila[3])[:-3]}\nTarifa: {fila[4]}\nImporte: {fila[5]}"
                )

            # Reinicia los valores de varios atributos
            self.elcambioes.set("")
            self.elimportees.set("")
            self.cuantopagasen.set("")
            self.descripcion.set('')
            self.precio.set(salida)
            self.copia.set("")
            self.importe.set("")
            self.ffeecha.set("")
            self.ffeecha_auxiliar.set("")
            self.folio.set("")
            self.entryfolio.focus()

        else:
            # Si el valor de salida tiene menos de 5 caracteres, significa que no ha sido cobrado
            self.scrol_datos_boleto_cobrado.delete("1.0", tk.END)
            self.PrTi.set("Normal")
            self.label15.configure(text="Lo puedes COBRAR")

            # Obtiene la fecha actual
            fecha = datetime.today()
            fecha1 = fecha.strftime("%Y-%m-%d %H:%M:%S")
            fechaActual = datetime.strptime(fecha1, '%Y-%m-%d %H:%M:%S')
            self.copia.set(fechaActual)

            # Obtiene la fecha del boleto seleccionado y realiza las conversiones necesarias
            date_time_str = str(self.descripcion.get())
            date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
            date_time_mod = datetime.strftime(date_time_obj, '%Y/%m/%d/%H/%M/%S')
            date_time_mod2 = datetime.strptime(date_time_mod, '%Y/%m/%d/%H/%M/%S')
            ffecha = fechaActual - date_time_mod2

            # Calcula el tiempo en segundos vividos, horas dentro y minutos dentro
            segundos_vividos = ffecha.seconds
            horas_dentro, segundos_vividos = divmod(segundos_vividos, 3600)
            minutos_dentro, segundos_vividos = divmod(segundos_vividos, 60)

            self.ffeecha.set(ffecha)
            self.ffeecha_auxiliar.set(self.ffeecha.get()[:-3])

            if minutos_dentro < 15 and minutos_dentro >= 0:
                minutos = 1
            elif minutos_dentro < 30 and minutos_dentro >= 15:
                minutos = 2
            elif minutos_dentro < 45 and minutos_dentro >= 30:
                minutos = 3
            elif minutos_dentro <= 59 and minutos_dentro >= 45:
                minutos = 4

            if ffecha.days == 0 and horas_dentro == 0:
                # Si la permanencia es menor a 1 hora, se aplica una tarifa fija de 28 unidades
                importe = 20
                self.importe.set(importe)
                self.IImporte.config(text=importe)
                self.entrypromo.focus()
            else:
                # Si la permanencia es mayor a 1 hora, se calcula el importe según una fórmula específica
                importe = ((ffecha.days) * 250 + (horas_dentro * 20) + (minutos) * 5)
                self.importe.set(importe)
                self.IImporte.config(text=importe)
                self.entrypromo.focus()


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
        self.PonerFOLIO.set('')
        self.IImporte.config(text="")

    def Comprobante(self):
        """
        Esta función genera un comprobante de pago para el boleto seleccionado.

        Imprime un comprobante de pago con información relevante del boleto, como la placa del vehículo, la hora de entrada y salida,
        el tiempo de permanencia, el importe y el tipo de cobro. Además, genera un código QR a partir de la información de entrada y salida.

        :param self: Objeto de la clase que contiene los atributos y métodos necesarios.

        :return: None
        """

        # Obtener la placa
        placa = self.Placa.get()
        promocion = self.PrTi.get()

        p.set('center')
        p.image("LOGO1.jpg")
        p.text("----------------------------------\n")
        p.text("Comprobante de pago\n")
        if placa == "BoletoPerdido":
            p.text("BOLETO PERDIDO\n")


        EntradaCompro = str(self.descripcion.get())
        folioactual=str(self.folio.get())
        SalioCompro = str(self.copia.get())
        imgqr = (SalioCompro + folioactual)


        self.operacion1.generar_QR(imgqr)
        print(f"QR salida: {imgqr}")


        #Compro de comprobante
        p.set('left')
        ImporteCompro=str(self.importe.get(),)
        p.text("El importe es $"+ImporteCompro+"\n")
        EntradaCompro = str(self.descripcion.get(),)
        p.text('El auto entro: '+EntradaCompro[:-3]+'\n')
        SalioCompro = str(self.copia.get(),)

        p.text('El auto salio: '+SalioCompro[:-3]+'\n')
        TiempoCompro = str(self.ffeecha.get(),)
        p.text('El auto permanecio: '+TiempoCompro[:-3]+'\n')
        folioactual=str(self.folio.get(), )
        p.text('Placa del auto: '+placa+'\n')
        p.text(f"Tipo de cobro: {promocion}\n")
        p.text('El folio del boleto es: '+folioactual+'\n')
        p.set(align="center")
        p.image("reducida.png")
        p.text("----------------------------------\n")
        p.cut()


        p.set(align="center")
        p.image("LOGO1.jpg")

        p.text("----------------------------------\n")
        p.text("Comprobante de pago\n")

        if placa == "BoletoPerdido":
            p.text("BOLETO PERDIDO\n")
        EntradaCompro = str(self.descripcion.get(),)
        SalioCompro = str(self.copia.get(),)

        #Compro de comprobante
        p.set('left')
        ImporteCompro=str(self.importe.get(),)
        p.text("El importe es $"+ImporteCompro+"\n")
        EntradaCompro = str(self.descripcion.get(),)
        p.text('El auto entro: '+EntradaCompro[:-3]+'\n')
        SalioCompro = str(self.copia.get(),)
        p.text('El auto salio: '+SalioCompro[:-3]+'\n')
        TiempoCompro = str(self.ffeecha.get(),)
        p.text('El auto permanecio: '+TiempoCompro[:-3]+'\n')
        folioactual=str(self.folio.get(), )
        p.text('Placa del auto: '+placa+'\n')
        p.text(f"Tipo de cobro: {promocion}\n")
        p.text('El folio del boleto es: '+folioactual+'\n')
        p.text("----------------------------------\n")
        p.cut()
        self.Placa.set("")


    def GuardarCobro(self):
        salida = str(self.precio.get(), )#deveria ser salida en lugar de precio pero asi estaba el base
        if len(salida)>5:
            self.label15.configure(text=("con salida, INMODIFICABLE"))
            mb.showinfo("Información", "Ya Tiene Salida")
            self.descripcion.set('')
            self.precio.set('')
            self.copia.set("")
            #self.importe.set("")
            self.ffeecha.set("")
            self.ffeecha_auxiliar.set("")
            self.folio.set("")
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
            self.label15.configure(text=(""))
            self.importe.set("")
            self.ffeecha.set("")
            self.ffeecha_auxiliar.set("")
            self.folio.set("")
            self.PrTi.set("")
            self.PonerFOLIO.set('')
            #self.elcambioes.set("")
            #self.elimportees.set("")
            #self.cuantopagasen.set("")
            self.entryfolio.focus()#se posiciona en leer qr



    def CalculaPromocion(self,event):
           global TipoPromocion
           TipoPromocion = str(self.promo.get(), )#se recibe el codigo
           respuesta=self.operacion1.ValidaPromo(TipoPromocion)
           print(str(respuesta))
           if respuesta:
              mb.showwarning("IMPORTANTE", "LA PROMOCION YA FUE APLICADA")
           else:

              TipoProIni=TipoPromocion[:8]
              print("TIPO",str(TipoProIni))
              if TipoProIni==("a1 anuie") or TipoProIni==("A1 ANUIE"):
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
                       importe = 0
                       self.importe.set(importe)
                   importe = str(self.importe.get(), )
                   importe = int(importe)
                   if horas_dentro >= 1:
                        importe = str(self.importe.get(), )
                        importe = int(importe)
                        importe=(importe - 20)

                   self.importe.set(importe)
                   self.label9.configure(text =(importe, "cobro"))
                   self.PrTi.set("ANUIS1")
                   #mb.showinfo("liverpool",importe)
                   self.promo.set("")
              if TipoProIni==("A2 ANUIS") or TipoProIni==("a2 anuis"):
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
                   if horas_dentro < 2:
                       importe = 0
                       self.importe.set(importe)
                   importe = str(self.importe.get(), )
                   importe = int(importe)
                   #mb.showinfo("liverpool",importe)
                   if horas_dentro >= 2:
                        importe = str(self.importe.get(), )
                        #mb.showinfo("liverpool",importe)
                        importe = int(importe)
                        importe=(importe - 40)
                        #importe = ((ffeecha.days)*720 + (horas_dentro * 30)+(minutos_dentro)*1)
                   self.importe.set(importe)
                   self.label9.configure(text =(importe, "cobro"))
                   self.PrTi.set("ANUIS2")
                   #mb.showinfo("liverpool",importe)
                   self.promo.set("")
              if TipoProIni==("EV ANUIE") or TipoProIni==("ev anuie"):
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
                   if horas_dentro < 8:
                       importe = 80
                       self.importe.set(importe)
                   importe = str(self.importe.get(), )
                   importe = int(importe)
                   if horas_dentro >= 8:
                        importe = str(self.importe.get(), )
                        importe = int(importe)
                        importe=(importe - 140)
                        #importe = ((ffeecha.days)*720 + (horas_dentro * 30)+(minutos_dentro)*1)
                   self.importe.set(importe)
                   self.label9.configure(text =(importe, "cobro"))
                   self.PrTi.set("EVENTO")
                   #mb.showinfo("liverpool",importe)
                   self.promo.set("")
              if TipoProIni==("CN CENEV") or TipoProIni==("cn cenev"):
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
                   if horas_dentro < 8:
                       importe = 80
                       self.importe.set(importe)
                   importe = str(self.importe.get(), )
                   importe = int(importe)
                   if horas_dentro >= 8:
                        importe = str(self.importe.get(), )
                        importe = int(importe)
                        importe=(importe - 140)
                        #importe = ((ffeecha.days)*720 + (horas_dentro * 30)+(minutos_dentro)*1)
                   self.importe.set(importe)
                   self.label9.configure(text =(importe, "cobro"))
                   self.PrTi.set("CENEVAL")
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
                        mb.showinfo("Pension",'Se registra SALIDA del auto')

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
        self.entryFOLIOCancelado.grid(column=1, row=1)
        self.boton7=tk.Button(self.FrmCancelado, text="B./SIN cobro", command=self.BoletoDentro2, width=12, height=2, anchor="center")
        self.boton7.grid(column=0, row=0, padx=1, pady=1)

        self.btnCancelado=tk.Button(self.FrmCancelado, text="Cancelar Boleto ", command=self.BoletoCancelado, width=12, height=2, anchor="center")
        self.btnCancelado.grid(column=0, row=2)
        self.scrolledtxt2=st.ScrolledText(self.FrmCancelado, width=26, height=7)
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



        self.CortesAnteri=tk.StringVar()
        self.entryCortesAnteri=tk.Entry(self.labelframe3, width=20, textvariable=self.CortesAnteri)
        self.entryCortesAnteri.grid(column=1, row=0)

        self.boton1=ttk.Button(self.labelframe1, text="Todas las Entradas", command=self.listar)
        self.boton1.grid(column=0, row=0, padx=4, pady=4)
        self.boton2=ttk.Button(self.labelframe1, text="Entradas sin corte", command=self.listar1)
        self.boton2.grid(column=0, row=2, padx=4, pady=4)
        self.boton3=tk.Button(self.labelframe2, text="Calcular Corte", command=self.Calcular_Corte, width=15, height=1)
        self.boton3.grid(column=2, row=0, padx=4, pady=4)
        self.boton4=tk.Button(self.labelframe2, text="Generar Corte", command=self.Guardar_Corte, width=15, height=1, anchor="center", background="red")
        self.boton4.grid(column=2, row=4, padx=4, pady=4)
        self.boton5=tk.Button(self.labelframe3, text="Imprimir salidas\nCorte", command=self.desglose_cobrados, width=15, height=3, anchor="center")
        self.boton5.grid(column=1, row=2, padx=4, pady=4)
        self.scrolledtext1=st.ScrolledText(self.labelframe1, width=28, height=4)
        self.scrolledtext1.grid(column=0,row=1, padx=1, pady=1)

        self.comboMesCorte = ttk.Combobox(self.labelframe5, width=6, justify=tk.RIGHT, state="readonly")
        self.comboMesCorte["values"] = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
        self.comboMesCorte.current(0)
        self.comboMesCorte.grid(column=1, row=0, padx=1, pady=1)
        self.AnoCorte=tk.IntVar()
        Ano= datetime.now().date().year
        self.AnoCorte.set(Ano)
        self.entryAnoCorte=tk.Entry(self.labelframe5, width=7, textvariable=self.AnoCorte, justify=tk.RIGHT)
        self.entryAnoCorte.grid(column=1, row=2)
        self.Clave2=tk.StringVar()
        self.entryClave2=tk.Entry(self.labelframe5, width=7, textvariable=self.Clave2, show="*", justify=tk.RIGHT)
        self.entryClave2.grid(column=1, row=5)
        self.boton6=tk.Button(self.labelframe5, text="Reporte de Corte", command=self.Reporte_Corte, width=15, height=1, anchor="center", background="red")
        self.boton6.grid(column=3, row=2, padx=4, pady=4)


    def BoletoDentro2(self):
        respuesta=self.operacion1.Autos_dentro()
        self.scrolledtxt2.delete("1.0", tk.END)
        for fila in respuesta:
            self.scrolledtxt2.insert(tk.END, "Folio num: "+str(fila[0])+"\nEntro: "+str(fila[1])[:-3]+"\nPlacas: "+str(fila[2])+"\n\n")


    def desglose_cobrados(self):
        Numcorte=str(self.CortesAnteri.get(), )
        Numcorte=int(Numcorte)
        Numcorte=str(Numcorte)
        respuesta=self.operacion1.desglose_cobrados(Numcorte)
        self.scrolledtxt2.delete("1.0", tk.END)



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
        """
        Esta función cancela un boleto específico.

        Verifica si se ha ingresado un número de folio para cancelar y muestra una advertencia para confirmar la cancelación.
        Si se confirma la cancelación, obtiene los datos del boleto cancelado y realiza las operaciones correspondientes.
        Muestra información relevante del boleto cancelado y guarda el registro del cobro cancelado.

        :param self: Objeto de la clase que contiene los atributos y métodos necesarios.

        :return: None
        """

        if len(self.FolioCancelado.get()) == 0:
            mb.showerror("Error", "Ingrese un folio a cancelar")
            return None

        cancelar = mb.askokcancel("Advertencia", f"¿Estas seguro de querer cancelar el boleto con folio: {self.FolioCancelado.get()}?")

        if cancelar:
            datos = self.FolioCancelado.get()
            self.folio.set(datos)

            datos = self.folio.get()
            respuesta = self.operacion1.consulta(datos)

            if len(respuesta) > 0:
                if respuesta[0][1] is not None:
                    self.FolioCancelado.set("")
                    self.folio.set("")
                    mb.showerror("Error", "No se puede cancelar un boleto ya cobrado")
                    return None

                if respuesta[0][6] == "BoletoPerdido":
                    mb.showerror("Error", "El folio ingresado corresponde a una reposición de un boleto perdido, no se puede cancelar.")
                    self.FolioCancelado.set("")
                    self.folio.set("")
                    return None

                self.descripcion.set(respuesta[0][0])
                self.precio.set(respuesta[0][1])
                self.CalculaPermanencia()



                fecha = datetime.today()
                fecha1 = fecha.strftime("%Y-%m-%d %H:%M:%S")
                fechaActual = datetime.strptime(fecha1, '%Y-%m-%d %H:%M:%S')
                date_time_str = str(self.descripcion.get())
                date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
                date_time_mod = datetime.strftime(date_time_obj, '%Y/%m/%d/%H/%M/%S')
                date_time_mod2 = datetime.strptime(date_time_mod, '%Y/%m/%d/%H/%M/%S')
                ffecha = fechaActual - date_time_mod2
                segundos_vividos = ffecha.seconds
                horas_dentro, segundos_vividos = divmod(segundos_vividos, 3600)
                minutos_dentro, segundos_vividos = divmod(segundos_vividos, 60)
                if horas_dentro <= 24:
                    importe = 0
                if horas_dentro > 24 or ffecha.days >= 1:
                    importe = 0
                self.importe.set(importe)
                self.IImporte.config(text=importe)
                self.PrTi.set("CDO")
                self.promo.set("")
                p.text('Boleto Cancelado\n')
                FoliodelCancelado = str(self.FolioCancelado.get())
                p.text('Folio boleto cancelado: ' + FoliodelCancelado + '\n')
                fecha = datetime.today()
                fechaNota = datetime.today()
                fechaNota = fechaNota.strftime("%b-%d-%A-%Y %H:%M:%S")
                horaNota = str(fechaNota)
                p.set(align="left")
                p.set('Big line\n', font='b')
                p.text('Fecha: ' + horaNota[:-3] + '\n')
                EntradaCompro = str(self.descripcion.get())
                p.text('El auto entro: ' + EntradaCompro[:-3] + '\n')
                SalioCompro = str(self.copia.get())
                p.text('El auto salio: ' + SalioCompro[:-3] + '\n')
                self.GuardarCobro()
                self.FolioCancelado.set("")
                p.cut()

            else:
                self.descripcion.set('')
                self.precio.set('')
                mb.showinfo("Información", "No existe un auto con dicho código")
        else:
            self.FolioCancelado.set("")


    def listar(self):
        respuesta=self.operacion1.recuperar_todos()
        self.scrolledtext1.delete("1.0", tk.END)
        for fila in respuesta:
            self.scrolledtext1.insert(tk.END, "Entrada num: "+str(fila[0])+"\nEntro: "+str(fila[1])[:-3]+"\nSalio: "+str(fila[2])[:-3]+"\n\n")


    def listar1(self):
        respuesta=self.operacion1.recuperar_sincobro()
        self.scrolledtext1.delete("1.0", tk.END)
        #respuesta=str(respuesta)
        for fila in respuesta:
            self.scrolledtext1.insert(tk.END, "Entrada num: "+str(fila[0])+"\nEntro: "+str(fila[1])[:-3]+"\nSalio: "+str(fila[2])[:-3]+"\nImporte: "+str(fila[3])+"\n\n")

            p.text('Entrada Num :')
            p.text(str(fila[0]))
            p.text('\n')
            p.text('Entro :')
            p.text(str(fila[1])[:-3])
            p.text('\n')
            p.text('Salio :')
            p.text(str(fila[2])[:-3])
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

        ######Obtenemos los datos del Cajero en Turno
        cajero=self.operacion1.CajeroenTurno()
        for fila in cajero:
           cajero1 = fila[0]
           nombre2 = fila[1]
           inicio1 = fila[2]
           turno1 = fila[3]
           usuario1 = fila[4]
        hoy = str(datetime.today())
        hoy1=hoy[:20]

        datos=(hoy1, cajero1)
        self.operacion1.Cierreusuario(datos)
        dato=(cajero1)
        self.operacion1.NoAplicausuario(dato)
        ##la fecha final de este corte que es la actual
        fechaDECorte = str(self.FechaCorte.get(),)
        fechaDECorte = datetime.strptime(fechaDECorte, '%Y-%m-%d %H:%M:%S' )
        ######la fecha del inicial obtiene de labase de datos
        fechaInicio1 = str(inicio1)
        fechaInicio2 = datetime.strptime(fechaInicio1, '%Y-%m-%d %H:%M:%S')
        fechaInicio = fechaInicio2
        ######el importe se obtiene de la suma
        ImpCorte2 =str(self.ImporteCorte.get(),)
        Im38=ImpCorte2.strip('(,)')
        AEE = (self.operacion1.CuantosAutosdentro())
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

        p.image("LOGO1.jpg")
        p.text(" Est TENAYUCA CORTE Num "+maxnum+"\n")
        p.text('IMPORTE: $ '+Im38+'\n')
        ultiCort1=str(self.FechUCORTE.get(),)                
        ultiCort4= datetime.strptime(ultiCort1, '%Y-%m-%d %H:%M:%S')
        ultiCort5 = datetime.strftime(ultiCort4, '%A %d %m %Y a las %H:%M:%S')
        p.text('Inicio: ')
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
        p.text("Cajero en Turno: "+nombre2+"\n")
        p.text("Turno: "+str(turno1)+"\n")
        dato =(inicio1)
        inicios = self.operacion1.IniciosdeTurno(dato)
        for fila in inicios:
            p.text("Sesion "+fila[1]+": "+str(fila[0])+"\n")

        BolCobrImpresion=str(self.BoletosCobrados.get(),)
        p.text("Boletos Cobrados: "+BolCobrImpresion+"\n")

        p.text('Boletos Expedidos: '+BEDespuesCorteImpre+'\n')
        BAnterioresImpr=str(self.BAnteriores.get(),)#######
        p.text("Boletos Turno Anterior: "+BAnterioresImpr+"\n")
        #AutosAnteriores = int(self.Autos_Anteriores.get(),)
        #AutosAnteriores = str(AutosAnteriores)
        #p.text('Sensor Turno Anterior: '+AutosAnteriores+'\n')

        AEE1 = self.operacion1.CuantosAutosdentro()
        for fila in AEE1:
            AEE = fila[0]
        BDentroImp = (AEE + int(BEDespuesCorteImpre)) - int(BolCobrImpresion) #str(self.BDentro.get(),)
        str(BDentroImp)
        p.text('Boletos dejados: '+str(BDentroImp)+'\n')
        AutosEnEstacImpre = str(self.AutosEnEstacionamiento.get(),)
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




        respuesta=self.operacion1.desglose_cobrados(Numcorte)
        self.scrolledtxt2.delete("1.0", tk.END)



        p.text("Cantidad e Importes "+'\n')
        p.text("Cantidad - Tarifa - valor C/U - Total "+'\n')
        for fila in respuesta:
            self.scrolledtxt2.insert(tk.END, str(fila[0])+" Boletos con tarifa "+str(fila[1])+"\n"+"valor c/u $"+str(fila[2])+" Total $"+str(fila[3])+"\n\n")

            p.text(f"   {str(fila[0])}   -  {str(fila[1])}   -  ${str(fila[2])}  -  ${str(fila[3])}\n")

        else:
            p.text("\n")
            p.text(f"{BolCobrImpresion} Boletos         Suma total ${Im38}\n\n")    

        p.text("----------------------------------\n")


        Boletos_perdidos_generados = self.operacion1.Boletos_perdidos_generados()
        Boletos_perdidos_generados = Boletos_perdidos_generados[0][0]
        Boletos_perdidos_generados_desglose = self.operacion1.Boletos_perdidos_generados_desglose()

        Boletos_perdidos_cobrados = self.operacion1.Boletos_perdidos_cobrados(Numcorte)
        Boletos_perdidos_cobrados = Boletos_perdidos_cobrados[0][0]
        Boletos_perdidos_cobrados_desglose = self.operacion1.Boletos_perdidos_cobrados_desglose(Numcorte)

        Boletos_perdidos_no_cobrados = self.operacion1.Boletos_perdidos_no_cobrados()
        Boletos_perdidos_no_cobrados = Boletos_perdidos_no_cobrados[0][0]


        if Boletos_perdidos_generados > 0 or Boletos_perdidos_cobrados > 0 or Boletos_perdidos_no_cobrados > 0:

            p.text("BOLETOS PERDIDOS"+'\n\n')

            p.text(f"Boletos perdidos generados: {Boletos_perdidos_generados + Boletos_perdidos_cobrados}"+'\n')
            for boleto in Boletos_perdidos_cobrados_desglose:
                p.text(f"Folio:{boleto[0]}\nFecha entrada:{boleto[1]}\n")
            for boleto in Boletos_perdidos_generados_desglose:
                p.text(f"Folio:{boleto[0]}\nFecha entrada:{boleto[1]}\n")

            p.text("**********************************\n")

            p.text(f"Boletos perdidos cobrados: {Boletos_perdidos_cobrados}"+'\n\n')
            for boleto in Boletos_perdidos_cobrados_desglose:
                p.text(f"Folio:{boleto[0]}\nFecha entrada:{boleto[1]}\nFecha salida:{boleto[2]}\n")
            p.text("**********************************\n")

            p.text(f"Boletos perdidos quedados: {Boletos_perdidos_no_cobrados}"+'\n\n')
            for boleto in Boletos_perdidos_generados_desglose:
                p.text(f"Folio:{boleto[0]}\nFecha entrada:{boleto[1]}\n")

            p.text("----------------------------------\n")


        respuesta = self.operacion1.total_pensionados_corte(Numcorte)
        if len(respuesta) > 0:

            p.text("Cantidad e Importes Pensiones"+'\n')
            p.text("Cuantos - Concepto - ImporteTotal "+'\n')
            for fila in respuesta:
                p.text(f"   {str(fila[0])}   -  {str(fila[1])}   -   ${str(fila[2])}\n")

            else:
                p.text("----------------------------------\n")


        p.text("----------------------------------\n")
        p.cut()
        self.Cerrar_Programa()



    def Cerrar_Programa(self):
        self.ventana1.destroy()

    def Reporte_Corte(self):
        contrasena = str(self.entryClave2.get(), )
        ##simpledialog.askinteger("Contrasena", "Capture su Contrasena:",
                                 ##parent=self.labelframe4) # minvalue=8, maxvalue=8
        if len(contrasena) == 0:
            mb.showwarning("IMPORTANTE", "Capturar: La CLAVE para ejecutar las acciones")
            self.entryClave2.focus()
        elif contrasena == "13579" :
            #try:
                mes=self.comboMesCorte.get()
                Ano=int(self.entryAnoCorte.get(), )
                if Ano is None :
                    mb.showwarning("IMPORTANTE", "Debe capturar el Ano del reporte")
                    return False
                elif Ano <= 0 :
                    mb.showwarning("IMPORTANTE", "Distribucion debe ser un numero positivo mayor a cero")
                    return False
                else :
                    Libro = '/home/pi/Documents/Cobro/XlsCorte/Rpte Corte '+ str(mes)+'-'+str(Ano)+'  '+str(datetime.now().date())+'.xlsx' #+'/' '/home/pi/Documents/electrofloculacion/belen/Prueba/RPTCORTE.xlsx'
                    datos=(mes, Ano)
                    #Obtenemos Fecha (Inicialy Final) del mes que solicita el reporte
                    CorteMaxMin=self.operacion1.Cortes_MaxMin(datos)
                    for fila in CorteMaxMin:
                       UltFecha=fila[0]
                       IniFecha=fila[1]
                       FinFecha=fila[2]
                    #Obtenemos Primer y Ultimo Folio de Cortes del Mes que se solicita el reporte
                    datos=(IniFecha)
                    CorteIni=self.operacion1.Cortes_Folio(datos)
                    datos=(UltFecha)
                    #CorteFin=self.operacion1.Cortes_FolioFin(datos)
                    CorteFin=self.operacion1.Cortes_Folio(datos)
                    #Obtnemos los Registros entre estos dos Folios para el cuerpo del reporte
                    datos=(CorteIni, CorteFin)
                    #datos=(IniFecha, UltFecha)
                    Registros=self.operacion1.Registros_corte(datos)
                    TotalesCorte=self.operacion1.Totales_corte(datos)
                    ResumenPromo=self.operacion1.Resumen_promo(datos)
                    workbook = xlsxwriter.Workbook(Libro)
                    worksheet = workbook.add_worksheet('CORTE')
                    #Definimos Encabezado Principal
                    #Obtenemos imagen del Encabezado
                    worksheet.insert_image('A3', '/home/pi/Documents/Cobro/LOGO NEW.jpg') #,{'x_scale': 0.20, 'y_scale': 0.20} Insert de Logo (imagen.png)
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
                        #print(str(fila[3]))
                        worksheet.write('G'+str(row), fila[0], cell_format5)#Total de Cobros en resumen
                        worksheet.write('F'+str(row), fila[3], cell_format6)#Total de Folios en Resumen
                        worksheet.write('G'+str(row+5), fila[0], cell_format1)# Total de cobros Encabezado
                        worksheet.write('G'+str(row+4),str(fila[2]) +" al "+ str(fila[1]))
                    #Definimos Formato y Ancho de Fila Encabezado del cuerpo del reporte
                    cell_format = workbook.add_format({'bold': True, 'align':'center', 'text_wrap':True, 'border':1, 'pattern':1, 'bg_color':'#D9D9D9'}) #808080
                    worksheet.set_row(row+7, 34)
                    #worksheet.set_row(10, 34)
                    #Definimos anchos de Columna del cuerpo del reporte
                    worksheet.set_column(0, 0, 10)
                    worksheet.set_column(1, 2, 30)
                    worksheet.set_column(3, 4, 14)
                    worksheet.set_column(5, 5, 13)
                    worksheet.set_column(6, 6, 30)
                    worksheet.set_column(7, 7, 10)
                    #Definimos Nombres de columnas del cuerpo del reporte
                    worksheet.write('A'+str(row+8), 'FOLIO', cell_format)
                    worksheet.write('B'+str(row+8), 'FECHA Y HORA ENT', cell_format)
                    worksheet.write('C'+str(row+8), 'FECHA Y HORA SAL', cell_format)
                    worksheet.write('D'+str(row+8), 'TIEMPO', cell_format)
                    worksheet.write('E'+str(row+8), 'PRECIO', cell_format)
                    worksheet.write('F'+str(row+8), 'CORTES', cell_format)
                    worksheet.write('G'+str(row+8), 'DESCRIPCION', cell_format)
                    worksheet.write('H'+str(row+8), 'PROM', cell_format)
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
                    workbook.close()
                    mb.showinfo("Reporte de Corte",'Reporte Guardado')
            #except:
                #print('lo que escribiste no es un entero')
                #mb.showwarning("IMPORTANTE", "Ha ocurrido un error: Revise los datos capturados")
        else:
            mb.showwarning("ERROR", 'Contrasena Incorrecta')

    def Puertoycontar(self):
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

    ###################### Fin de Pagina3 Inicio Pagina4 ###############################
    def Alta_Pensionado(self):
        self.pagina4 = ttk.Frame(self.cuaderno1)
        self.cuaderno1.add(self.pagina4, text="Modulo Pensionados")
        #enmarca los controles LabelFrame 
        self.labelframe1=ttk.LabelFrame(self.pagina4, text="Pensionados")
        self.labelframe1.grid(column=0, row=0, sticky=tk.NW)
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
        self.lbldatosVig1=ttk.Label(self.labelframe1, text=" ") #Informativo En consulta muestra la Fecha de Vigencia
        self.lbldatosVig1.grid(column=2, row=12, padx=4, pady=4)
        self.lbldatosVig2=ttk.Label(self.labelframe1, text=" ") #Informativo En consulta muestra la Fecha de Vigencia
        self.lbldatosVig2.grid(column=3, row=12, padx=4, pady=4)

        self.Montoxmes=tk.IntVar(value=0)  #IntVar(value=0)
        self.entryMontoxmes=ttk.Entry(self.labelframe1, width=15, textvariable=self.Montoxmes)
        self.entryMontoxmes.grid(column=3, row=9)
        self.comboCortesia = ttk.Combobox(self.labelframe1, width=5, justify=tk.LEFT, state="readonly")
        self.comboCortesia["values"] = ["Si", "No"]
        self.comboCortesia.current(1)
        self.comboCortesia.grid(column=3, row=10, padx=1, pady=1)
        self.Tole=tk.IntVar(value=0)
        self.entryTole=ttk.Entry(self.labelframe1, width=15, textvariable=self.Tole)
        self.entryTole.grid(column=3, row=11)

        #####Botones de Accion: Alta
        self.boton1=tk.Button(self.labelframe1, text="Guardar", command=self.Guarda_Pensionado, width=15, height=1, anchor="center")#, background="red"
        self.boton1.grid(column=0, row=20, padx=4, pady=4)
        self.boton3=tk.Button(self.labelframe1, text="Consultar", command=self.Consulta_Pensionado, width=15, height=1, anchor="center")#, background="red"
        self.boton3.grid(column=1, row=20, padx=4, pady=4)



        self.lbldatos21=ttk.Label(self.labelframe1, text="***CLAVE***")
        self.lbldatos21.grid(column=3, row=19, padx=4, pady=4)
        self.Clave=tk.StringVar()
        self.entryClave=ttk.Entry(self.labelframe1, width=8, textvariable=self.Clave, show="*")#, justify=tk.RIGHT
        self.entryClave.grid(column=3, row=20, padx=4, pady=4)

        label_frame_tipo_pago = tk.LabelFrame(self.pagina4, text="Pago Pension")
        label_frame_tipo_pago.grid(column=0, row=1, sticky=tk.NW)

        ######Pago, Vigencia y Numero de tarjeta
        self.labelframe3=tk.LabelFrame(label_frame_tipo_pago, text="Datos de pago")
        self.labelframe3.grid(column=0, row=0, padx=4, pady=4) 
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
        self.comboMensual["values"] = ["1"]#, "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
        self.comboMensual.current(0)
        self.comboMensual.grid(column=1, row=3, padx=1, pady=1)
        self.Vigencia=tk.StringVar()
        self.entryVigencia=ttk.Entry(self.labelframe3, width=20, textvariable=self.Vigencia, state="readonly")
        self.entryVigencia.grid(column=4, row=2)
        self.Estatus=tk.StringVar()
        self.entryEstatus=ttk.Entry(self.labelframe3, width=20, textvariable=self.Estatus, state="readonly")#Informativo
        self.entryEstatus.grid(column=4, row=3, padx=4, pady=4)
        #####Botones de Accion: Pagar

        self.tipo_pago_ = None

        label_frame_tipo_pago = tk.LabelFrame(label_frame_tipo_pago, text="Tipo de pago")
        label_frame_tipo_pago.grid(column=1, row=0, padx=10, pady=10, sticky=tk.NW)

        # Crear una variable de control para el estado del checkbox
        self.variable_tipo_pago_efectivo = tk.BooleanVar()
        # Crear un checkbox y asociarlo a la variable de control
        checkbox_efectivo = tk.Checkbutton(label_frame_tipo_pago, text="Efectivo", variable=self.variable_tipo_pago_efectivo, command=lambda:{self.cambiar_valor(self.variable_tipo_pago_transferencia)})

        # Ubicar el checkbox en la ventana principal
        checkbox_efectivo.grid(column=0, row=0, padx=0, pady=0, sticky=tk.NW)

        self.variable_tipo_pago_transferencia = tk.BooleanVar()

        checkbox_transferencia = tk.Checkbutton(label_frame_tipo_pago, text="Transferencia", variable=self.variable_tipo_pago_transferencia, command=lambda:{self.cambiar_valor(self.variable_tipo_pago_efectivo)})

        # Ubicar el checkbox en la ventana principal
        checkbox_transferencia.grid(column=0, row=1, padx=0, pady=0, sticky=tk.NW)


        self.boton2=tk.Button(label_frame_tipo_pago, text="Cobrar Pension", command=self.Cobro_Pensionado, width=12, height=1, anchor="center", background="red")#, background="red"
        self.boton2.grid(column=0, row=3, padx=4, pady=4)

        ######Muestra de Pensionados Adentro
        self.labelframe4=ttk.LabelFrame(self.pagina4, text="Consulta")
        self.labelframe4.grid(column=1, row=0, padx=5, pady=10, sticky=tk.NW)
        self.lbldatos22=ttk.Label(self.labelframe4, text="---Pensionados Adentro---")
        self.lbldatos22.grid(column=0, row=1, padx=4, pady=4)
        self.scrolledPen=st.ScrolledText(self.labelframe4, width=28, height=14)
        self.scrolledPen.grid(column=0,row=2, padx=10, pady=10)
        self.lbldatosTotPen=ttk.Label(self.labelframe4, text="")
        self.lbldatosTotPen.grid(column=0, row=4, padx=4, pady=4)

        self.boton5=tk.Button(self.labelframe4, text="Consultar", command=self.PenAdentro, width=12, height=1, anchor="center")#, background="red"
        self.boton5.grid(column=0, row=6, padx=4, pady=4)

    ###IMPORTANTE: SE PUEDE MODIFICAR EL # DE TARJETA, ASÍ QUE DESDE QUE SE CONSULTA ASIGNAR A UNA VARIBLE
    ##GLOBAL CON EL ID DEL CLIENTE PARA GUARDAR LOS CAMBIOS. POR SI CAMBIAN EL NUMERO DE TARJETA
    def Guarda_Pensionado(self): #Alta Pensionado Nuevo
        contrasena= str(self.entryClave.get(), )
        if len(contrasena) == 0:
           mb.showwarning("IMPORTANTE", "Capturar: La CLAVE para ejecutar las acciones")
        elif contrasena == "P4s3":
            #try:
                ##Generales
                numtarjeta=str(self.NumTarjeta.get(),) #self.NumTarjeta=tk.StringVar()
                Nombre=str(self.PenNombre.get(), )
                ApellidoPat=str(self.PenApellPat.get(), )
                ApellidoMat=str(self.PenApellMat.get(), )
                Telefono1=str(self.PenTelefonoObli.get(), )
                Telefono2=""#str(self.PenTelefonoOpc.get(), )
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
                montomes= int(self.Montoxmes.get(), )
                tolerancia=int(self.Tole.get(), )
                if cortesia == "Si" :
                    vigencia = "Activo"
                    NvaVigencia= date.today() + timedelta(days = 3650)
                    montoxmes = 1 ###Si el Pensionado tiene cortesia, no es necesario el monto a cobrar
                    texto = "Datos Guardados"
                elif cortesia == "No" and montomes == 0:
                    vigencia = "Inactiva"
                    NvaVigencia= date.today()
                    mb.showwarning("IMPORTANTE", "Debe capturar el Monto x Mes")
                    #self.Montoxmes.focus()
                    return False
                else:
                    vigencia = "Inactiva"
                    NvaVigencia= date.today()
                    montoxmes = int(self.Montoxmes.get(), )
                    texto = "Datos Guardados: REALIZAR PAGO PARA ACTIVAR TARJETA"
                #mb.showwarning("IMPORTANTE", str(len(numtarjeta)))
                if len(numtarjeta) == 0 :
                    mb.showwarning("IMPORTANTE", "Leer Numero de Tarjeta")
                    return False
                elif len(Nombre) == 0 :
                    mb.showwarning("IMPORTANTE", "Capturar: Nombre de la Empresa")
                    return False
                elif len(ApellidoPat) == 0 :
                    mb.showwarning("IMPORTANTE", "Capturar: Nombre del Contacto")
                    return False

                elif tolerancia is None :
                    mb.showwarning("IMPORTANTE", "Capturar: Tolerancia")
                    return False
                elif tolerancia < 0 :
                    mb.showwarning("IMPORTANTE", "La Tolerancia debe ser mayor a cero")
                    return False
                else :
                    #print("paso")
                    tarjeta=int(numtarjeta)
                    #print(str(tarjeta))
                    Existe=self.operacion1.ValidarID(tarjeta)
                    #mb.showwarning("IMPORTANTE", Existe)
                    if len(Existe) != 0 and PensionadoOpen == 1: # PensionadoOpen=1 implica un Nuevo Pensionado
                        mb.showwarning("IMPORTANTE", "Numero de tarjeta ya asignado")
                        self.NumTarjeta.set("")
                        self.entryNumTarjeta.focus()
                        return False
                    elif PensionadoOpen == 1: #Alta de Pensionado Nuevo
                        datos=(numtarjeta, Nombre, ApellidoPat, ApellidoMat, fechaAlta, Telefono1, Telefono2, Ciudad, Colonia, CP, Calle, Placa, Modelo, Color, montoxmes, cortesia, tolerancia, vigencia, NvaVigencia)
                        self.operacion1.AltaPensionado(datos)
                        mb.showinfo("Alta de Pensionados", texto)
                    else : #Se trata de un Cambio a un pensionado existente
                        fechaCambio = date.today()
                        datos=(numtarjeta, Nombre, ApellidoPat, ApellidoMat, Telefono1, Ciudad, Colonia, CP, Calle, Placa, Modelo, Color, montoxmes, cortesia, tolerancia, fechaCambio, vigencia, NvaVigencia, PensionadoOpen)
                        self.operacion1.ModificarPensionado(datos)
                        mb.showinfo("Modificar Información", texto)
                self.NumTarjeta.set("")
                self.PenNombre.set("")
                self.PenApellPat.set("")
                self.PenApellMat.set("")
                self.PenTelefonoObli.set("")
                #self.PenTelefonoOpc.set("")
                self.PenCalle.set("")
                self.PenColonia.set("")
                self.PenCiudad.set("")
                self.PenCP.set("")
                self.Placas.set("")
                self.AutoMod.set("")
                self.AutoColor.set("")
                self.lbldatosVig2.configure(text=" ")
                self.Vigencia.set("")
                self.Estatus.set("")
                self.Montoxmes.set(0)
                self.comboCortesia.current(0)
                self.Tole.set(0)
                self.Clave.set("")
                self.entryNumTarjeta.focus()


            #except:
                #mb.showwarning("IMPORTANTE", "Ha ocurrido un error: Revise los datos capturados")
        else:
            mb.showwarning("ERROR", 'CLAVE Incorrecta')

    def Consulta_Pensionado(self): #Trae la información del Pensionado a Consultar
        contrasena= str(self.entryClave.get(), )
        if len(contrasena) == 0:
            mb.showwarning("IMPORTANTE", "Capturar: La CLAVE para ejecutar las acciones")
        elif contrasena == "P4s3":
                ##Generales
                numtarjeta=str(self.NumTarjeta.get(), )#self.NumTarjeta=tk.StringVar()
            #try:
                if len(numtarjeta) == 0 :
                    mb.showwarning("IMPORTANTE", "Debe Leer primero el Numero de Tarjeta")
                    self.PenNombre.set("")
                    self.PenApellPat.set("")
                    self.PenApellMat.set("")
                    self.PenTelefonoObli.set("")
                    #self.PenTelefonoOpc.set("")
                    self.PenCalle.set("")
                    self.PenColonia.set("")
                    self.PenCiudad.set("")
                    self.PenCP.set("")
                    self.Placas.set("")
                    self.AutoMod.set("")
                    self.AutoColor.set("")
                    #self.enVig2.set("")
                    self.Estatus.set("")
                    self.Montoxmes.set(0)
                    self.comboCortesia.current(0)
                    self.Tole.set(0)
                    self.Clave.set("")
                    self.entryNumTarjeta.focus()
                    self.lbldatosVig2.configure(text=" ")
                    return False
                else :
                    tarjeta=int(numtarjeta)
                    Existe=self.operacion1.ValidarID(tarjeta)
                    if len(Existe) == 0 :
                        mb.showwarning("IMPORTANTE", "No existe Pensionado para ese Num de Tarjeta")
                        self.NumTarjeta.set("")
                        self.entryNumTarjeta.focus()
                        self.PenNombre.set("")
                        self.PenApellPat.set("")
                        self.PenApellMat.set("")
                        self.PenTelefonoObli.set("")
                        #self.PenTelefonoOpc.set("")
                        self.PenCalle.set("")
                        self.PenColonia.set("")
                        self.PenCiudad.set("")
                        self.PenCP.set("")
                        self.Placas.set("")
                        self.AutoMod.set("")
                        self.AutoColor.set("")
                        #self.enVig2.set("")
                        self.Estatus.set("")
                        self.Montoxmes.set(0)
                        self.comboCortesia.current(0)
                        self.Tole.set(0)
                        self.Clave.set("")
                        self.lbldatosVig2.configure(text=" ")
                        return False
                    else:
                        global PensionadoOpen #reasignamos valor a la Variable global
                        PensionadoOpen=Existe #Cachamos el Id_cliente por si se hacen modificaciones
                        #Como le que gusarda es el ID_cleinte, esto permite que se cambie inclusive
                        #el número de tarjeta, que puede suceder si el Pensionado pierde la tarjeta
                        respuesta=self.operacion1.ConsultaPensionado(Existe)
                        #Nom_cliente, Apell1_cliente, Apell2_cliente, Telefono1, Telefono2, Ciudad, Colonia, CP, Calle_num, Placas, Modelo_auto, Color_auto, Fecha_vigencia, Estatus
                        for fila in respuesta:
                            #self.NumTarjeta.set(numtarjeta)
                            self.PenNombre.set(str(fila[0]))
                            self.PenApellPat.set(str(fila[1]))
                            self.PenApellMat.set(str(fila[2]))
                            self.PenTelefonoObli.set(str(fila[3]))
                            #self.PenTelefonoOpc.set(str(fila[4]))
                            self.PenCiudad.set(str(fila[5]))
                            self.PenCalle.set(str(fila[8]))
                            self.PenColonia.set(str(fila[6]))
                            self.PenCP.set(str(fila[7]))
                            self.Placas.set(str(fila[9]))
                            self.AutoMod.set(str(fila[10]))
                            self.AutoColor.set(str(fila[11]))
                            self.lbldatosVig1.configure(text="Vigencia:")
                            if fila[14] == 'Inactiva': #Se lee el campo Vigencia
                                EstVig="INACTIVO"
                            else :
                                EstVig="Activo"
                            if str(fila[16]) == "Si": #Si el Pensionado tiene Cortesia
                                self.comboCortesia.current(0)
                                self.lbldatosVig2.configure(text="Abierta"+"/"+EstVig)
                                global VigenciaOpen #Con esta Variable identificamos si cambiaron de Cortesi a pago
                                VigenciaOpen=0
                                self.Montoxmes.set(str(0))
                            else:
                                self.comboCortesia.current(1) #Cuando el Pensionado NO tiene Cortesia
                                if EstVig == "Activo":
                                    self.lbldatosVig2.configure(text=str(fila[12]))
                                else:
                                    self.lbldatosVig2.configure(text=EstVig)
                                self.Montoxmes.set(str(fila[15]))
                            global VigenciaNva
                            VigenciaNva = fila[12] #Guardamos la fecha de vigencia por si cambiaron de Cortesi a pago, o viceverza
                            self.Tole.set(str(fila[17]))
                            self.Clave.set("")
                            self.entryNumTarjeta.focus()
            #except:
                #mb.showwarning("IMPORTANTE", "Ha ocurrido un error: Revise los datos capturados")
        else:
            mb.showwarning("ERROR", 'CLAVE Incorrecta')


    def ConsulPagoPen(self,event):
        numtarjeta=self.NumTarjeta3.get()
        #print("entro")
        if numtarjeta == "":
            mb.showwarning("IMPORTANTE", "Debe Leer el Numero de Tarjeta")
            self.NumTarjeta3.set("")
            self.entryNumTarjeta3.focus()
            #self.comboMensual.current(0)
        else :
            tarjeta=int(numtarjeta)
            #print(numtarjeta)
            Existe=self.operacion1.ValidarID(tarjeta)
            if len(Existe) == 0 :
                self.NumTarjeta3.set("")
                self.entryNumTarjeta3.focus()
                mb.showwarning("IMPORTANTE", "No existe Cliente para ese Num de Tarjeta")
                return False
            else:
                respuesta=self.operacion1.ConsultaPensionado(Existe)
                #Nom_cliente 0, Apell1_cliente 1, Apell2_cliente 2, Telefono1 3, Telefono2 4, Ciudad 5, Colonia 6,
                #CP 7, Calle_num 8, Placas 9, Modelo_auto 10, Color_auto 11, Fecha_vigencia 12, Estatus 13,
                #Vigencia 14, Monto 15, Cortesia 16, Tolerancia 17
                for fila in respuesta:
                    self.comboMensual.current(0)
                    VigAct=fila[12] #Fecha de Vigencia
                    Estatus=fila[14] # Vigencia Activo/Inactiva
                    monto=fila[15]
                    cortesia=fila[16]
                    print(monto)
                    if cortesia == "Si" :
                       mb.showinfo("IMPORTANTE", "El Pensionado cuenta con CORTESIA")
                       self.NumTarjeta3.set("")
                       self.entryNumTarjeta3.focus()
                    else :
                        if fila[14] == 'Inactiva':
                            EstVig="INACTIVO"
                            self.Estatus.set(EstVig)
                            mes = date.today().month
                            dia = date.today().day
                            if mes == 1: #Enero
                               dias = 31
                               sigue = 28
                            elif mes == 2: #Febrero
                               dias = 28
                               sigue = 31
                            elif mes == 3: #Marzo
                               dias = 31
                               sigue = 30
                            elif mes == 4: #Abril
                               dias = 30
                               sigue = 31
                            elif mes == 5: #Mayo
                               dias = 31
                               sigue = 30
                            elif mes == 6: #Junio
                               dias = 30
                               sigue = 31
                            elif mes == 7: #Julio
                               dias = 31
                               sigue = 31
                            elif mes == 8: #Agosto
                               dias = 31
                               sigue = 31
                            elif mes == 9: #Septiembre
                               dias = 30
                               sigue = 31
                            elif mes == 10: #Octubre
                               dias = 31
                               sigue = 30
                            elif mes == 11: #Noviembre
                               dias = 30
                               sigue = 31
                            elif mes == 12: #Diciembre
                               dias = 31
                               sigue = 30
                            ##Si Pensionado paga por primera vez sólo paga los días faltantes al cierre de mes
                            ##Esto se hizo así a petición de Alberto Ordaz
                            if (dias - dia) > 0:
                               pago = (monto/dias)*(dias-dia)
                               NvaVigencia = date.today() + timedelta(days = (dias-dia))
                               self.Monto.set(pago)
                            elif (dias - dia) == 0:
                               pago = monto
                               NvaVigencia = date.today() + timedelta(days = sigue)
                        else:
                           self.Estatus.set(Estatus)
                           pago = monto
                        self.Monto.set(pago)
                        self.comboMensual.focus()
                        self.Vigencia.set(VigAct)

    def Cobro_Pensionado(self):
        numtarjeta=self.NumTarjeta3.get()
        try:
            if (self.variable_tipo_pago_transferencia.get() == False) and (self.variable_tipo_pago_efectivo.get() == False):raise TypeError("Selecciona una forma de pago")

            #usuario = self.operacion1.nombre_usuario_activo()
            #usuario = str(usuario[0][0])
            usuario = "prueba"

            #Generales
            nummes=int(self.comboMensual.get())
            fechaPago=datetime.now()
            fechaPago = fechaPago.strftime("%Y-%m-%d %H:%M:%S")

            if len(numtarjeta) == 0 :
                mb.showwarning("IMPORTANTE", "Debe Leer el Numero de Tarjeta")
                self.comboMensual.current(0)
                self.entryNumTarjeta.focus()
                return False
            else :

                tarjeta=int(numtarjeta)
                Existe=self.operacion1.ValidarID(tarjeta)
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
                        Nom_cliente = fila[0]
                        Apell1_cliente = fila[1]
                        Apell2_cliente = fila[2]
                        VigAct=fila[12] #Fecha de Vigencia Actual
                        #VigActShow= datetime.strptime(VigAct, '%Y-%m-%d')
                        Estatus=fila[14] #Activo/Inactiva
                        monto=fila[15]
                        cortesia=fila[16]
                        Tolerancia=int(fila[17])
                        self.Vigencia.set(VigAct)
                        self.Estatus.set(Estatus)
                        self.entryNumTarjeta3.focus()
                    #Calculando la Nueva Vigencia apartir del dia de Pago
                    #Calculo de Vigencia Pensionado Paga
                    mes = date.today().month

                    dia = date.today().day
                    if mes == 1: #Enero
                       dias = 31
                       sigue = 28
                    elif mes == 2: #Febrero
                       dias = 28
                       sigue = 31
                    elif mes == 3: #Marzo
                       dias = 31
                       sigue = 30
                    elif mes == 4: #Abril
                       dias = 30
                       sigue = 31
                    elif mes == 5: #Mayo
                       dias = 31
                       sigue = 30
                    elif mes == 6: #Junio
                       dias = 30
                       sigue = 31
                    elif mes == 7: #Julio
                       dias = 31
                       sigue = 31
                    elif mes == 8: #Agosto
                       dias = 31
                       sigue = 31
                    elif mes == 9: #Septiembre
                       dias = 30
                       sigue = 31
                    elif mes == 10: #Octubre
                       dias = 31
                       sigue = 30
                    elif mes == 11: #Noviembre
                       dias = 30
                       sigue = 31
                    elif mes == 12: #Diciembre
                        dias = 31
                        sigue = 30

                    if Estatus == "Inactiva": #VigAct
                    ##Si Pensionado paga por primera vez sólo paga los días faltantes al cierre de mes
                    ##Esto se hizo así a petición de Alberto Ordaz
                        if (dias - dia) > 0:
                            pago = (monto/dias)*(dias-dia)
                            NvaVigencia = self.nueva_vigencia(VigAct)
                        elif (dias - dia) == 0:
                            pago = monto
                            NvaVigencia = self.nueva_vigencia(VigAct)
                    else:
                        pago = monto*nummes
                        NvaVigencia = self.nueva_vigencia(VigAct)

                    NvaVigencia = datetime.strptime(NvaVigencia, "%Y-%m-%d %H:%M:%S")
                    NvaVigencia = NvaVigencia.strftime("%Y-%m-%d %H:%M:%S")

                    datos=(Existe, tarjeta, fechaPago, NvaVigencia, nummes, pago, self.tipo_pago_)
                    datos1=("Activo", NvaVigencia, Existe)
                    self.operacion1.CobrosPensionado(datos)
                    self.operacion1.UpdPensionado(datos1)


                    self.imprimir_comprobante_pago_pensionado(
                                                             numero_tarjeta = tarjeta,
                                                             Nom_cliente = Nom_cliente,
                                                             Apell1_cliente = Apell1_cliente,
                                                             Apell2_cliente = Apell2_cliente,
                                                             fecha_pago = fechaPago,
                                                             vigencia = NvaVigencia[:10],
                                                             monto = pago,
                                                             usuario = usuario,
                                                             tipo_pago = self.tipo_pago_)

                    mb.showinfo("IMPORTANTE", "PAGO realizado con éxito")
                    self.Monto.set("")
                    self.Vigencia.set("")
                    self.Estatus.set("")
                    self.comboMensual.current(0)
                    self.NumTarjeta3.set("")
                    self.entryNumTarjeta3.focus()
                    self.vaciar_tipo_pago()

        except TypeError as e:
            mb.showwarning(f"IMPORTANTE", e)
            traceback.print_exc()

        except Exception as e:
            print(e)
            mb.showwarning("IMPORTANTE", "Ha ocurrido un error: Revise los datos capturados")
            self.Monto.set("")
            self.comboMensual.current(0)
            self.Vigencia.set("")
            self.Estatus.set("")
            self.NumTarjeta3.set("")
            self.entryNumTarjeta3.focus()

    def PenAdentro(self):
        self.scrolledPen.configure(state="normal")
        respuesta=self.operacion1.TreaPenAdentro()
        self.scrolledPen.delete("1.0", tk.END)
        cont=0
        for fila in respuesta:
            self.scrolledPen.insert(tk.END, f"{cont+1}) {fila[0]}: \n   {fila[1]} {fila[2]}\n   {fila[3]} - {fila[4]}\n\n")
            cont=cont+1
        self.lbldatosTotPen.configure(text="PENSIONADOS ADENTRO: "+str(cont))
        self.scrolledPen.configure(state="disabled")


    def imprimir_comprobante_pago_pensionado(self,
                                            numero_tarjeta: str,
                                            Nom_cliente: str,
                                            Apell1_cliente: str,
                                            Apell2_cliente: str,
                                            fecha_pago: str,
                                            vigencia: str,
                                            monto: float,
                                            usuario: str,
                                            tipo_pago: str) -> None:
        """Imprime un comprobante de pago de una pensión.
        Args:
            numero_tarjeta (str): El número de tarjeta del pensionado.
            Nom_cliente (str): El nombre del pensionado.
            Apell1_cliente (str): El primer apellido del pensionado.
            Apell2_cliente (str): El segundo apellido del pensionado.
            fecha_pago (str): La fecha en que se hizo el pago.
            vigencia (str): La fecha de vigencia de la pensión.
            monto (float): El monto que se pagó.
            usuario (str): Nombre del usuario en turno.
            tipo_pago (str): Tipo de pago.
        Returns:
            None: Esta función no devuelve nada, simplemente imprime un comprobante.
        Raises:
            None
        """

        p.text("----------------------------------\n")
        # Agrega un encabezado al comprobante
        p.text("        Comprobante de pago\n\n")

        # Establece la alineación del texto a la izquierda
        p.set(align="left")
        # Agrega información sobre el pago al comprobante
        p.image("LOGO1.jpg")
        p.text(f"Numero de tarjeta: {numero_tarjeta}\n")
        p.text(f"Nombre: {Nom_cliente}\n")
        p.text(f"Apellido 1: {Apell1_cliente}\n")
        p.text(f"Apellido 2: {Apell2_cliente}\n")
        p.text(f"Fecha de pago: {fecha_pago}\n")
        p.text(f"Monto pagado: ${monto}\n")
        p.text(f"Tipo de pago: {tipo_pago}\n")
        p.text(f"Cobro: {usuario}\n\n")
        p.text(f"Fecha de vigencia: {vigencia}\n")

        p.text("----------------------------------\n")

        # Corta el papel para finalizar la impresión
        p.cut()

    def cambiar_valor(self, contrario):
        """Cambia el valor de la variable según las variables de tipo de pago seleccionadas.
        Args:
            contrario (BooleanVar): Una variable booleana que se utiliza para establecer un valor opuesto.
        Returns:
            None
        """
        try:
            # Establece la variable contrario como False
            contrario.set(False)

            # Si la variable de tipo de pago transferencia está seleccionada, establece tipo_pago_ como "Transferencia"
            if self.variable_tipo_pago_transferencia.get():
                self.tipo_pago_ = "Transferencia"

            # Si la variable de tipo de pago efectivo está seleccionada, establece tipo_pago_ como "Efectivo"
            elif self.variable_tipo_pago_efectivo.get():
                self.tipo_pago_ = "Efectivo"

            # Si ninguna de las variables de tipo de pago está seleccionada, establece tipo_pago_ como None
            else:
                self.tipo_pago_ = None

        except Exception as e:
            # Si ocurre un error, no hace nada
            pass

    def vaciar_tipo_pago(self):
        """Vacia las variables de tipo de pago.
        Returns:
            None
        """
        # Establece las variables de tipo de pago como False
        self.variable_tipo_pago_transferencia.set(False)
        self.variable_tipo_pago_efectivo.set(False)

    def nueva_vigencia(self, fecha):
        """
        Obtiene la fecha del último día del mes siguiente a la fecha dada y la devuelve como una cadena de texto en el formato '%Y-%m-%d %H:%M:%S'.

        :param fecha (str or datetime): Fecha a partir de la cual se obtendrá la fecha del último día del mes siguiente.

        :raises: TypeError si la fecha no es una cadena de texto ni un objeto datetime.

        :return:
            - nueva_vigencia (str): Una cadena de texto en el formato '%Y-%m-%d %H:%M:%S' que representa la fecha del último día del mes siguiente a la fecha dada.
        """
        try:
            if fecha == None:
                # Obtener la fecha y hora actual en formato deseado
                fecha = datetime.today().strftime("%Y-%m-%d 23:59:59")

                # fecha = "2023-04-30 23:59:59"

                # Convertir la cadena de caracteres en un objeto datetime
                fecha = datetime.strptime(fecha, "%Y-%m-%d 23:59:59")

                fecha = fecha - relativedelta(months=1)

            # Verificar que la fecha sea de tipo str o datetime
            elif not isinstance(fecha, (str, datetime)):
                raise TypeError("La fecha debe ser una cadena de texto o un objeto datetime.")
            
            # Convertir la fecha dada en un objeto datetime si es de tipo str
            elif isinstance(fecha, str):
                fecha = datetime.strptime(fecha, '%Y-%m-%d 23:59:59')
            
            # Obtener la fecha del primer día del siguiente mes
            mes_siguiente = fecha + relativedelta(months=1, day=1)
            
            # Obtener la fecha del último día del mes siguiente
            ultimo_dia_mes_siguiente = mes_siguiente + relativedelta(day=31)
            if ultimo_dia_mes_siguiente.month != mes_siguiente.month:
                ultimo_dia_mes_siguiente -= relativedelta(days=1)
            
            # convertir la fecha del último día del mes siguiente en formato de cadena
            nueva_vigencia = ultimo_dia_mes_siguiente.strftime('%Y-%m-%d 23:59:59')

            # Devolver el valor
            return nueva_vigencia
        
        except TypeError as e:
            mb.showwarning("Error", f"{e}")
        except Exception as e:
            mb.showwarning("Error", f"{e}")

    def BoletoDañado(self):
        """
        Esta función se encarga de manejar el cobro de un boleto dañado.

        Verifica si se ha ingresado un número de folio para el boleto dañado y realiza las operaciones correspondientes.
        Muestra información relevante del boleto dañado y establece el tipo de pago como "Danado".

        :param self: Objeto de la clase que contiene los atributos y métodos necesarios.

        :return: None
        """

        datos = self.PonerFOLIO.get()
        self.folio.set(str(datos))
        datos = self.folio.get()

        if len(datos) > 0:
            respuesta = self.operacion1.consulta(datos)
            if len(respuesta) > 0:
                if respuesta[0][6] == "BoletoPerdido":
                    mb.showerror("Error", "No se puede cobrar como maltratado un boleto perdido")
                    self.PonerFOLIO.set("")
                    self.folio.set("")
                    return None

                else:
                    self.descripcion.set(respuesta[0][0])
                    self.precio.set(respuesta[0][1])
                    self.CalculaPermanencia()
                    self.PrTi.set("Danado")

            else:
                self.descripcion.set('')
                self.precio.set('')
                self.PonerFOLIO.set('')

                mb.showinfo("Información", "No existe un auto con dicho código")
        else:
            mb.showinfo("Error", "Ingrese el folio del boleto dañado")
            self.folio.set("")
            self.entryfolio.focus()




#aplicacion1=FormularioOperacion()
