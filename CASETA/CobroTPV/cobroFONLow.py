from datetime import datetime, date, time, timedelta
from tkinter import messagebox as mb

PensionadoOpen=1

from escpos.printer import *

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb
from tkinter import scrolledtext as st

from tkinter import *
from tkinter import simpledialog

from operacion import Operacion
import xlsxwriter




p = Usb(0x04b8, 0x0e15, 0)
penalizacion_con_importe = False
from dateutil.relativedelta import relativedelta
from view_login import View_Login
from queries import Pensionados
from view_agregar_pensionado import View_agregar_pensionados
from view_modificar_pensionado import View_modificar_pensionados
import traceback
import math

import atexit

contraseña_pensionados = "P4s3"

valor_tarjeta = 116
valor_reposiion_tarjeta = 232
penalizacion_diaria_pension = 0

logo_1 = "LOGO1.jpg"
qr_imagen = "reducida.png"
PROMOCIONES = ('EV ANUIE', 'ev anuie', 'A2 ANUIS', "a2 anuis", "A1 ANUIE", "a1 anuie")#, 'CN CENEV')

nombre_estacionamiento = 'Tenayuca'

from controller_email import main

class FormularioOperacion:
    def __init__(self):
        atexit.register(main)

        self.controlador_crud_pensionados = Pensionados()
        self.folio_auxiliar = None

        self.DB=Operacion()
        self.ventana1=tk.Tk()
        self.ventana1.title(f"{nombre_estacionamiento} COBRO")
        self.cuaderno1 = ttk.Notebook(self.ventana1)
        self.cuaderno1.config(cursor="")         # Tipo de cursor
        self.ExpedirRfid()
        self.consulta_por_folio()
        self.listado_completo()
        self.interface_pensionados()
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
        respuesta=self.DB.Autos_dentro()
        self.scrolledtext.delete("1.0", tk.END)
        for fila in respuesta:
            self.scrolledtext.insert(tk.END, "Entrada num: "+str(fila[0])+"\nEntro: "+str(fila[1])[:-3]+"\n\n")

    def agregarRegistroRFID(self):
        #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$impresion    $$$$$$$$$$$$$$$$$$$
        MaxFolio=str(self.DB.MaxfolioEntrada())
        MaxFolio = MaxFolio.strip("[(,)]")
        n1 = MaxFolio
        n2 = "1"
        masuno = int(n1)+int(n2)
        masuno = str(masuno)
        self.MaxId.set(masuno)

        folio_cifrado = self.DB.cifrar_folio(folio = masuno)
        # print(f"QR entrada: {folio_cifrado}")

        #Generar QR
        self.DB.generar_QR(folio_cifrado)

        fechaEntro = datetime.today()

        horaentrada = str(fechaEntro)
        horaentrada=horaentrada[:19]
        self.labelhr.configure(text=(horaentrada[:-3], "Entro"))
        corteNum = 0
        placa=str(self.Placa.get(), )
        datos=(fechaEntro, corteNum, placa)

        p.image(logo_1)
        p.text("--------------------------------------\n")
        p.set(align="center")
        p.text("BOLETO DE ENTRADA\n")
        folioZZ=('FOLIO 000' + masuno)
        p.text('Entro: '+horaentrada[:-3]+'\n')
        p.text('Placas '+placa+'\n')
        p.text(folioZZ+'\n')

        p.set(align = "center")
        p.image(qr_imagen)

        p.text("--------------------------------------\n")
        p.cut()

        self.DB.altaRegistroRFID(datos)
        self.Placa.set('')


    #########################fin de pagina1 inicio pagina2#########################
    def consulta_por_folio(self):
        self.pagina2 = ttk.Frame(self.cuaderno1)
        self.cuaderno1.add(self.pagina2, text=" Modulo de Cobro")
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
        self.cuantopagasen.set(100)
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


        self.IImporte = ttk.Label(self.labelframe3, text="") #Creacion del Label
        self.IImporte.config(width =4)
        self.IImporte.config(background="white") #Cambiar color de fondo
        self.IImporte.config(font=('Arial', 48)) #Cambiar tipo y tamaño de fuente
        self.IImporte.grid(column=1, row=4, padx=0, pady=0)   


        #se crea objeto para MOSTRAR LA HORA DEL CALCULO
        self.copia_fecha_salida = tk.StringVar()
        self.entry_copia_fecha_salida=tk.Entry(self.labelframe3, width=15, textvariable=self.copia_fecha_salida, state = "readonly")
        self.entry_copia_fecha_salida.grid(column=1, row=1)

        #SE CREA UN OBJETO caja de texto IGUAL A LOS DEMAS Y MUESTRA EL TOTAL DEL TIEMPO
        self.TiempoTotal=tk.StringVar()
        self.TiempoTotal_auxiliar=tk.StringVar()
        self.entryTiempoTotal=tk.Entry(self.labelframe3, width=15, textvariable=self.TiempoTotal_auxiliar, state= "readonly")
        self.entryTiempoTotal.grid(column=1, row=2)
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
        self.fecha_entrada=tk.StringVar()
        self.entry_fecha_entrada=ttk.Entry(self.labelframe2, textvariable=self.fecha_entrada, state="readonly",  width=15)
        self.entry_fecha_entrada.grid(column=1, row=1, padx=4, pady=4, sticky=tk.NW)

        #se crea objeto para mostrar el dato la Salida solo lectura
        self.fecha_salida=tk.StringVar()
        self.entry_fecha_salida=ttk.Entry(self.labelframe2, textvariable=self.fecha_salida, state="readonly",  width=15)
        self.entry_fecha_salida.grid(column=1, row=2, padx=4, pady=4, sticky=tk.NW)

        #creamos un objeto para obtener la lectura de la PROMOCION
        self.promo=tk.StringVar()
        self.promo_auxiliar=tk.StringVar()
        self.entrypromo=tk.Entry(self.labelpromo, textvariable=self.promo)
        self.entrypromo.bind('<Return>',self.CalculaPromocion)#con esto se lee automatico
        self.entrypromo.grid(column=1, row=0, padx=4, pady=4)           
        #este es donde pongo el tipo de PROMOCION
        self.TarifaPreferente=tk.StringVar()
        self.entryTarifaPreferente=tk.Entry(self.labelpromo, width=20, textvariable=self.TarifaPreferente, state= "readonly")
        self.entryTarifaPreferente.grid(column=1, row=1)
        #botones


        self.bcambio=tk.Button(self.labelcuantopagas, text="Cobro", command=self.calcular_cambio, width=10, height=2, anchor="center", background="red")
        self.bcambio.grid(column=0, row=4)

        self.BoletoDentro()


    def BoletoDentro(self):
        respuesta=self.DB.Autos_dentro()
        self.scrolledtxt.delete("1.0", tk.END)
        for fila in respuesta:
            self.scrolledtxt.insert(tk.END, "Folio num: "+str(fila[0])+"\nEntro: "+str(fila[1])[:-3]+"\nPlacas: "+str(fila[2])+"\n\n")

    def BoletoPerdido_conFolio(self):
        """
        Esta funcion se encarga de manejar el cobro de un boleto perdido con folio.

        Verifica si se ha ingresado un número de folio para el boleto perdido y realiza las operaciones correspondientes.
        Calcula la permanencia del vehículo y el importe a cobrar.
        Establece el concepto del boleto como "Per" de perdido.

        :param self: Objeto de la clase que contiene los atributos y métodos necesarios.

        :return: None
        """

        datos = self.PonerFOLIO.get()

        if len(datos) == 0:
            mb.showerror("Error", "Ingrese un folio")
            return

        self.folio.set(datos)
        datos = self.folio.get()
        self.folio_auxiliar = datos
        importe = 0

        # Consultar los datos correspondientes al folio
        respuesta = self.DB.consulta(datos)
        if len(respuesta) > 0:
            # Establecer la descripcion y precio basados en la respuesta
            self.fecha_entrada.set(respuesta[0][0])
            self.fecha_salida.set(respuesta[0][1])
            self.Placa.set(respuesta[0][6])

            # Calcular la permanencia
            self.CalculaPermanencia()


            if penalizacion_con_importe:

                # Calcular el importe basado en las horas y días de permanencia
                if self.horas_dentro <= 24:
                    importe = 200 + ((self.dias_dentro) * 720 + (self.horas_dentro * 20))
                elif self.horas_dentro > 24 or self.dias_dentro >= 1:
                    importe = 200 + ((self.dias_dentro) * 720 + (self.horas_dentro * 20))

            else:
                importe = 250

            # Establecer el importe y mostrarlo
            self.mostrar_importe(importe)

            # Realizar otras operaciones y configuraciones
            self.TarifaPreferente.set("Per")
            self.promo.set("")
            self.PonerFOLIO.set("")

        else:
            # Limpiar campos y mostrar mensaje de error
            self.limpiar_campos()
            mb.showinfo("Informacion", "No existe un auto con dicho codigo")

    def BoletoPerdido_sinFolio(self):
        """
        Esta funcion se encarga de imprimir un boleto perdido sin un número de folio especificado.

        Verifica si se ha confirmado la impresion del boleto perdido.
        Genera un boleto nuevo para poder cobrar boletos que han sido extraviados.
        Agrega el registro del pago a la base de datos.

        :return: None
        """
        Boleto_perdido = mb.askokcancel("Advertencia", f"¿Esta seguro de imprimir un boleto perdido?")

        if Boleto_perdido:
            MaxFolio=str(self.DB.MaxfolioEntrada())
            MaxFolio = MaxFolio.strip("[(,)]")
            n1 = MaxFolio
            n2 = "1"
            masuno = int(n1)+int(n2)
            masuno = str(masuno)
            self.MaxId.set(masuno)

            fechaEntro = datetime.today()
            horaentrada = str(fechaEntro)
            horaentrada=horaentrada[:19]
            corteNum = 0
            placa="BoletoPerdido"
            datos=(fechaEntro, corteNum, placa)

            #aqui lo imprimimos

            p.image(logo_1)
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
            self.DB.altaRegistroRFID(datos)
            self.Placa.set('')

        self.BoletoDentro()
        self.BoletoDentro2()

    def consultar(self, event):
        # Vaciar campo de importe
        self.IImporte.config(text="")

        # Obtener folio
        datos=str(self.folio.get())

        # Si la caja de texto esta vacia limpia la informacion en pantalla
        if len(datos) == 0:
            self.limpiar_campos()
            self.entryfolio.focus()
            return

        #Verificar si lee el folio o la promocion
        if len(datos) > 20:

            mb.showinfo("Promocion", "leer primero el folio")
            self.limpiar_campos()
            self.entryfolio.focus()
            return

        folio = self.DB.descifrar_folio(folio_cifrado = datos)
        self.folio.set(folio)
        folio = self.folio.get()
        self.folio_auxiliar = folio
        print(f"\nFolio descifrado: {folio}")

        respuesta=self.DB.consulta(folio)
        if len(respuesta) == 0:
            mb.showinfo("Informacion", "No existe un auto con dicho codigo")
            self.limpiar_campos()
            return

        self.fecha_entrada.set(respuesta[0][0])
        self.fecha_salida.set(respuesta[0][1])
        self.Placa.set(respuesta[0][6])
        self.CalculaPermanencia()#nos vamos a la funcion de calcular permanencia


    def CalculaPermanencia(self):
        """
        Esta funcion calcula la permanencia del folio seleccionado.

        Realiza diferentes cálculos basados en la informacion del boleto y actualiza los valores correspondientes.

        :param self: Objeto de la clase que contiene los atributos y métodos necesarios.

        :return: None
        """
        # Borra el valor actual del importe
        self.IImporte.config(text="")

        # Obtiene el valor de salida
        salida = self.fecha_salida.get()

        if len(salida) > 5:
            # Si el valor de salida tiene más de 5 caracteres, significa que ya ha sido cobrado
            self.label15.configure(text=("Este Boleto ya Tiene cobro"))

            # Realiza una consulta con el folio seleccionado para obtener informacion adicional del boleto
            respuesta = self.DB.consulta({self.folio.get()})

            # Imprime en una caja de texto la informacion del boleto cuando ya ha sido cobrado
            self.scrol_datos_boleto_cobrado.delete("1.0", tk.END)
            for fila in respuesta:
                self.scrol_datos_boleto_cobrado.insert(
                    tk.END,
                    f"Folio: {fila[2]}\nEntro: {str(fila[0])[:-3]}\nSalio: {str(fila[1])[:-3]}\nTiempo: {str(fila[3])[:-3]}\nTarifa: {fila[4]}\nImporte: {fila[5]}"
                )

            pregunta = mb.askyesno("Advertencia", "Este boleto ya tiene cobro ¿Desea reimprimir el comprobante de pago?")

            if pregunta:

                Entrada = respuesta[0][0]
                Salida = respuesta[0][1]

                folio = respuesta[0][2]
                TiempoTotal = str(respuesta[0][3])
                TarifaPreferente = respuesta[0][4]
                Importe = respuesta[0][5]
                Placas = respuesta[0][6]

                self.Placa.set(Placas)
                self.folio.set(folio)
                self.TarifaPreferente.set(TarifaPreferente)
                self.importe.set(Importe)
                self.fecha_entrada.set(Entrada)
                self.copia_fecha_salida.set(Salida)
                self.TiempoTotal.set(TiempoTotal)

                self.Comprobante(titulo='REIMPRESION')

            # Reinicia los valores de varios atributos
            self.limpiar_campos()
            return

        # Si el valor de salida tiene menos de 5 caracteres, significa que no ha sido cobrado
        self.scrol_datos_boleto_cobrado.delete("1.0", tk.END)
        self.TarifaPreferente.set("Normal")
        self.label15.configure(text="Lo puedes COBRAR")

        # Obtiene la fecha actual
        Salida = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        Salida = datetime.strptime(Salida, '%Y-%m-%d %H:%M:%S')

        self.copia_fecha_salida.set(Salida)


        # Obtiene la fecha del boleto seleccionado y realiza las conversiones necesarias
        Entrada = self.fecha_entrada.get()
        Entrada = datetime.strptime(Entrada, '%Y-%m-%d %H:%M:%S')

        TiempoTotal = Salida - Entrada

        # Calcula la diferencia en días, horas y minutos
        self.dias_dentro = TiempoTotal.days
        segundos_vividos = TiempoTotal.seconds

        self.horas_dentro, segundos_vividos = divmod(segundos_vividos, 3600)
        self.minutos_dentro, segundos_vividos = divmod(segundos_vividos, 60)

        self.TiempoTotal.set(TiempoTotal)
        self.TiempoTotal_auxiliar.set(self.TiempoTotal.get()[:-3])

        # Calcula la tarifa y el importe a pagar
        if self.minutos_dentro == 0:
            minutos = 0
        elif self.minutos_dentro < 16 and self.minutos_dentro >= 1:
            minutos = 1
        elif self.minutos_dentro < 31 and self.minutos_dentro >= 16:
            minutos = 2
        elif self.minutos_dentro < 46 and self.minutos_dentro >= 31:
            minutos = 3
        elif self.minutos_dentro <= 59 and self.minutos_dentro >= 46:
            minutos = 4

        importe = 0

        if self.dias_dentro == 0 and self.horas_dentro == 0:
            # Si la permanencia es menor a 1 hora, se aplica una tarifa fija de 20 unidades
            importe = 20
        else:
            # Si la permanencia es mayor a 1 hora, se calcula el importe según una formula específica
            importe = ((self.dias_dentro) * 250 + (self.horas_dentro * 20) + (minutos) * 5)

        # Establecer el importe y mostrarlo
        self.mostrar_importe(importe)

        # Coloca el foco en el campo entrypromo
        self.entrypromo.focus()

    def calcular_cambio(self):
        folio = self.folio.get()
        if len(folio) == 0:
            mb.showerror("Error", "Error vuelva a escanear el QR del boleto")

            # Reinicia los valores de varios atributos
            self.limpiar_campos()
            return

        if self.folio_auxiliar != folio:
            mb.showerror("Error", "Error vuelva a escanear el QR del boleto")

            # Reinicia los valores de varios atributos
            self.limpiar_campos()
            return

        elimporte=str(self.importe.get(), )
        self.elimportees.set(elimporte)
        valorescrito=str(self.cuantopagasen.get(),)
        elimporte=float(elimporte)
        valorescrito=int(valorescrito)

        cambio=valorescrito-elimporte
        cambio=str(cambio)

        self.elcambioes.set(cambio)

        self.GuardarCobro()

        self.Comprobante(QR_salida=True)
        self.Comprobante(titulo='CONTRA', imagen_logo=False)

        self.limpiar_campos()



    def Comprobante(self, titulo: str = 'Comprobante de pago', imagen_logo: bool = True, QR_salida: bool = False) -> None:
        """Genera un comprobante de pago o un boleto cancelado.

        Args:
            titulo (str, optional): El título del comprobante. Por defecto es 'Comprobante de pago'.
            imagen_logo (bool, optional): Indica si se debe imprimir una imagen de logo en el comprobante. Por defecto es True.
            QR_salida (bool, optional): Indica si se debe imprimir un codigo QR de salida en el comprobante. Por defecto es False.
        """

        # Obtiene los valores de diferentes variables desde las variables de control
        Placa = self.Placa.get()
        Folio = self.folio.get()
        TarifaPreferente = self.TarifaPreferente.get()
        Importe = self.importe.get()
        Entrada = self.fecha_entrada.get()[:-3]
        Salida = self.copia_fecha_salida.get()[:-3]
        TiempoTotal = self.TiempoTotal.get()[:-3]

        valor = 'N/A'

        # Configuracion de la impresora
        p.set(align="center")
        p.text(f"{titulo}\n")

        if titulo == "Boleto Cancelado":
            # Seccion de comprobante para boletos cancelados
            p.set(align="left")

            p.text(f'Folio boleto cancelado: {Folio}\n')
            hoy = datetime.today().strftime("%b-%d-%A-%Y %H:%M:%S")
            p.set('Big line\n', font='b')
            p.text(f'Fecha: {hoy[:-3]}\n')
            p.text(f'El auto entro: {Entrada}\n')
            p.text(f'El auto salio: {Salida}\n')
        else:
            # Seccion de comprobante para pagos normales o boletos perdidos

            if Placa == "BoletoPerdido":
                # Si es un boleto perdido, muestra un mensaje especial
                p.text("BOLETO PERDIDO\n")
                Entrada = valor
                Salida = valor
                TiempoTotal = valor

            if imagen_logo:
                imgqr = (Salida + Folio)
                self.DB.generar_QR(imgqr)

                # Imprimir el logo si está habilitado
                p.image(logo_1)
                print("Imprime logo")
            p.set(align="left")

            p.text("El importe es: $" + Importe + "\n")
            p.text('El auto entro: ' + Entrada + '\n')
            p.text('El auto salio: ' + Salida + '\n')
            p.text('El auto permanecio: ' + TiempoTotal + '\n')
            p.text('El folio del boleto es: ' + Folio + '\n')
            p.text('TIPO DE COBRO: ' + TarifaPreferente + '\n')

            if QR_salida:
                # Imprimir el codigo QR de salida si está habilitado
                p.set(align="center")
                p.image(qr_imagen)
                print("Imprime QR salida")

        p.cut()


    def GuardarCobro(self):
        """Guarda la informacion de un cobro realizado en la base de datos."""

        # Obtener el valor del codigo QR de promocion (si está presente, de lo contrario, será None)
        QRPromo = self.promo_auxiliar.get()
        if QRPromo == '': QRPromo = None

        # Obtener el valor del folio del boleto
        folio = self.folio.get()

        # Realiza una consulta con el folio seleccionado para obtener informacion adicional del boleto
        respuesta = self.DB.consulta(folio)

        if len(respuesta) == 0:
            # Si no se encuentra el boleto con el folio proporcionado, muestra un mensaje de error y sale de la funcion
            mb.showerror("Error", f"Ha ocurrido un error al realizar el cobro, escanee nuevamente el QR")
            return

        # Obtener valores adicionales del boleto
        Entrada = self.fecha_entrada.get()
        Salida = self.copia_fecha_salida.get()
        TiempoTotal = self.TiempoTotal.get()
        TarifaPreferente = self.TarifaPreferente.get()
        importe = self.importe.get()

        # Configurar una etiqueta con informacion de prueba
        self.label15.configure(text=(Salida, "SI se debe modificar"))

        # Valor para verificar el cobro (valor de ejemplo)
        vobo = "lmf"

        # Crear una tupla con los datos del cobro
        datos = (vobo, importe, TiempoTotal, Entrada, Salida, TarifaPreferente, QRPromo, folio)

        # Guardar el cobro en la base de datos
        self.DB.guardacobro(datos)


    def CalculaPromocion(self, event):
        """
        Esta funcion se encarga de aplicar una promocion al boleto seleccionado.

        :param event: Evento que activa la funcion.

        :return: None
        """

        # Valida si el boleto está cobrado como perdido
        TarifaPreferente = self.TarifaPreferente.get()
        if TarifaPreferente == "Per":
            mb.showerror("Error", "A los boletos cobrados como perdidos no se pueden aplicar promociones")
            self.promo.set('')
            self.promo_auxiliar.set('')
            self.entrypromo.focus()
            return

        # Valida que solo se pueda aplicar una promocion por boleto
        if TarifaPreferente not in ["Normal", "Danado"]:
            mb.showerror("Error", "Solo se puede aplicar una promocion por boleto")
            self.promo.set('')
            self.entrypromo.focus()
            return

        # Obtiene el tipo de promocion
        QRPromo = self.promo.get()

        # Obtiene las primeras 8 letras de la promocion (se asume que son suficientes para identificar el tipo de promocion)
        TipoPromo = QRPromo[:8]

        # Verifica si la promocion es conocida en el diccionario PROMOCIONES
        if TipoPromo not in PROMOCIONES:
            mb.showwarning("IMPORTANTE", "Promocion desconocida, escanee nuevamente el QR de promocion")
            self.promo.set('')
            self.promo_auxiliar.set('')
            self.entrypromo.focus()
            return

        # Valida si la promocion ya fue aplicada previamente
        respuesta = self.DB.ValidaPromo(QRPromo)

        if len(respuesta) > 0:
            mb.showwarning("IMPORTANTE", "LA PROMOCION YA FUE APLICADA")
            self.promo.set('')
            self.promo_auxiliar.set('')
            self.entrypromo.focus()
            return

        self.promo_auxiliar.set(QRPromo)
        # Obtiene el importe actual
        importe = int(self.importe.get())

        # Aplica diferentes descuentos según el tipo de promocion
        if TipoPromo==("EV ANUIE") or TipoPromo==("ev anuie"):

            if self.horas_dentro <= 8 and self.minutos_dentro < 1:
                importe = 80

            else:# self.horas_dentro > 8:
                importe= importe - 80

            text_promo = "EVENTO"

        elif TipoPromo==("a1 anuie") or TipoPromo==("A1 ANUIE"):

            if self.horas_dentro <= 1:
                if self.horas_dentro == 1 and self.minutos_dentro >= 1:
                    importe = importe - 20
                else:
                    importe = 0

            else:#if self.horas_dentro > 1:
                importe = importe - 20


            text_promo = "ANUIS1"

        elif TipoPromo==("A2 ANUIS") or TipoPromo==("a2 anuis"):

            if self.horas_dentro <= 2:
                if self.horas_dentro == 2 and self.minutos_dentro >= 1:
                    importe = importe - 40
                else:
                    importe = 0

            else:#if self.horas_dentro > 1:
                importe = importe - 40

            text_promo = "ANUIS2"

        # elif TipoPromo==("CN CENEV") or TipoPromo==("cn cenev"):

        #     if self.horas_dentro <= 8 and self.minutos_dentro < 1:
        #         importe = 80

        #     if self.horas_dentro >= 8:
        #         importe = importe - 140

        #     text_promo = "CENEVAL"

        # Añade "Danado" a la descripcion de la promocion si el boleto está marcado como "Danado"
        if TarifaPreferente == "Danado":
            text_promo = text_promo + TarifaPreferente

        # Establece el tipo de promocion y muestra el importe actualizado
        self.TarifaPreferente.set(text_promo)
        self.promo.set("")
        self.mostrar_importe(importe)





    ###################### Fin de Pagina2 Inicio Pagina3 ###############################
    def listado_completo(self):
        self.pagina3 = ttk.Frame(self.cuaderno1)
        self.cuaderno1.add(self.pagina3, text="Modulo de Corte")
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


        self.seccion_boton_usuario = ttk.LabelFrame(self.labelframe5, text='Administrar usuarios')
        self.seccion_boton_usuario.grid(column=3, row=3, padx=4, pady=4, sticky='NESW') 

        self.boton_usuarios=tk.Button(self.seccion_boton_usuario, text="Entrar",	 
        command=lambda:{
                self.desactivar(),
                View_Login(),
                self.activar()
                },
        width=15, height=1, anchor="center", background="red")
        self.boton_usuarios.grid(column=0, row=0, padx=4, pady=4)

        self.BoletoDentro2()

    def BoletoDentro2(self):
        respuesta=self.DB.Autos_dentro()
        self.scrolledtxt2.delete("1.0", tk.END)
        for fila in respuesta:
            self.scrolledtxt2.insert(tk.END, "Folio num: "+str(fila[0])+"\nEntro: "+str(fila[1])[:-3]+"\nPlacas: "+str(fila[2])+"\n\n")


    def desglose_cobrados(self):
        Numcorte=str(self.CortesAnteri.get(), )
        Numcorte=int(Numcorte)
        Numcorte=str(Numcorte)

        respuesta=self.DB.desglose_cobrados(Numcorte)
        self.scrolledtxt2.delete("1.0", tk.END)

        p.text("El Numero de corte es "+Numcorte+'\n')
        for fila in respuesta:
            self.scrolledtxt2.insert(tk.END, str(fila[0])+" Boletos con tarifa "+str(fila[1])+"\n"+"valor c/u $"+str(fila[2])+" Total $"+str(fila[3])+"\n\n")

            p.text(f"  {str(fila[0])}  -  {str(fila[1])}  -  ${str(fila[2])}   -  ${str(fila[3])}\n")

        p.cut()

    def BoletoCancelado(self):
        """
        Esta funcion cancela un boleto específico.

        Verifica si se ha ingresado un número de folio para cancelar y muestra una advertencia para confirmar la cancelacion.
        Si se confirma la cancelacion, obtiene los datos del boleto cancelado y realiza las operaciones correspondientes.
        Muestra informacion relevante del boleto cancelado y guarda el registro del cobro cancelado.

        :param self: Objeto de la clase que contiene los atributos y métodos necesarios.

        :return: None
        """

        if len(self.FolioCancelado.get()) == 0:
            mb.showerror("Error", "Ingrese un folio a cancelar")
            self.entryFOLIOCancelado.focus()
            return

        cancelar = mb.askokcancel("Advertencia", f"¿Estas seguro de querer cancelar el boleto con folio: {self.FolioCancelado.get()}?")

        if cancelar == False:
            self.FolioCancelado.set("")
            self.entryFOLIOCancelado.focus()
            return

        folio = self.FolioCancelado.get()
        self.folio.set(folio)

        folio = self.folio.get()
        respuesta = self.DB.consulta(folio)

        if len(respuesta) == 0:
            self.fecha_entrada.set('')
            self.fecha_salida.set('')
            mb.showinfo("Informacion", "No existe un auto con dicho codigo")
            return

        Salida = respuesta[0][1]
        Placas = respuesta[0][6]

        if Salida is not None:
            self.FolioCancelado.set("")
            self.folio.set("")
            mb.showerror("Error", "No se puede cancelar un boleto ya cobrado")
            return

        if Placas == "BoletoPerdido":
            mb.showerror("Error", "El folio ingresado corresponde a una reposicion de un boleto perdido, no se puede cancelar.")
            self.FolioCancelado.set("")
            self.folio.set("")
            return

        Entrada = str(respuesta[0][0])
        self.fecha_entrada.set(Entrada)

        self.CalculaPermanencia()

        importe = 0

        # Establecer el importe y mostrarlo
        self.mostrar_importe(importe)

        self.TarifaPreferente.set("CDO")

        self.GuardarCobro()

        self.Comprobante(titulo='Boleto Cancelado', imagen_logo=False)

        self.FolioCancelado.set("")

        self.limpiar_campos()

    def listar(self):
        respuesta=self.DB.recuperar_todos()
        self.scrolledtext1.delete("1.0", tk.END)
        for fila in respuesta:
            self.scrolledtext1.insert(tk.END, "Entrada num: "+str(fila[0])+"\nEntro: "+str(fila[1])[:-3]+"\nSalio: "+str(fila[2])[:-3]+"\n\n")

    def listar1(self):
        respuesta=self.DB.recuperar_sincobro()
        self.scrolledtext1.delete("1.0", tk.END)
        #respuesta=str(respuesta)
        for fila in respuesta:
            self.scrolledtext1.insert(tk.END, "Entrada num: "+str(fila[0])+"\nEntro: "+str(fila[1])[:-3]+"\nSalio: "+str(fila[2])[:-3]+"\nImporte: "+str(fila[3])+"\n\n")
            ###p = Usb(0x04b8, 0x0202, 0)
            #p = Usb(0x04b8, 0x0e15, 0)#esta es la impresora con sus valores que se obtienen con lsusb
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
        respuesta=self.DB.corte()
        self.ImporteCorte.set(respuesta)
        ##obtengamo la fechaFin del ultimo corte
        ultiCort1=str(self.DB.UltimoCorte())
        #mb.showinfo("msj uno",ultiCort1)
        startLoc = 20
        endLoc = 43
        ultiCort1=(ultiCort1)[startLoc: endLoc]
        ultiCort1 = ultiCort1.strip('),')
        if len(ultiCort1) <= 19:   

            ultiCort1= datetime.strptime(ultiCort1, '%Y, %m, %d, %H, %M')
        else:
            ultiCort1= datetime.strptime(ultiCort1, '%Y, %m, %d, %H, %M, %S')

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
        cajero=self.DB.CajeroenTurno()
        for fila in cajero:
            cajero1 = fila[0]
            nombre2 = fila[1]
            inicio1 = fila[2]
            turno1 = fila[3]
            usuario1 = fila[4]
        hoy = str(datetime.today())
        hoy1=hoy[:20]


        datos=(hoy1, cajero1)
        self.DB.Cierreusuario(datos)
        dato=(cajero1)
        self.DB.NoAplicausuario(dato)
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
        AEE=(self.DB.CuantosAutosdentro())
        maxnumid=str(self.DB.MaxfolioEntrada())
        maxnumid = "".join([x for x in maxnumid if x.isdigit()])#con esto solo obtenemos los numeros
        maxnumid=int(maxnumid)
        maxnumid=str(maxnumid)
        pasa = str(self.BDentro.get(),)
        NumBolQued = pasa.strip('(),')
        datos=(Im38, fechaInicio, fechaDECorte,AEE,maxnumid,NumBolQued)
        self.DB.GuarCorte(datos)
        maxnum1=str(self.DB.Maxfolio_Cortes())
        maxnum = "".join([x for x in maxnum1 if x.isdigit()])#con esto solo obtenemos los numeros
        maxnum=int(maxnum)
        maxnum=str(maxnum)
        vobo = "cor"#este es para que la instruccion no marque error
        ActEntradas = (maxnum, vobo )
        self.label4.configure(text=("Numero de corte",maxnum))

        p.image(logo_1)

        p.text(f" Est {nombre_estacionamiento} CORTE Num "+maxnum+"\n")
        p.text('IMPORTE: $ '+Im38+'\n')
        ultiCort1=str(self.FechUCORTE.get(),)
        DDESEM=(datetime.today().weekday())

        if DDESEM == 0:
            DDESEM = 'LUNES'
        if DDESEM == 1:
            DDESEM = 'MARTES'
        if DDESEM == 2:
            DDESEM = 'MIERCOLES'
        if DDESEM == 3:
            DDESEM = 'JUEVES'
        if DDESEM == 4:
            DDESEM = 'VIERNES'
        if DDESEM == 5:
            DDESEM = 'SABADO'
        if DDESEM == 6:
            DDESEM = 'DOMINGO'

        ultiCort4= datetime.strptime(ultiCort1, '%Y-%m-%d %H:%M:%S')
        ultiCort5 = datetime.strftime(ultiCort4, '%D a las %H:%M:%S')
        p.text('Inicio: ')
        p.text(str(DDESEM))
        p.text(' ')
        p.text(ultiCort5)
        p.text('\n')
        valorFEsteCorte = str(self.FechaCorte.get(),)
        fechaDECorte = datetime.strptime(valorFEsteCorte, '%Y-%m-%d %H:%M:%S' )
        fechaDECorte = datetime.strftime(fechaDECorte, '%D a las %H:%M:%S' )
        p.text('Final :')
        p.text(str(DDESEM))
        p.text(' ') 
        p.text(str(fechaDECorte))
        p.text('\n')
        MaxFolio=str(self.DB.MaxfolioEntrada())
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
        inicios = self.DB.IniciosdeTurno(dato)
        for fila in inicios:
            p.text("Sesion "+fila[1]+": "+str(fila[0])+"\n")
                                        
        BolCobrImpresion=str(self.BoletosCobrados.get(),)
        p.text("Boletos Cobrados: "+BolCobrImpresion+"\n")

        p.text('Boletos Expedidos: '+BEDespuesCorteImpre+'\n')
        BAnterioresImpr=str(self.BAnteriores.get(),)#######
        p.text("Boletos Turno Anterior: "+BAnterioresImpr+"\n")
        AEE1 = self.DB.CuantosAutosdentro()
        for fila in AEE1:
            AEE = fila[0]
        BDentroImp = (AEE + int(BEDespuesCorteImpre)) - int(BolCobrImpresion)

        p.text('Boletos Dejados: '+str(BDentroImp)+'\n')
        AutosEnEstacImpre = str(self.AutosEnEstacionamiento.get(),)
        p.text('------------------------------')
        p.text('\n')

        self.ImporteCorte.set("")

        self.DB.ActualizarEntradasConcorte(ActEntradas)
        vobo='ant'
        self.DB.NocobradosAnt(vobo)
        ponercorte =int(maxnum) 
        #mb.showinfo("primero",ponercorte)
        self.CortesAnteri.set(ponercorte)
        #self.desglose_cobrados()
        Numcorte=str(self.CortesAnteri.get(), )
        Numcorte=int(Numcorte)
        Numcorte=str(Numcorte)

        respuesta=self.DB.desglose_cobrados(Numcorte)
        self.scrolledtxt2.delete("1.0", tk.END)



        p.text("Cantidad e Importes "+'\n')
        p.text("Cantidad - Tarifa - valor C/U - Total "+'\n')
        for fila in respuesta:
            self.scrolledtxt2.insert(tk.END, str(fila[0])+" Boletos con tarifa "+str(fila[1])+"\n"+"valor c/u $"+str(fila[2])+" Total $"+str(fila[3])+"\n\n")

            p.text(f"  {str(fila[0])}  -  {str(fila[1])}  -  ${str(fila[2])}   -  ${str(fila[3])}\n")

        else:
            p.text("\n")
            p.text(f"{BolCobrImpresion} Boletos        Suma total ${Im38}\n\n")    

        p.text("----------------------------------\n")

        # Obtiene la cantidad de boletos perdidos generados
        Boletos_perdidos_generados = self.DB.Boletos_perdidos_generados()
        Boletos_perdidos_generados = Boletos_perdidos_generados[0][0]

        # Obtiene el desglose de los boletos perdidos generados
        Boletos_perdidos_generados_desglose = self.DB.Boletos_perdidos_generados_desglose()

        # Obtiene la cantidad de boletos perdidos cobrados
        Boletos_perdidos_cobrados = self.DB.Boletos_perdidos_cobrados(Numcorte)
        Boletos_perdidos_cobrados = Boletos_perdidos_cobrados[0][0]

        # Obtiene el desglose de los boletos perdidos cobrados
        Boletos_perdidos_cobrados_desglose = self.DB.Boletos_perdidos_cobrados_desglose(Numcorte)

        # Obtiene la cantidad de boletos perdidos no cobrados
        Boletos_perdidos_no_cobrados = self.DB.Boletos_perdidos_no_cobrados()
        Boletos_perdidos_no_cobrados = Boletos_perdidos_no_cobrados[0][0]

        # Si hay boletos perdidos generados, cobrados o no cobrados, se procede a imprimir el reporte
        if Boletos_perdidos_generados > 0 or Boletos_perdidos_cobrados > 0 or Boletos_perdidos_no_cobrados > 0:
            # Imprime el encabezado de la seccion de boletos perdidos
            p.text("BOLETOS PERDIDOS"+'\n\n')

            # Imprime la cantidad de boletos perdidos generados y su desglose
            p.text(f"Boletos perdidos generados: {Boletos_perdidos_generados + Boletos_perdidos_cobrados}" + '\n')
            for boleto in Boletos_perdidos_cobrados_desglose:
                p.text(f"Folio:{boleto[0]}\nFecha entrada:{boleto[1]}\n")
            for boleto in Boletos_perdidos_generados_desglose:
                p.text(f"Folio:{boleto[0]}\nFecha entrada:{boleto[1]}\n")

            # Imprime separador
            p.text("**********************************\n")

            # Imprime la cantidad de boletos perdidos cobrados y su desglose
            p.text(f"Boletos perdidos cobrados: {Boletos_perdidos_cobrados}" + '\n\n')
            for boleto in Boletos_perdidos_cobrados_desglose:
                p.text(f"Folio:{boleto[0]}\nFecha entrada:{boleto[1]}\nFecha salida:{boleto[2]}\n")
            p.text("**********************************\n")

            # Imprime la cantidad de boletos perdidos no cobrados y su desglose
            p.text(f"Boletos perdidos quedados: {Boletos_perdidos_no_cobrados}" + '\n\n')
            for boleto in Boletos_perdidos_generados_desglose:
                p.text(f"Folio:{boleto[0]}\nFecha entrada:{boleto[1]}\n")

            # Imprime separador
            p.text("----------------------------------\n")

        # Obtiene la cantidad e importes de las pensiones para el corte actual
        respuesta = self.DB.total_pensionados_corte(Numcorte)

        # Si hay pensionados en el corte, se procede a imprimir la seccion correspondiente
        if len(respuesta) > 0:
            p.text("Cantidad e Importes Pensiones" + '\n')
            p.text("Cuantos - Concepto - ImporteTotal " + '\n')
            for fila in respuesta:
                p.text(f"   {str(fila[0])}   -  {str(fila[1])}   -   ${str(fila[2])}\n")
            else:
                p.text("----------------------------------\n")

        # Imprime un separador final
        p.text("----------------------------------\n")

        # Corta el papel
        p.cut()
        p.close()

        # Cierra el programa al final del reporte
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
                    CorteMaxMin=self.DB.Cortes_MaxMin(datos)
                    for fila in CorteMaxMin:
                       UltFecha=fila[0]
                       IniFecha=fila[1]
                       FinFecha=fila[2]
                    #Obtenemos Primer y Ultimo Folio de Cortes del Mes que se solicita el reporte
                    datos=(IniFecha)
                    CorteIni=self.DB.Cortes_Folio(datos)
                    datos=(UltFecha)
                    #CorteFin=self.DB.Cortes_FolioFin(datos)
                    CorteFin=self.DB.Cortes_Folio(datos)
                    #Obtnemos los Registros entre estos dos Folios para el cuerpo del reporte
                    datos=(CorteIni, CorteFin)
                    #datos=(IniFecha, UltFecha)
                    Registros=self.DB.Registros_corte(datos)
                    TotalesCorte=self.DB.Totales_corte(datos)
                    ResumenPromo=self.DB.Resumen_promo(datos)
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
        
        CuantosBoletosCobro=str(self.DB.CuantosBoletosCobro())
        CuantosBoletosCobro = CuantosBoletosCobro.strip('(),')
        self.BoletosCobrados.set(CuantosBoletosCobro)
        BEDCorte=str(self.DB.BEDCorte())
        BEDCorte = BEDCorte.strip('(),')
        self.BEDespuesCorte.set(BEDCorte)
        BAnteriores=str(self.DB.BAnteriores())
        BAnteriores = BAnteriores.strip('(),')
        self.BAnteriores.set(BAnteriores)
        MaxFolioCorte=str(self.DB.Maxfolio_Cortes())
        MaxFolioCorte=MaxFolioCorte.strip('(),')
        QuedadosBol=str(self.DB.Quedados_Sensor(MaxFolioCorte))
        QuedadosBol=QuedadosBol.strip('(),')
        self.BAnteriores.set(QuedadosBol)
        maxNumidIni=str(self.DB.MaxnumId())
        maxNumidIni = "".join([x for x in maxNumidIni if x.isdigit()])#con esto solo obtenemos los numeros
        maxNumidIni=int(maxNumidIni)
        maxFolioEntradas= str(self.DB.MaxfolioEntrada())
        maxFolioEntradas = "".join([x for x in maxFolioEntradas if x.isdigit()])#con esto solo obtenemos los numero
        maxFolioEntradas=int(maxFolioEntradas)
        BEDCorte=maxFolioEntradas-maxNumidIni
        BEDCorte=str(BEDCorte)
        self.BEDespuesCorte.set(BEDCorte)
        CuantosAutosdentro=str(self.DB.CuantosAutosdentro())
        MaxFolioCorte=str(self.DB.Maxfolio_Cortes())
        MaxFolioCorte=MaxFolioCorte.strip('(),')
        dentroCorte=str(self.DB.Quedados_Sensor(MaxFolioCorte))
        CuantosAutosdentro = CuantosAutosdentro.strip('(),')
        dentroCorte = dentroCorte.strip('(),')
        self.BDentro.set(CuantosAutosdentro)
        self.Autos_Anteriores.set(dentroCorte)
        #AutosAnteriores = int(self.Autos_Anteriores.get(),)
        #Cuantos_hay_dentro = ((AutosAnteriores + EntradasSen) - SalidasSen)
        #self.AutosEnEstacionamiento.set(Cuantos_hay_entro)

    ###################### Fin de Pagina2 Inicio Pagina3 ###############################
    def interface_pensionados(self):
        self.registros = None
        self.tipo_pago_ = None

        self.pagina4 = ttk.Frame(self.cuaderno1)
        self.cuaderno1.add(self.pagina4, text="Modulo Pensionados")
        #enmarca los controles LabelFrame 
        labelframe_pensionados = tk.LabelFrame(self.pagina4, text="Pensionados")
        labelframe_pensionados.grid(column=0, row=0, padx=5, pady=5, sticky=tk.NW)

        label_frame_datos_pago = tk.Frame(labelframe_pensionados)
        label_frame_datos_pago.grid(column=0, row=0, padx=5, pady=5, sticky=tk.NW)

        ######Pago, Vigencia y Numero de tarjeta
        labelframe_pensionados_datos_pago=tk.LabelFrame(label_frame_datos_pago, text="Datos de pago")
        labelframe_pensionados_datos_pago.grid(column=0, row=0, padx=5, sticky=tk.NW)

        labelframe_pensionados_datos_pago__=tk.Frame(labelframe_pensionados_datos_pago)
        labelframe_pensionados_datos_pago__.grid(column=0, row=0)

        lbldatos20=ttk.Label(labelframe_pensionados_datos_pago__, text="Num. Tarjeta:")
        lbldatos20.grid(column=0, row=0, padx=4, pady=4)
        self.variable_numero_tarjeta=tk.StringVar()
        self.caja_texto_numero_tarjeta=ttk.Entry(labelframe_pensionados_datos_pago__, width=15, textvariable=self.variable_numero_tarjeta)
        self.caja_texto_numero_tarjeta.grid(column=1, row=0, padx=4, pady=4)

        boton_consultar_pensionado=tk.Button(labelframe_pensionados_datos_pago__, text="Consultar", command=self.ConsulPagoPen, width=12, height=1, anchor="center",  font=("Arial", 10), background="red")
        boton_consultar_pensionado.grid(column=4, row=0, padx=4, pady=4)     

        lbldatos16=ttk.Label(labelframe_pensionados_datos_pago__, text="Monto Mensual:")#informativo
        lbldatos16.grid(column=0, row=1, padx=4, pady=4)
        self.Monto=tk.StringVar()
        entryMonto=ttk.Entry(labelframe_pensionados_datos_pago__, width=10, textvariable=self.Monto, state="readonly")
        entryMonto.grid(column=1, row=1)

        etiqueta_vigencia=ttk.Label(labelframe_pensionados_datos_pago__, text="Vigencia:")
        etiqueta_vigencia.grid(column=3, row=1, padx=4, pady=4)
        self.Vigencia=tk.StringVar()
        cata_texto_vigencia=ttk.Entry(labelframe_pensionados_datos_pago__, width=15, textvariable=self.Vigencia, state="readonly")
        cata_texto_vigencia.grid(column=4, row=1, padx=4, pady=4)

        lbldatos17=ttk.Label(labelframe_pensionados_datos_pago__, text="Mensualidades a Pagar:")
        lbldatos17.grid(column=0, row=2, padx=4, pady=4)

        self.meses_pago = tk.StringVar()
        self.comboMensual = ttk.Combobox(labelframe_pensionados_datos_pago__, width=8, state="readonly", textvariable=self.meses_pago)
        self.comboMensual["values"] = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
        self.comboMensual.current(0)
        self.comboMensual.grid(column=1, row=2, padx=4, pady=4)

        etiqueta_estatus=ttk.Label(labelframe_pensionados_datos_pago__, text="Estatus:")
        etiqueta_estatus.grid(column=3, row=2, padx=4, pady=4)  
        self.Estatus=tk.StringVar()
        cata_texto_estatus=ttk.Entry(labelframe_pensionados_datos_pago__, width=15, textvariable=self.Estatus, state="readonly")
        cata_texto_estatus.grid(column=4, row=2, padx=4, pady=4)

        label_frame_informacion = tk.Frame(labelframe_pensionados_datos_pago)
        label_frame_informacion.grid(column=0, row=2)

        self.etiqueta_informacion = ttk.Label(label_frame_informacion, text="", font=("Arial", 11))
        self.etiqueta_informacion.grid(column=0, row=0)



        label_frame_tipo_pago = tk.LabelFrame(label_frame_datos_pago, text="Tipo de pago")
        label_frame_tipo_pago.grid(column=1, row=0, padx=6, pady=5, sticky=tk.NW)

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


        boton2=tk.Button(label_frame_tipo_pago, text="Cobrar Pension", command=self.Cobro_Pensionado, width=12, height=1, anchor="center",  font=("Arial", 10), background="red")
        boton2.grid(column=0, row=3, padx=4, pady=4)

        self.etiqueta_informacion_pago = ttk.Label(label_frame_tipo_pago, text="", font=("Arial", 11))
        self.etiqueta_informacion_pago.grid(column=0, row=4)    



        labelframe_pensionados_acciones = tk.LabelFrame(labelframe_pensionados, text="Acciones")
        labelframe_pensionados_acciones.grid(column=1, row=0, padx=5, pady=5, sticky=tk.NW)

        self.boton_agregar_pensionado=tk.Button(labelframe_pensionados_acciones, text="Agregar Pensionado", anchor="center", font=("Arial", 12), width=27, command=self.agregar_pensionado)
        self.boton_agregar_pensionado.grid(column=0, row=0, padx=5, pady=5, sticky=tk.NW)
     
        self.boton_modificar_pensionado=tk.Button(labelframe_pensionados_acciones, text="Modificar info Pensionado", anchor="center", command=self.modificar_pensionado, font=("Arial", 12), width=27)
        self.boton_modificar_pensionado.grid(column=0, row=1, padx=5, pady=5, sticky=tk.NW)

        labelframe_pensionados_acciones_contraseña = ttk.Frame(labelframe_pensionados_acciones)
        labelframe_pensionados_acciones_contraseña.grid(column=0, row=2)

        lbldatos21=ttk.Label(labelframe_pensionados_acciones_contraseña, text="Contraseña", font=("Arial", 10))
        lbldatos21.grid(column=0, row=0, padx=4, pady=4)

        self.variable_contraseña_pensionados=tk.StringVar()
        self.campo_texto_contraseña_pensionados=ttk.Entry(labelframe_pensionados_acciones_contraseña, width=20, textvariable=self.variable_contraseña_pensionados, show="*", font=("Arial", 10))
        self.campo_texto_contraseña_pensionados.grid(column=1, row=0, padx=4, pady=4)

       


        ######Muestra de Pensionados Adentro
        labelframe_pensionados_dentro = tk.LabelFrame(labelframe_pensionados, text="Pensionados Adentro")
        labelframe_pensionados_dentro.grid(column=1, row=1, padx=5, pady=5)

        self.lbldatosTotPen=ttk.Label(labelframe_pensionados_dentro, text="")
        self.lbldatosTotPen.grid(column=0, row=0, padx=4, pady=4)        

        boton5=tk.Button(labelframe_pensionados_dentro, text="Actualizar", command=self.PenAdentro, width=28, height=1, anchor="center", font=("Arial", 10), background="red")
        boton5.grid(column=0, row=1, padx=4, pady=4)

        self.scroll_pensionados_dentro = st.ScrolledText(labelframe_pensionados_dentro, width=28, height=18)
        self.scroll_pensionados_dentro.grid(column=0,row=2, padx=10, pady=10)




        #Tabla de Pensionados
        labelframe_pensionados.columnconfigure(0, weight=1)
        labelframe_pensionados.rowconfigure(1, weight=1)

        labelframe_tabla_pensionados = tk.LabelFrame(labelframe_pensionados, text="Tabla pensionados")
        labelframe_tabla_pensionados.grid(column=0, row=1, padx=5, pady=5, sticky='NSEW')

        labelframe_tabla_pensionados.columnconfigure(0, weight=1)
        labelframe_tabla_pensionados.rowconfigure(0, weight=1)

        # Obtiene los nombres de las columnas de la tabla que se va a mostrar
        columnas = ['N° de tarjeta', 'Cortesia', 'Nombre', 'Estado', 'Vigencia', 'Tolerancia', 'ID', 'Estatus']

        # Crea un Treeview con una columna por cada campo de la tabla
        self.tabla = ttk.Treeview(labelframe_tabla_pensionados, columns=columnas)
        self.tabla.config(height=8)
        self.tabla.grid(row=0, column=0, sticky='NSEW', padx=5, pady=5)

        # Define los encabezados de columna
        i = 1
        for headd in columnas:
            self.tabla.heading(f'#{i}', text=headd)
            self.tabla.column(f'#{i}', stretch=True)
            i += 1

        self.tabla.column('#0', width=0, stretch=False)
        self.tabla.column('#1', width=85, stretch=False)
        self.tabla.column('#2', width=60, stretch=False)
        self.tabla.column('#3', width=70, stretch=False)
        self.tabla.column('#4', width=70, stretch=False)
        self.tabla.column('#5', width=120, stretch=False)
        self.tabla.column('#6', width=75, stretch=False)
        self.tabla.column('#7', width=0, stretch=False)
        self.tabla.column('#8', width=100, stretch=False)

        # Crea un Scrollbar vertical y lo asocia con el Treeview
        scrollbar_Y = ttk.Scrollbar(labelframe_tabla_pensionados, orient='vertical', command=self.tabla.yview)
        self.tabla.configure(yscroll=scrollbar_Y.set)
        scrollbar_Y.grid(row=0, column=1, sticky='NS')

        # Crea un Scrollbar horizontal y lo asocia con el Treeview
        scrollbar_X = ttk.Scrollbar(labelframe_tabla_pensionados, orient='horizontal', command=self.tabla.xview)
        self.tabla.configure(xscroll=scrollbar_X.set)
        scrollbar_X.grid(row=1, column=0, sticky='EW')

        # Empaqueta el Treeview en el labelframe
        self.tabla.grid(row=0, column=0, sticky='NSEW', padx=5, pady=5)

        self.tarjetas_expiradas()
        self.ver_pensionados()
        self.PenAdentro()


    
    def ConsulPagoPen(self):
        """Consulta la informacion de un pensionado y muestra los detalles del pago.
        
        Obtiene la informacion del pensionado asociado al número de tarjeta ingresado,
        calcula el monto a pagar y muestra los detalles del pago en la interfaz gráfica.

        Returns:
            None
        """
        numtarjeta = self.variable_numero_tarjeta.get()

        if not numtarjeta:
            mb.showwarning("IMPORTANTE", "Debe Leer el Numero de Tarjeta")
            self.limpiar_datos_pago()
            return

        numtarjeta = int(numtarjeta)
        resultado = self.DB.ValidarID(numtarjeta)

        if not resultado:
            mb.showwarning("IMPORTANTE", "No existe Cliente para ese Num de Tarjeta")
            self.limpiar_datos_pago()
            return

        respuesta = self.DB.ConsultaPensionado(resultado)

        if not respuesta:
            mb.showwarning("IMPORTANTE", "No se encontro informacion para el cliente")
            return

        cliente = respuesta[0]
        VigAct = cliente[12]
        Estatus = cliente[14]
        monto = cliente[15]
        cortesia = cliente[16]
        tolerancia = int(cliente[17])

        self.Monto.set(monto)
        self.Vigencia.set(VigAct)
        self.Estatus.set(Estatus)
        pago = 0
        nummes = int(self.meses_pago.get())

        self.etiqueta_informacion.configure(text="")
        if cortesia == "Si":
            self.etiqueta_informacion.configure(text="El Pensionado cuenta con Cortesía")

        # Logica para determinar el pago según el estatus del pensionado
        # y mostrar mensajes informativos
        if Estatus == "Inactiva":
            # Cálculo del pago con penalizacion para estatus Inactiva
            pago = self.calcular_pago_media_pension(monto)
            total = pago + valor_tarjeta
            self.etiqueta_informacion.configure(text="Tarjeta desactivada")
            mb.showwarning("IMPORTANTE", f"La tarjeta esta desactivada, por lo que el pensionado solo pagará los dias faltantes del mes junto al precio de la tarjeta, posteriormente solo pagará el valor registrado de la pension.\n\nPago pension: {pago}\nPago tarjeta:    {valor_tarjeta}\nPago total:        {total}")
            pago = total

        elif Estatus == "InactivaPerm":
            # Cálculo del pago con penalizacion para estatus InactivaPerm
            pago_mensualidad = monto * nummes
            total = pago_mensualidad + valor_tarjeta

            self.etiqueta_informacion.configure(text="Tarjeta desactivada de forma permanente")
            mb.showwarning("IMPORTANTE", f"La tarjeta esta desactivada de forma permanente, por lo que el pensionado pagará una penalizacion correspondiente al precio de la tarjeta ademas de su respectiva mensualidad.\n\nPago pension: {pago_mensualidad}\nPenalizacion:    {valor_tarjeta}\nPago total:        {total}")
            pago = total

        elif Estatus == "InactivaTemp":
            pago_mensualidad = monto * nummes

            self.etiqueta_informacion.configure(text="Tarjeta desactivada de forma temporal")
            mb.showwarning("IMPORTANTE", f"La tarjeta esta desactivada de forma temporal, por lo que el pensionado solo pagará su respectiva mensualidad.")
            pago = pago_mensualidad

        elif Estatus == "Reposicion":
            self.etiqueta_informacion.configure(text="Tarjeta de reposicion")
            mb.showwarning("IMPORTANTE", "La tarjeta es de reposicion por lo que el pensionado solo pagará dicho valor")
            pago = valor_reposiion_tarjeta

        elif VigAct != None:

            # Obtener la fecha y hora actual en formato deseado
            VigAct = VigAct.strftime("%Y-%m-%d %H:%M:%S")
            # Convertir la cadena de caracteres en un objeto datetime
            VigAct = datetime.strptime(VigAct, "%Y-%m-%d %H:%M:%S")

            # Obtener la fecha y hora actual en formato deseado
            hoy = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
            # Convertir la cadena de caracteres en un objeto datetime
            hoy = datetime.strptime(hoy, "%Y-%m-%d %H:%M:%S")

            limite = VigAct + timedelta(days=tolerancia)
            print(f"limite: {limite}")

            penalizacion_pension = 0

            if hoy > limite:
                penalizacion_pension, dias_atrasados = self.calcular_penalizacion_diaria(
                    penalizacion_diaria=penalizacion_diaria_pension,
                    fecha_limite=limite)

                mb.showwarning("IMPORTANTE", f"Vigencia Vencida por {dias_atrasados} días, se aplicará una penalizacion de ${penalizacion_pension}.00 sumado a su pago de pension.")
                self.caja_texto_numero_tarjeta.focus()

            pago = (monto * nummes) + penalizacion_pension

        self.etiqueta_informacion_pago.configure(text=f"${pago}.00")



    def Cobro_Pensionado(self):
        """Realiza el cobro de la pension al pensionado y actualiza su informacion en la base de datos.

        Realiza el cobro correspondiente a la pension del pensionado según su estado,
        tipo de pension y forma de pago seleccionada. Actualiza la informacion del pensionado
        en la base de datos con los nuevos datos de vigencia y estatus. Además, imprime un comprobante
        de pago y muestra mensajes informativos.

        Raises:
            TypeError: Si no se ha seleccionado una forma de pago.
        """
        numtarjeta = str(self.variable_numero_tarjeta.get())
        nummes = int(self.meses_pago.get())

        try:
            usuario = self.DB.nombre_usuario_activo()
            usuario = str(usuario[0][0])
            # usuario = "prueba"

            # Verificar que se ha seleccionado una forma de pago
            if not self.variable_tipo_pago_transferencia.get() and not self.variable_tipo_pago_efectivo.get():
                raise TypeError("Selecciona una forma de pago")

            if not numtarjeta:
                mb.showwarning("IMPORTANTE", "Debe Leer el Numero de Tarjeta")
                self.caja_texto_numero_tarjeta.focus()
                return

            tarjeta = int(numtarjeta)
            Existe = self.DB.ValidarID(tarjeta)

            if not Existe:
                mb.showwarning("IMPORTANTE", "No existe Cliente para ese Num de Tarjeta")
                self.caja_texto_numero_tarjeta.focus()
                return

            respuesta = self.DB.ConsultaPensionado(Existe)

            if not respuesta:
                mb.showwarning("IMPORTANTE", "No se encontro informacion para el cliente")
                return

            cliente = respuesta[0]
            Nom_cliente = cliente[0]
            Apell1_cliente = cliente[1]
            Apell2_cliente = cliente[2]
            VigAct = cliente[12]
            Estatus = cliente[14]
            monto = cliente[15]
            cortesia = cliente[16]
            Tolerancia = int(cliente[17])

            fechaPago = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if Estatus == "Inactiva":
                pago = self.calcular_pago_media_pension(monto)
                total = pago + valor_tarjeta
                pago = total

            elif Estatus == "InactivaPerm":
                pago = monto * nummes
                total = pago + valor_tarjeta
                pago = total

            elif Estatus == "InactivaTemp":
                pago_mensualidad = monto * nummes
                pago = pago_mensualidad

            elif Estatus == "Reposicion":pago = valor_reposiion_tarjeta

            elif VigAct != None:

                # Obtener la fecha y hora actual en formato deseado
                VigAct = VigAct.strftime("%Y-%m-%d %H:%M:%S")
                # Convertir la cadena de caracteres en un objeto datetime
                VigAct = datetime.strptime(VigAct, "%Y-%m-%d %H:%M:%S")

                # Obtener la fecha y hora actual en formato deseado
                hoy = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
                # Convertir la cadena de caracteres en un objeto datetime
                hoy = datetime.strptime(hoy, "%Y-%m-%d %H:%M:%S")

                limite = VigAct + timedelta(days=Tolerancia)
                print(limite)

                penalizacion_pension = 0

                if hoy > limite:
                    penalizacion_pension, dias_atrasados = self.calcular_penalizacion_diaria(
                        penalizacion_diaria=penalizacion_diaria_pension,
                        fecha_limite=limite)

                pago = (monto * nummes) + penalizacion_pension

            if cortesia == "Si":NvaVigencia = self.nueva_vigencia(
                    fecha= VigAct,
                    cortesia="Si")
            else:NvaVigencia = self.nueva_vigencia(
                    fecha= VigAct,
                    meses=nummes)

            datos = (Existe, tarjeta, fechaPago, NvaVigencia, nummes, pago, self.tipo_pago_)
            datos1 = ("Activo", NvaVigencia, Existe)

            self.DB.CobrosPensionado(datos)
            self.DB.UpdPensionado(datos1)

            self.imprimir_comprobante_pago_pensionado(
                numero_tarjeta=tarjeta,
                Nom_cliente=Nom_cliente,
                Apell1_cliente=Apell1_cliente,
                Apell2_cliente=Apell2_cliente,
                fecha_pago=fechaPago,
                vigencia=NvaVigencia[:10],
                monto=pago,
                usuario=usuario,
                tipo_pago=self.tipo_pago_
            )

            mb.showinfo("IMPORTANTE", "PAGO realizado con éxito")
            self.limpiar_datos_pago()

        except TypeError as e:
            print(e)
            traceback.print_exc()
            mb.showwarning("Error", e)

        except Exception as e:
            print(e)
            traceback.print_exc()
            mb.showwarning("Error", e)


    def PenAdentro(self):
        """Muestra en la interfaz gráfica la lista de pensionados que están adentro.

        Obtiene la lista de pensionados que están dentro del lugar y muestra sus nombres
        y detalles en un ScrolledText en la interfaz gráfica.
        """
        self.scroll_pensionados_dentro.configure(state="normal")
        respuesta=self.DB.TreaPenAdentro()
        self.scroll_pensionados_dentro.delete("1.0", tk.END)
        cont=0
        for fila in respuesta:
            self.scroll_pensionados_dentro.insert(tk.END,
            f"{cont+1}) {fila[0]}: \n   {fila[1]} {fila[2]}\n   {fila[3]} - {fila[4]}\n\n")
            cont=cont+1
        self.lbldatosTotPen.configure(text="PENSIONADOS ADENTRO: "+str(cont))
        self.scroll_pensionados_dentro.configure(state="disabled")

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
        """Imprime un comprobante de pago de una pension.
        Args:
            numero_tarjeta (str): El número de tarjeta del pensionado.
            Nom_cliente (str): El nombre del pensionado.
            Apell1_cliente (str): El primer apellido del pensionado.
            Apell2_cliente (str): El segundo apellido del pensionado.
            fecha_pago (str): La fecha en que se hizo el pago.
            vigencia (str): La fecha de vigencia de la pension.
            monto (float): El monto que se pago.
            usuario (str): Nombre del usuario en turno.
            tipo_pago (str): Tipo de pago.
        Returns:
            None: Esta funcion no devuelve nada, simplemente imprime un comprobante.
        Raises:
            None
        """
        # Establece la alineacion del texto al centro
        p.set(align="center")

        p.text("----------------------------------\n")
        # Agrega un encabezado al comprobante
        p.text("        Comprobante de pago\n\n")
        
        # Establece la alineacion del texto a la izquierda
        p.set(align="left")

        # Agrega informacion sobre el pago al comprobante
        p.image(logo_1)
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

        # Corta el papel para finalizar la impresion
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

    def nueva_vigencia(self, fecha, meses = 1, cortesia = None):
        """
        Obtiene la fecha del último día del mes siguiente a la fecha dada y la devuelve como una cadena de texto en el formato '%Y-%m-%d %H:%M:%S'.

        :param fecha (str or datetime): Fecha a partir de la cual se obtendrá la fecha del último día del mes siguiente.

        :raises: TypeError si la fecha no es una cadena de texto ni un objeto datetime.

        :return:
            - nueva_vigencia (str): Una cadena de texto en el formato '%Y-%m-%d %H:%M:%S' que representa la fecha del último día del mes siguiente a la fecha dada.
        """
        try:
            nueva_vigencia = ''
            if fecha == None:
                # Obtener la fecha y hora actual en formato deseado
                fecha = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

                # fecha = "2023-04-30 23:59:59"

                # Convertir la cadena de caracteres en un objeto datetime
                fecha = datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S")

                fecha = fecha - relativedelta(months=1)

            # Verificar que la fecha sea de tipo str o datetime
            elif not isinstance(fecha, (str, datetime)):
                raise TypeError("La fecha debe ser una cadena de texto o un objeto datetime.")

            # Convertir la fecha dada en un objeto datetime si es de tipo str
            elif isinstance(fecha, str):
                fecha = datetime.strptime(fecha, '%Y-%m-%d 23:59:59')

            if cortesia == "Si":
                nueva_vigencia = fecha + relativedelta(years=1)

            else:
                # Obtener la fecha del primer día del siguiente mes
                mes_siguiente = fecha + relativedelta(months=meses, day=1)
                
                # Obtener la fecha del último día del mes siguiente
                ultimo_dia_mes_siguiente = mes_siguiente + relativedelta(day=31)
                if ultimo_dia_mes_siguiente.month != mes_siguiente.month:
                    ultimo_dia_mes_siguiente -= relativedelta(days=1)

                nueva_vigencia = ultimo_dia_mes_siguiente

            # convertir la fecha en formato de cadena
            nueva_vigencia = nueva_vigencia.strftime('%Y-%m-%d 23:59:59')

            # Devolver el valor
            return nueva_vigencia
        
        except TypeError as e:
            print(e)
            traceback.print_exc()
            mb.showwarning("Error", f"{e}")
        except Exception as e:
            print(e)
            traceback.print_exc()
            mb.showwarning("Error", f"{e}")

    def BoletoDañado(self):
        """
        Esta funcion se encarga de manejar el cobro de un boleto dañado.

        Verifica si se ha ingresado un número de folio para el boleto dañado y realiza las operaciones correspondientes.
        Muestra informacion relevante del boleto dañado y establece el tipo de pago como "Danado".

        :param self: Objeto de la clase que contiene los atributos y métodos necesarios.

        :return: None
        """

        datos = self.PonerFOLIO.get()
        self.folio.set(str(datos))
        datos = self.folio.get()
        self.folio_auxiliar = datos

        if len(datos) == 0:
            mb.showinfo("Error", "Ingrese el folio del boleto dañado")
            self.limpiar_campos()
            self.entryPonerFOLIO.focus()
            return

        respuesta = self.DB.consulta(datos)
        if len(respuesta) == 0:
            self.limpiar_campos()
            mb.showinfo("Informacion", "No existe un auto con dicho codigo")
            self.entryPonerFOLIO.focus()
            return

        if respuesta[0][6] == "BoletoPerdido":
            mb.showerror("Error", "No se puede cobrar como Danado un boleto perdido")
            self.limpiar_campos()
            self.entryPonerFOLIO.focus()
            return

        self.fecha_entrada.set(respuesta[0][0])
        self.fecha_salida.set(respuesta[0][1])
        self.CalculaPermanencia()
        self.TarifaPreferente.set("Danado")
        self.PonerFOLIO.set('')





    def desactivar(self):
        """Desactiva los botones de la interface"""
        self.ventana1.withdraw()  # oculta la ventana

    def activar(self):
        """ Activa los botones de la interface  """
        self.ventana1.deiconify()



    def desactivar_botones(self):
        """Esta funcion deshabilita los botones que permiten agregar y modificar pensionados en la interfaz gráfica."""
        self.boton_agregar_pensionado.configure(state='disabled')
        self.boton_modificar_pensionado.configure(state='disabled')


    def activar_botones(self):
        """Esta funcion habilita los botones que permiten agregar y modificar pensionados en la interfaz gráfica."""
        self.boton_agregar_pensionado.configure(state='normal')
        self.boton_modificar_pensionado.configure(state='normal')


    def limpiar_campos(self):
        """Limpia los campos y reinicia los valores de los atributos relacionados con la interfaz gráfica.

        Esta funcion reinicia los valores de varios atributos de la interfaz gráfica a su estado inicial,
        lo que implica limpiar campos de entrada de texto y etiquetas, y establecer valores por defecto en algunos atributos.
        """
        # Reinicia los valores de varios atributos
        self.folio.set("")
        self.Placa.set("")
        self.fecha_entrada.set("")
        self.fecha_salida.set("")
        self.copia_fecha_salida.set("")
        self.importe.set("")
        self.TiempoTotal.set("")
        self.TiempoTotal_auxiliar.set("")
        self.promo.set("")
        self.promo_auxiliar.set('')
        self.PonerFOLIO.set("")
        self.label15.configure(text="")
        self.TarifaPreferente.set("")
        self.IImporte.config(text="")
        self.folio_auxiliar = None
        self.entryfolio.focus()
        self.BoletoDentro()
        self.BoletoDentro2()


    def vaciar_tabla(self):
        """Vacía la tabla de datos.

        Esta funcion elimina todas las filas de la tabla que muestra los datos de pensionados en la interfaz gráfica.
        """
        # Elimina todas las filas de la tabla
        self.tabla.delete(*self.tabla.get_children())

    def llenar_tabla(self, registros):
        """
        Llena la tabla con los registros que cumplen con los criterios de búsqueda.

        :param registros: (list) Una lista de tuplas que representan los registros obtenidos de la base de datos.

        :raises None:

        :return: None
        """
        # Limpia la tabla antes de llenarla con nuevos registros
        self.vaciar_tabla()

        if self.registros:
            for registro in registros:
                # Pasa los valores del registro como tupla
                self.tabla.insert('', 'end', values=registro)


    def ver_pensionados(self):
        """
        Obtiene y muestra todos los pensionados en la tabla.

        Esta funcion obtiene todos los registros de pensionados desde la base de datos y luego los muestra
        en la tabla de la interfaz gráfica.
        """
        self.registros = self.controlador_crud_pensionados.ver_pensionados()
        self.llenar_tabla(self.registros)


    def eliminar_pensionado(self):
        """Elimina el pensionado seleccionado."""
        pass

    def agregar_pensionado(self):
        """
        Abre la ventana para agregar un nuevo pensionado.

        Esta funcion desactiva los botones, verifica la contraseña, y luego abre la ventana para agregar un nuevo pensionado.
        """
        self.desactivar_botones()
        contraseña = self.variable_contraseña_pensionados.get()

        if len(contraseña) == 0:
            mb.showwarning("Error", "Ingrese la contraseña para agregar un pensionado")
            self.variable_contraseña_pensionados.set("")
            self.campo_texto_contraseña_pensionados.focus()
            self.activar_botones()
            return

        if contraseña != contraseña_pensionados:
            mb.showwarning("Error", "Contraseña incorrecta")
            self.variable_contraseña_pensionados.set("")
            self.campo_texto_contraseña_pensionados.focus()
            self.activar_botones()
            return

        self.variable_contraseña_pensionados.set("")
        self.variable_numero_tarjeta.set("")
        View_agregar_pensionados()

        self.limpiar_datos_pago()
        self.ver_pensionados()
        self.activar_botones()


    def modificar_pensionado(self):
        """
        Abre la ventana para modificar los datos de un pensionado existente.

        Esta funcion desactiva los botones, verifica la contraseña y el número de tarjeta del pensionado,
        y luego abre la ventana para modificar los datos del pensionado existente.
        """
        self.desactivar_botones()
        contraseña = self.variable_contraseña_pensionados.get()
        numero_tarjeta = self.variable_numero_tarjeta.get()

        if len(numero_tarjeta) == 0:
            mb.showwarning("Error", "Ingrese el número de tarjeta del pensionado a modificar")
            self.variable_numero_tarjeta.set("")
            self.caja_texto_numero_tarjeta.focus()
            self.activar_botones()
            return

        if len(contraseña) == 0:
            mb.showwarning("Error", "Ingrese la contraseña para agregar un pensionado")
            self.variable_contraseña_pensionados.set("")
            self.campo_texto_contraseña_pensionados.focus()
            self.activar_botones()
            return

        if contraseña != contraseña_pensionados:
            mb.showwarning("Error", "Contraseña incorrecta")
            self.variable_contraseña_pensionados.set("")
            self.campo_texto_contraseña_pensionados.focus()
            self.activar_botones()
            return

        resultado = self.controlador_crud_pensionados.consultar_pensionado(numero_tarjeta)

        if len(resultado) == 0:
            mb.showerror("Error", "No está registrado un pensionado con dicho número de tarjeta")
            self.variable_numero_tarjeta.set("")
            self.limpiar_datos_pago()
            self.activar_botones()
            return

        self.variable_contraseña_pensionados.set("")
        self.variable_numero_tarjeta.set("")
        View_modificar_pensionados(datos_pensionado = resultado)
        self.limpiar_datos_pago()
        self.ver_pensionados()
        self.activar_botones()


    def limpiar_datos_pago(self):
        """
        Limpia y reinicia los datos relacionados con el pago de pensiones en la interfaz gráfica.

        Esta funcion reinicia los valores y la informacion mostrada en la interfaz gráfica
        relacionados con el pago de pensiones.
        """
        self.etiqueta_informacion.configure(text="")
        self.etiqueta_informacion_pago.configure(text="")
        self.variable_numero_tarjeta.set("")
        self.variable_contraseña_pensionados.set("")
        self.caja_texto_numero_tarjeta.focus()
        self.Monto.set("")
        self.comboMensual.current(0)
        self.Vigencia.set("")
        self.Estatus.set("")
        self.vaciar_tipo_pago()
        self.ver_pensionados()


    def calcular_pago_media_pension(self, monto):
        """
        Calcula el pago de media pension para un pensionado según el monto de la pension.

        :param monto: (float) Monto de la pension.

        :return: (int) El pago de media pension.
        """
        mes_actual = date.today().month
        año_actual = date.today().year

        ultimo_dia_mes = date(año_actual, mes_actual, 1) + relativedelta(day=31)
        dias_mes = ultimo_dia_mes.day

        dias_faltantes = dias_mes - date.today().day
        pago = math.ceil((monto / dias_mes) * dias_faltantes)

        return pago


    def calcular_penalizacion_diaria(self, penalizacion_diaria, fecha_limite):
        """
        Calcula la penalizacion diaria basada en la diferencia de días entre la fecha límite y la fecha actual.

        :param penalizacion_diaria: (float) La cantidad de penalizacion por cada día de atraso.
        :param fecha_limite: (str or datetime) La fecha límite en formato "%Y-%m-%d %H:%M:%S".

        :return: (tuple) Una tupla que contiene la penalizacion total a pagar por los días de atraso y el número de días atrasados.
        """

        # Obtener la fecha y hora actual en formato deseado
        hoy = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # hoy = '2023-07-30 11:59:59' 
        hoy = datetime.strptime(hoy, "%Y-%m-%d %H:%M:%S")

        # Convertir la fecha límite en un objeto datetime si es de tipo str
        if isinstance(fecha_limite, str):
            fecha_limite = datetime.strptime(fecha_limite, "%Y-%m-%d %H:%M:%S")

        # Calcular la cantidad de días de atraso
        fecha_atrasada = hoy - fecha_limite

        # print(f"fecha atrasada: {fecha_atrasada}")

        dias_atrasados = fecha_atrasada.days + 1  # Se suma 1 día para corregir fecha
        #if dias_atrasados == 0:dias_atrasados = 1

        # Calcular la penalizacion total
        penalizacion = dias_atrasados * penalizacion_diaria

        return penalizacion, dias_atrasados


    def tarjetas_expiradas(self):
        """
        Muestra las tarjetas vencidas en una ventana aparte.

        Esta funcion obtiene las tarjetas vencidas desde la base de datos, las muestra en una ventana aparte
        y luego desactiva las tarjetas vencidas en la base de datos.
        """
        tarjetas_expiradas = self.controlador_crud_pensionados.ver_tarjetas_expiradas()

        if len(tarjetas_expiradas) == 0:
            return

        self.mostrar_tabla_tarjetas_expiradas(tarjetas_expiradas)


    def mostrar_tabla_tarjetas_expiradas(self, datos):
        """
        Muestra una ventana con la tabla de tarjetas vencidas.

        :param datos: (list) Una lista de tuplas con los datos de las tarjetas vencidas.

        Esta funcion muestra una ventana con una tabla que contiene los datos de las tarjetas vencidas
        obtenidos desde la base de datos.
        """
        ventana = tk.Toplevel()
        ventana.title("Tarjetas vencidas")

        # Se elimina la funcionalidad del boton de cerrar
        ventana.protocol("WM_DELETE_WINDOW", lambda: cerrar_ventana())

        # Deshabilita los botones de minimizar y maximizar
        # ventana.attributes('-toolwindow', True)

        # Crear un Frame para contener la tabla y la etiqueta
        frame_tabla = tk.Frame(ventana)
        frame_tabla.pack(padx=10, pady=10)

        # Agregar etiqueta "Lista de tarjetas vencidas"
        etiqueta_titulo = tk.Label(frame_tabla, text="Lista de tarjetas vencidas", font=("Arial", 14))
        etiqueta_titulo.pack(side=tk.TOP, pady=10)

        # Crear el scroll de lado izquierdo
        scroll_y = tk.Scrollbar(frame_tabla, orient=tk.VERTICAL)

        # Crear la tabla utilizando el widget Treeview de ttk
        tabla = ttk.Treeview(frame_tabla, yscrollcommand=scroll_y.set)
        tabla["columns"] = ("Num_tarjeta", "Fecha_vigencia")

        # Configurar las columnas
        tabla.column("#0", width=0, stretch=tk.NO)  # Columna invisible para los índices
        tabla.column("Num_tarjeta", anchor=tk.CENTER, width=110)
        tabla.column("Fecha_vigencia", anchor=tk.CENTER, width=120)

        # Configurar los encabezados de las columnas
        tabla.heading("#0", text="", anchor=tk.W)
        tabla.heading("Num_tarjeta", text="Número de Tarjeta", anchor=tk.CENTER)
        tabla.heading("Fecha_vigencia", text="Fecha de Vigencia", anchor=tk.CENTER)

        # Insertar datos en la tabla
        for tarjeta, fecha in datos:
            tabla.insert("", "end", values=(tarjeta, fecha))

        # Configurar el scrollbar vertical para que controle la tabla
        scroll_y.config(command=tabla.yview)

        # Empacar el scrollbar vertical en el marco
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        tabla.pack(padx=10, pady=10)

        def cerrar_ventana():
            # Obtener la fecha y hora actual en formato deseado
            hoy = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            self.controlador_crud_pensionados.desactivar_tarjetas_expiradas(hoy)
            self.ver_pensionados()
            ventana.destroy()

        # Agregar boton "Aceptar" en color rojo centrado debajo de la tabla
        btn_aceptar = tk.Button(ventana, text="Aceptar", bg="red", command=cerrar_ventana, font=("Arial", 14))
        btn_aceptar.pack(side=tk.BOTTOM, pady=10)

        # Obtener las dimensiones de la ventana principal
        self.ventana1.update_idletasks()
        ancho_ventana_principal = self.ventana1.winfo_width()
        alto_ventana_principal = self.ventana1.winfo_height()

        # Obtener las dimensiones de la pantalla
        ancho_pantalla = ventana.winfo_screenwidth()
        alto_pantalla = ventana.winfo_screenheight()

        # Calcular la posicion de la ventana secundaria para que quede en el centro de la pantalla
        x = self.ventana1.winfo_x() + (ancho_ventana_principal - ventana.winfo_width()) // 2
        y = self.ventana1.winfo_y() + (alto_ventana_principal - ventana.winfo_height()) // 2

        # Verificar que la ventana secundaria no quede fuera de la pantalla
        x = max(0, min(x, ancho_pantalla - ventana.winfo_width()))
        y = max(0, min(y, alto_pantalla - ventana.winfo_height()))

        # Posicionar la ventana secundaria en el centro de la pantalla
        ventana.geometry(f"+{x}+{y}")

        # Elevar la ventana secundaria al frente de todas las otras ventanas
        ventana.lift()


    def mostrar_importe(self, text_importe):
        """
        Muestra el importe en la interfaz gráfica.

        :param text_importe: (str) El importe a mostrar.

        Esta funcion muestra el importe en la interfaz gráfica, actualizando el valor en la etiqueta correspondiente.
        """
        self.importe.set(text_importe)
        self.IImporte.config(text=self.importe.get())

# aplicacion1=FormularioOperacion()

