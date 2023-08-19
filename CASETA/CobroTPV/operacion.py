import pymysql
from tkinter import messagebox as mb
import random
import qrcode

class Operacion:
    def __init__(self):
        self.host = "192.168.1.121"
        self.user = "Aurelio"
        self.password = "RG980320"
        self.database = "Parqueadero1"

    def abrir(self):
        conexion=pymysql.connect(host=self.host,
                                 user=self.user,
                                 passwd=self.password,
                                 database=self.database)

        return conexion


    def altaRegistroRFID(self, datos):
        cone=self.abrir()
        cursor=cone.cursor()
        sql="insert into Entradas(Entrada, CorteInc, Placas) values (%s,%s,%s)"
        cursor.execute(sql, datos)
        cone.commit()
        cone.close()

    def guardacobro(self, datos):
        cone=self.abrir()
        cursor=cone.cursor()
        sql = "update Entradas set vobo = %s, Importe = %s, TiempoTotal = %s, Entrada = %s, Salida = %s,TarifaPreferente = %s, QRPromo = %s where id = %s;"
        cursor.execute(sql, datos)
        cone.commit()
        cone.close()

    def ValidaPromo(self, datos):
        cone=self.abrir()
        cursor=cone.cursor()
        sql="select id from Entradas where QRPromo = %s "
       #sql="select descripcion, precio from articulos where codigo=%s"
        cursor.execute(sql, datos)
        cone.close()
        return cursor.fetchall() 

    def consulta(self, datos):
        cone=self.abrir()
        cursor=cone.cursor()
        sql="select Entrada, Salida, id, TiempoTotal, TarifaPreferente, Importe, Placas from Entradas where id=%s"
       #sql="select descripcion, precio from articulos where codigo=%s"
        cursor.execute(sql, datos)
        cone.close()
        return cursor.fetchall()

    def recuperar_todos(self):
        cone=self.abrir()
        cursor=cone.cursor()
        sql="select id, Entrada, Salida from Entradas"
        cursor.execute(sql)
        cone.close()
        return cursor.fetchall()

    def recuperar_sincobro(self):
        cone=self.abrir()
        cursor=cone.cursor()
        sql="select id, Entrada, Salida, Importe from Entradas where CorteInc = 0 and Importe is not null "
        cursor.execute(sql)
        cone.close()
        return cursor.fetchall()
    def desglose_cobrados(self,Numcorte):
        cone=self.abrir()
        cursor=cone.cursor()
        #sql="SELECT TarifaPreferente,Importe, Count(*) as cuantos FROM Entradas where CorteInc = 6 "
        #sql="SELECT TarifaPreferente,Importe, Count(*) as cuantos FROM Entradas where CorteInc = %s GROUP BY TarifaPreferente,Importe;"
        sql="SELECT Count(*),TarifaPreferente,Importe, Count(*)*Importe  as cuantos FROM Entradas where CorteInc = %s GROUP BY TarifaPreferente,Importe;"
        #sql="select id, Entrada, Salida, Importe from Entradas where CorteInc = 0 and Importe is not null "
        cursor.execute(sql,Numcorte)
        cone.close()
        return cursor.fetchall()
    def Autos_dentro(self):
        cone=self.abrir()
        cursor=cone.cursor()
        sql="select id, Entrada, Placas from Entradas where CorteInc = 0 and Importe is null and Salida is null "
        cursor.execute(sql)
        cone.close()
        return cursor.fetchall()

    def CuantosAutosdentro(self):
        cone=self.abrir()
        cursor=cone.cursor()
        sql="select count(*) from Entradas where CorteInc = 0 and Importe is null and Salida is null "
        cursor.execute(sql)
        cone.close()
        return cursor.fetchall()
    def Quedados_Sensor(self, datos):
        cone=self.abrir()
        cursor=cone.cursor()
        sql="select Quedados from Cortes where Folio=%s"
       #sql="select descripcion, precio from articulos where codigo=%s"
        cursor.execute(sql, datos)
        cone.close()
        return cursor.fetchall()

    def NumBolQued(self, datos):
        cone=self.abrir()
        cursor=cone.cursor()
        sql="select NumBolQued from Cortes where Folio=%s"
       #sql="select descripcion, precio from articulos where codigo=%s"
        cursor.execute(sql, datos)
        cone.close()
        return cursor.fetchall()
    def EntradasSensor(self):
        cone=self.abrir()
        cursor=cone.cursor()
        sql="select EntSens from AccesosSens where Folio=1"
       #sql="select descripcion, precio from articulos where codigo=%s"
        cursor.execute(sql)
        cone.close()
        return cursor.fetchall()
    def SalidasSensor(self):
        cone=self.abrir()
        cursor=cone.cursor()
        sql="select SalSens from AccesosSens where Folio=1"
       #sql="select descripcion, precio from articulos where codigo=%s"
        cursor.execute(sql)
        cone.close()
        return cursor.fetchall()

    def CuantosBoletosCobro(self):
        cone=self.abrir()
        cursor=cone.cursor()
        sql="select count(*) from Entradas where CorteInc = 0 and Importe is not null and Salida is not null "
        cursor.execute(sql)
        cone.close()
        return cursor.fetchall()
    def BEDCorte(self):
        cone=self.abrir()
        cursor=cone.cursor()
        sql="select count(*) from Entradas where ((vobo is null and TarifaPreferente is null) or (vobo = 'lmf' and TarifaPreferente = ''))"
        cursor.execute(sql)
        cone.close()
        return cursor.fetchall()

    def BAnteriores(self):
        cone=self.abrir()
        cursor=cone.cursor()
        sql="select count(*) from Entradas where vobo = 'ant' "
        cursor.execute(sql)
        cone.close()
        return cursor.fetchall()

    def corte(self):
        cone=self.abrir()
        cursor=cone.cursor()
        sql="select COALESCE(sum(importe), 0) from Entradas where CorteInc = 0"
        cursor.execute(sql)
        cone.close()
        return cursor.fetchall()
    def MaxfolioEntrada(self):
        cone=self.abrir()
        cursor=cone.cursor()
        sql="select max(id) from Entradas;"
        cursor.execute(sql)
        cone.close()
        return cursor.fetchall()

    def Maxfolio_Cortes(self):
        cone=self.abrir()
        cursor=cone.cursor()
        sql="select max(Folio) from Cortes;"
        cursor.execute(sql)
        cone.close()
        return cursor.fetchall()

    def ActualizarEntradasConcorte(self, maxnum):
        cone=self.abrir()
        cursor=cone.cursor()
        sql = "update Entradas set CorteInc = %s, vobo = %s where TiempoTotal is not null and CorteInc=0;"
        #sql = "update Entradas set CorteInc=%s where TiempoTotal is not null and CorteInc=0;"
        cursor.execute(sql,maxnum)
        cone.commit()
        cone.close()

    def NocobradosAnt(self, vobo):
        cone=self.abrir()
        cursor=cone.cursor()
        sql = "update Entradas set vobo = %s where Importe is null and CorteInc=0;"
        cursor.execute(sql,vobo)
        cone.commit()
        cone.close()

    def obtenerNumCorte(self):
        cone=self.abrir()
        cursor=cone.cursor()
        sql="select max(Folio) from Cortes"
        #sql = "update Entradas set CorteInc = 1 WHERE Importe > 0"
        cursor.execute(sql)
        #cone.commit()
        cone.close()
        return cursor.fetchall()
    def MaxnumId(self):
        cone=self.abrir()
        cursor=cone.cursor()
        sql="select max(idInicial) from Cortes"
        #sql = "update Entradas set CorteInc = 1 WHERE Importe > 0"
        cursor.execute(sql)
        #cone.commit()
        cone.close()
        return cursor.fetchall()

    def GuarCorte(self, datos):
        cone=self.abrir()
        cursor=cone.cursor()
        sql="insert into Cortes(Importe, FechaIni, FechaFin,Quedados,idInicial,NumBolQued) values (%s,%s,%s,%s,%s,%s)"
        #sql = "update Entradas set CorteInc = 1 WHERE Importe > 0"
        cursor.execute(sql,datos)
        cone.commit()
        cone.close()
    def UltimoCorte(self):
        cone=self.abrir()
        cursor=cone.cursor()
        sql="select max(FechaFin) from Cortes;"
        cursor.execute(sql)
        cone.close()
        return cursor.fetchall()

    #### REPORTE DE CORTES A EXCEL ####
    def Cortes_MaxMin(self, datos):
        cone=self.abrir()
        cursor=cone.cursor()
        sql="SELECT max(FechaIni), min(FechaIni), max(FechaFin) FROM Cortes where MONTH(FechaIni)=%s AND YEAR(FechaIni)=%s "
        #sql="SELECT max(FechaFin), min(FechaFin) FROM Cortes where MONTH(FechaFin)=%s AND YEAR(FechaFin)=%s "
        cursor.execute(sql,datos)
        cone.close()
        return cursor.fetchall()
    def Cortes_Folio(self, datos):
        cone=self.abrir()
        cursor=cone.cursor()
        sql="SELECT Folio FROM Cortes where FechaIni=%s"
        #sql="SELECT Folio FROM Cortes where FechaFin=%s"
        cursor.execute(sql,datos)
        cone.close()
        return cursor.fetchall()
    def Registros_corte(self, datos):
        cone=self.abrir()
        cursor=cone.cursor()
        sql="SELECT id, Entrada, Salida, TiempoTotal, Importe, CorteInc, Placas, TarifaPreferente FROM Entradas where CorteInc > (%s-1) AND CorteInc < (%s+1)"  #CorteInc > (%s-1) AND CorteInc < (%s+1)
        cursor.execute(sql,datos)
        cone.close()
        return cursor.fetchall()
    def Totales_corte(self, datos1):
        cone=self.abrir()
        cursor=cone.cursor()
        #sql="SELECT TarifaPreferente,Importe, Count(*) as cuantos FROM Entradas where CorteInc = 6 " sum(Importe),
        #sql="SELECT TarifaPreferente,Importe, Count(*) as cuantos FROM Entradas where CorteInc = %s GROUP BY TarifaPreferente,Importe;"
        sql="SELECT sum(Importe), max(CorteInc), min(CorteInc), Count(TarifaPreferente) FROM Entradas where CorteInc > (%s-1) AND CorteInc < (%s+1)" #Entrada > %s AND Entrada < %s
        #sql="select id, Entrada, Salida, Importe from Entradas where CorteInc = 0 and Importe is not null "
        cursor.execute(sql,datos1)
        cone.close()
        return cursor.fetchall()
    def Resumen_promo(self, datos1):
        cone=self.abrir()
        cursor=cone.cursor()
        sql="SELECT Count(TarifaPreferente),TarifaPreferente,Importe, sum(Importe) as ImporteTot FROM Entradas where CorteInc > (%s-1) AND CorteInc < (%s+1) GROUP BY TarifaPreferente ORDER BY ImporteTot DESC;" #Entrada >= %s AND Salida <= %s
        #sql="SELECT Count(*),TarifaPreferente,Importe, Count(*)*Importe  as cuantos FROM Entradas where CorteInc = %s GROUP BY TarifaPreferente,Importe;"
        #sql="SELECT Count(TarifaPreferente),TarifaPreferente,Importe, Count(TarifaPreferente)*Importe as ImporteTot FROM Entradas where CorteInc > (%s-1) AND CorteInc < (%s+1) GROUP BY TarifaPreferente,Importe ORDER BY ImporteTot;"
        cursor.execute(sql,datos1)
        cone.close()
        return cursor.fetchall()

    ####PENSIONADOS####

    def ValidarID(self, datos):
        cone=self.abrir()
        cursor=cone.cursor()
        sql="SELECT id_cliente FROM Pensionados WHERE Num_tarjeta=%s"
        cursor.execute(sql,datos)
        cone.close()
        return cursor.fetchall()       
    def AltaPensionado(self, datos):
        cone=self.abrir()
        cursor=cone.cursor()
        sql="INSERT INTO Pensionados(Num_tarjeta, Nom_cliente, Apell1_cliente, Apell2_cliente, Fecha_alta, Telefono1, Telefono2, Ciudad, Colonia, CP, Calle_num, Placas, Modelo_auto, Color_auto, Monto, Cortesia, Tolerancia, Vigencia, Fecha_vigencia) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        #datos=(numtarjeta, Nombre, ApellidoPat, ApellidoMat, fechaAlta, Telefono1, Telefono2, Ciudad, Colonia, CP, Calle, Placa, Modelo, Color, montoxmes, cortesia, tolerancia)
        cursor.execute(sql, datos)
        cone.commit()
        cone.close()
    def ConsultaPensionado(self, datos):
        cone=self.abrir()
        cursor=cone.cursor()
        sql="SELECT Nom_cliente, Apell1_cliente, Apell2_cliente, Telefono1, Telefono2, Ciudad, Colonia, CP, Calle_num, Placas, Modelo_auto, Color_auto, Fecha_vigencia, Estatus, Vigencia, Monto, Cortesia, Tolerancia FROM Pensionados where id_cliente=%s"
        cursor.execute(sql,datos)
        cone.close()
        return cursor.fetchall()
    def ModificarPensionado(self, datos):
        cone=self.abrir()
        cursor=cone.cursor()
        sql="UPDATE Pensionados SET Num_tarjeta=%s, Nom_cliente=%s, Apell1_cliente=%s, Apell2_cliente=%s, Telefono1=%s, Ciudad=%s, Colonia=%s, CP=%s, Calle_num=%s, Placas=%s, Modelo_auto=%s, Color_auto=%s, Monto=%s, Cortesia=%s, Tolerancia=%s, Ult_Cambio=%s, Vigencia=%s, Fecha_vigencia=%s  WHERE id_cliente=%s"
        #datos=(numtarjeta, Nombre, ApellidoPat, ApellidoMat, Telefono1, Telefono2, Ciudad, Colonia, CP, Calle, Placa, Modelo,                    Color, montoxmes, cortesia, tolerancia, PensionadoOpen)
        cursor.execute(sql, datos)
        cone.commit()
        cone.close()
    def CobrosPensionado(self, datos):
        cone=self.abrir()
        cursor=cone.cursor()
        sql="INSERT INTO PagosPens(idcliente, num_tarjeta, Fecha_pago, Fecha_vigencia, Mensualidad, Monto, TipoPago) values (%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql,datos)
        cone.commit()
        cone.close()
    def UpdPensionado(self, datos):
        cone=self.abrir()
        cursor=cone.cursor()
        sql="UPDATE Pensionados SET Vigencia=%s, Fecha_vigencia=%s WHERE id_cliente=%s"
        #sql = "update Entradas set CorteInc = %s, vobo = %s where TiempoTotal is not null and CorteInc=0;"
        cursor.execute(sql, datos)
        cone.commit()
        cone.close()
    def UpdMovsPens(self, datos):
        cone=self.abrir()
        cursor=cone.cursor()
        sql="UPDATE MovimientosPens SET Salida=%s, Estatus=%s WHERE idcliente=%s and Salida is null"
        #sql = "update Entradas set CorteInc = %s, vobo = %s where TiempoTotal is not null and CorteInc=0;"
        cursor.execute(sql, datos)
        cone.commit()
        cone.close()
    def UpdPens2(self, datos):
        cone=self.abrir()
        cursor=cone.cursor()
        sql="UPDATE Pensionados SET Estatus=%s WHERE id_cliente=%s"
        #sql = "update Entradas set CorteInc = %s, vobo = %s where TiempoTotal is not null and CorteInc=0;"
        cursor.execute(sql, datos)
        cone.commit()
        cone.close()
    def ValidarTarj(self, datos):
        cone=self.abrir()
        cursor=cone.cursor()
        sql="SELECT id_cliente, Estatus FROM Pensionados WHERE Num_tarjeta=%s"
        cursor.execute(sql,datos)
        cone.close()
        return cursor.fetchall()

    ##### CONSULTA PENSIONADOS ADENTRO    
    def TreaPenAdentro(self):
        cone=self.abrir()
        cursor=cone.cursor()
        sql="""SELECT Num_tarjeta, Nom_cliente, Apell1_cliente, Placas, Modelo_auto from Pensionados where Estatus = "Adentro";"""
        cursor.execute(sql)
        cone.close()
        return cursor.fetchall()

    #####USUARIOS###

    def ConsultaUsuario(self, datos):
        cone=self.abrir()
        cursor=cone.cursor()
        sql="SELECT Id_usuario, Contrasena, Nom_usuario FROM Usuarios WHERE Usuario = %s"
        cursor.execute(sql,datos)
        cone.close()
        return cursor.fetchall()
    def CajeroenTurno(self):
        cone=self.abrir()
        cursor=cone.cursor()
        sql="SELECT min(id_movs), nombre, inicio, turno, Idusuario FROM MovsUsuarios where CierreCorte is null"
        cursor.execute(sql)
        cone.close()
        return cursor.fetchall()
    def IniciosdeTurno(self, dato):
        cone=self.abrir()
        cursor=cone.cursor()
        sql="SELECT inicio, usuario FROM MovsUsuarios where inicio > %s" #and CierreCorte = 'No aplica'  Idusuario = %s and
        cursor.execute(sql, dato)
        cone.close()
        return cursor.fetchall()
    def ActuaizaUsuario(self, actual):
        cone=self.abrir()
        cursor=cone.cursor()
        sql="INSERT INTO MovsUsuarios(Idusuario, usuario, inicio, nombre, turno) values (%s,%s,%s,%s,%s)"
        #sql="INSERT INTO PagosPens(idcliente, num_tarjeta, Fecha_pago, Fecha_vigencia, Mensualidad, Monto) values (%s,%s,%s,%s,%s,%s)"
        cursor.execute(sql,actual)
        cone.commit()
        cone.close()
    def Cierreusuario(self, datos):
        cone=self.abrir()
        cursor=cone.cursor()
        sql = "update MovsUsuarios set CierreCorte = %s where  id_movs = %s;"
        cursor.execute(sql,datos)
        cone.commit()
        cone.close()
    def NoAplicausuario(self, dato):
        cone=self.abrir()
        cursor=cone.cursor()
        sql = "update MovsUsuarios set CierreCorte = 'No aplica' where  id_movs > %s;"
        cursor.execute(sql,dato)
        cone.commit()
        cone.close()

    def nombre_usuario_activo(self):
        """
        Esta función realiza una consulta a la base de datos para obtener el nombre del usuario que esta activo.
        Args:
        - self: referencia a la clase donde está definida la función.
        Returns:
        - resultados: lista de tuplas que contienen la siguiente información:
            - nombre: El nombre del usuario
        Esta función utiliza la librería de MySQL Connector para conectarse a la base de datos y ejecutar una consulta SQL.
        """

        # Se establece la conexión con la base de datos.
        cone = self.abrir()

        # Se crea un cursor para ejecutar la consulta.
        cursor = cone.cursor()

        # Se define la consulta SQL.
        sql = f"""SELECT nombre FROM MovsUsuarios WHERE CierreCorte IS Null"""

        # Se ejecuta la consulta y se almacenan los resultados en una lista de tuplas.
        cursor.execute(sql)
        resultados = cursor.fetchall()

        # Se cierra la conexión con la base de datos.
        cone.close()

        # Se devuelve la lista de tuplas con los resultados de la consulta.
        return resultados

    def total_pensionados_corte(self, corte):
        """
        Realiza una consulta a la base de datos para obtener la cantidad y el importe total de los pagos de pensiones 
        realizados en un corte específico.
        Args:
            self: referencia a la clase donde está definida la función.
            corte (int): el número de folio del corte que se desea consultar.
        Returns:
            resultados (list): una lista de tuplas que contienen la siguiente información:
                - Cuantos (int): la cantidad de pagos de pensiones realizados en el corte.
                - Concepto (str): una cadena que indica el tipo de pago (en este caso, siempre será "Pensionados").
                - ImporteTotal (float): el importe total de los pagos de pensiones realizados en el corte.
        Esta función utiliza la librería de MySQL Connector para conectarse a la base de datos y ejecutar una consulta SQL.
        """
        # Se establece la conexión con la base de datos.
        cone = self.abrir()

        # Se crea un cursor para ejecutar la consulta.
        cursor = cone.cursor()

        # Se define la consulta SQL.
        sql = f"""SELECT COUNT(*) AS Cuantos, TipoPago AS Concepto, COALESCE(FORMAT(SUM(p.Monto), 2), 0) AS ImporteTotal FROM PagosPens p INNER JOIN Cortes c ON p.Fecha_pago BETWEEN c.FechaIni AND c.FechaFin WHERE c.Folio = {corte} GROUP BY TipoPago;"""

        # Se ejecuta la consulta y se almacenan los resultados en una lista de tuplas.
        cursor.execute(sql)
        resultados = cursor.fetchall()

        # Se cierra la conexión con la base de datos.
        cone.close()

        # Se devuelve la lista de tuplas con los resultados de la consulta.
        return resultados

    def cifrar_folio(self, folio):
        """
        Cifra un número de folio utilizando una tabla de sustitución numérica.

        Args:
            folio (int): Número de folio a cifrar.

        Returns:
            str: Número de folio cifrado.
        """

        # Convierte el número de folio en una cadena de texto.
        folio = str(folio)

        # Genera un número aleatorio de 5 dígitos y lo convierte en una cadena de texto.
        num_random = random.randint(10000, 99999)
        numero_seguridad = str(num_random)

        # Concatena el número de seguridad al número de folio.
        folio = folio + numero_seguridad


        # Tabla de sustitución numérica.
        tabla = {'0': '5', '1': '3', '2': '9', '3': '1', '4': '7', '5': '0', '6': '8', '7': '4', '8': '6', '9': '2'}

        # Convierte el número de folio cifrado a una lista de dígitos.
        digitos = list(folio)

        # Sustituye cada dígito por el número correspondiente en la tabla de sustitución.
        cifrado = [tabla[digito] for digito in digitos]

        # Convierte la lista cifrada de vuelta a una cadena de texto.
        cifrado = ''.join(cifrado)

        # Devuelve el número de folio cifrado.
        return cifrado

    def descifrar_folio(self, folio_cifrado):
        """
        Descifra un número de folio cifrado utilizando una tabla de sustitución numérica.

        Args:
            folio_cifrado (str): Número de folio cifrado.

        Returns:
            str: Número de folio descifrado.
        """
        try:
            # Verifica si el número de folio es válido.
            if len(folio_cifrado) <= 5:
                raise ValueError("El folio no es válido, escanee nuevamente, si el error persiste contacte con un administrador.")

            # Verifica si el número de folio tiene caracteres inválidos.
            caracteres_invalidos = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '=', '+', '{', '}', '[', ']', '|', '\\', ':', ';', '<', '>', ',', '.', '/', '?']
            if any(caracter in folio_cifrado for caracter in caracteres_invalidos):
                raise TypeError("El folio no tiene un formato válido")

            # Tabla de sustitución numérica.
            tabla = {'0': '5', '1': '3', '2': '9', '3': '1', '4': '7', '5': '0', '6': '8', '7': '4', '8': '6', '9': '2'}

            # Convierte el número de folio cifrado a una lista de dígitos.
            digitos_cifrados = list(folio_cifrado)

            # Crea una tabla de sustitución inversa invirtiendo la tabla original.
            tabla_inversa = {valor: clave for clave, valor in tabla.items()}

            # Sustituye cada dígito cifrado por el número correspondiente en la tabla de sustitución inversa.
            descifrado = [tabla_inversa[digito] for digito in digitos_cifrados]

            # Convierte la lista descifrada de vuelta a una cadena de texto.
            descifrado = ''.join(descifrado)

            # Elimina los últimos 4 dígitos, que corresponden al número aleatorio generado en la función cifrar_folio.
            descifrado = descifrado[:-5]

            # Retorna el folio descifrado.
            return descifrado

        # Maneja el error si el formato del número de folio es incorrecto.
        except TypeError as error:
            mb.showerror("Error", f"El folio tiene un formato incorrecto, si el error persiste contacte a un administrador y muestre el siguiente error:\n{error}")
            return None

        # Maneja cualquier otro error que pueda ocurrir al descifrar el número de folio.
        except Exception as error:
            mb.showerror("Error", f"Ha ocurrido un error al descifrar el folio, intente nuevamente, si el error persiste contacte a un administrador y muestre el siguiente error:\n{error}")
            return None

    def generar_QR(self, QR_info: str, path: str = "reducida.png") -> None:
        """Genera un código QR a partir de la información dada y lo guarda en un archivo de imageen.

        Args:
            QR_info (str): La información para generar el código QR.
            path (str, optional): La ruta y el nombre del archivo de imagen donde se guardará el código QR, por defecto es "reducida.png".
        """
        # Generar el código QR
        img = qrcode.make(QR_info)

        # Redimensionar el código QR a un tamaño específico
        img = img.get_image().resize((320, 320))

        # Guardar la imagen redimensionada en un archivo
        img.save(path)


    def Boletos_perdidos_generados(self):
        cone=self.abrir()
        cursor=cone.cursor()
        sql = """SELECT COUNT(*) AS "BOLETOS PERDIDOS GENERADOS" FROM Entradas WHERE `Placas` = "BoletoPerdido" AND CorteInc = 0;"""
        cursor.execute(sql)        
        cone.commit()

        resultados = cursor.fetchall()

        # Se cierra la conexión con la base de datos.
        cone.close()

        # Se devuelve la lista de tuplas con los resultados de la consulta.
        return resultados

    def Boletos_perdidos_generados_desglose(self):
        cone=self.abrir()
        cursor=cone.cursor()
        sql = """SELECT id, Entrada, Salida, Placas FROM Entradas WHERE `Placas` = "BoletoPerdido" AND CorteInc = 0;"""
        cursor.execute(sql)        
        cone.commit()

        resultados = cursor.fetchall()

        # Se cierra la conexión con la base de datos.
        cone.close()

        # Se devuelve la lista de tuplas con los resultados de la consulta.
        return resultados



    def Boletos_perdidos_cobrados(self, Numcorte):
        cone=self.abrir()
        cursor=cone.cursor()
        sql = """SELECT COUNT(*) AS "BOLETOS PERDIDOS COBRADOS" FROM Entradas WHERE `Placas` = "BoletoPerdido" AND CorteInc = %s AND TarifaPreferente IS NOT NULL;"""
        cursor.execute(sql, Numcorte)        
        cone.commit()
        resultados = cursor.fetchall()

        # Se cierra la conexión con la base de datos.
        cone.close()

        # Se devuelve la lista de tuplas con los resultados de la consulta.
        return resultados


    def Boletos_perdidos_cobrados_desglose(self, Numcorte):
        cone=self.abrir()
        cursor=cone.cursor()
        sql = """SELECT id, Entrada, Salida, Placas FROM Entradas WHERE `Placas` = "BoletoPerdido" AND CorteInc = %s AND TarifaPreferente IS NOT NULL;"""
        cursor.execute(sql, Numcorte)        
        cone.commit()
        resultados = cursor.fetchall()

        # Se cierra la conexión con la base de datos.
        cone.close()

        # Se devuelve la lista de tuplas con los resultados de la consulta.
        return resultados



    def Boletos_perdidos_no_cobrados(self):
        cone=self.abrir()
        cursor=cone.cursor()
        sql = """SELECT COUNT(*) AS "BOLETOS PERDIDOS NO COBRADOS" FROM Entradas WHERE `Placas` = "BoletoPerdido" AND CorteInc = 0 AND TarifaPreferente IS NULL;"""
        cursor.execute(sql)        
        cone.commit()
        resultados = cursor.fetchall()

        # Se cierra la conexión con la base de datos.
        cone.close()

        # Se devuelve la lista de tuplas con los resultados de la consulta.
        return resultados


