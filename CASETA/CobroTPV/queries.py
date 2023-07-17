import re
from pymysql import err
from tkinter import messagebox
from operacion import Operacion
import traceback

class usuarios:

    def __init__ (self):
        operacion = Operacion()
        self.connection = operacion.abrir()

    def execute_query(self, query: str):
        """
        Ejecuta una consulta en la base de datos.

        :param query (str): La consulta SQL a ejecutar.

        :raises pymysql.err.OperationalError: Si la conexion se pierde.
        :raises err.ProgrammingError: Si la tabla no existe.

        :return:
            - result (list): Una lista con los resultados de la consulta.
        """
        try:
            if self.connection:
                # Crea un objeto cursor para ejecutar la consulta
                self.cursor = self.connection.cursor()

                # Se ejecuta la consulta
                self.cursor.execute(query)

                # Obtiene los resultados de la consulta
                result = self.cursor.fetchall()

                # Confirma los cambios en la base de datos
                self.connection.commit()

                # Cierra el cursor
                self.cursor.close()

                # Retorna los resultados de la consulta
                return result

        except err.OperationalError as e:
            print(e)
            traceback.print_exc()
            if "10054" in str(e):
                print(e)
                messagebox.showwarning("Error", "Se ha perdido la conexión con el servidor.\nEl programa se cerrará, posterior a eso inicie nuevamente sesión\n\nEn caso de que el error persista contacte a un administrador.")

        except err.ProgrammingError as error:
            traceback.print_exc()
            print(error)
            # Aquí se ejecuta el código en caso de que se genere la excepción ProgrammingError
            error_message = str(error)
            match = re.search(r"\((\d+),", error_message)
            error_number = int(match.group(1))
            if error_number == 1146:
                print(error)
                messagebox.showwarning("Error", f"Error: La tabla no existe.\n Es probable que la conexion actual no cuente con la tabla a la que intenta acceder, de ser caso contrario contacte con un administrador.")
                return None

        except Exception as e:
            print(e)
            traceback.print_exc()
            messagebox.showwarning("Error", f"Error al realizar la consulta, por favor contacte con un administrador y muestre el siguiente error:\n Error: {str(e)} ")
            return None


    def agregar_usuarios(self, datos):
        datos = tuple(datos)

        if self.connection:

            query = f"INSERT INTO Usuarios (Usuario, Contrasena, Nom_usuario, Fecha_alta, Telefono1, TelefonoEmer, Sucursal) VALUES {datos};"

            # Se ejecuta la consulta
            self.execute_query(query)

    def consultar_usuario(self, id):
        if self.connection:

            query = f"SELECT Usuario, Contrasena, Nom_usuario, Telefono1, TelefonoEmer, Sucursal FROM Usuarios WHERE Id_usuario = {id}"

            # Se ejecuta la consulta y se obtiene el resultado.
            resultado = self.execute_query(query)

            return resultado

    def ver_usuarios(self):

        if self.connection:

            query = f"SELECT Id_usuario, Usuario, Nom_usuario, Fecha_alta, Telefono1, TelefonoEmer, Sucursal FROM Usuarios"

            # Se ejecuta la consulta y se obtiene el resultado.
            resultado = self.execute_query(query)

            return resultado

    def eliminar_usuario(self, id):

        if self.connection:

            query = f"DELETE FROM Usuarios WHERE Id_usuario = {id}"

            # Se ejecuta la consulta
            self.execute_query(query)

    def actualizar_usuarios(self, datos, id):

        if self.connection:
            datos = tuple(datos)
        
            query = f"UPDATE Usuarios SET Usuario = '{datos[0]}', Contrasena = '{datos[1]}', Nom_usuario = '{datos[2]}',  Telefono1 = '{datos[3]}', TelefonoEmer = '{datos[4]}', Sucursal = '{datos[5]}' WHERE Id_usuario = '{id}';"

            # Se ejecuta la consulta
            self.execute_query(query)

class pensionados(usuarios):

    def agregar_pensionados(self, datos):
        datos = tuple(datos)

        if self.connection:

            query = f"INSERT INTO Pensionados (Num_tarjeta, Nom_cliente, Apell1_cliente, Apell2_cliente, Fecha_alta, Telefono1, Telefono2, Ciudad, Colonia, CP, Calle_num, Placas, Modelo_auto, Color_auto, Monto, Cortesia, Tolerancia, Vigencia) VALUES {datos};"

            # Se ejecuta la consulta
            self.execute_query(query)

    def consultar_pensionado(self, Num_tarjeta):
        if self.connection:
            query = f"SELECT Num_tarjeta, Nom_cliente, Apell1_cliente, Apell2_cliente, Telefono1, Telefono2, Ciudad, Colonia, CP, Calle_num, Placas, Modelo_auto, Color_auto, Monto, Cortesia, Tolerancia, Fecha_vigencia, Vigencia FROM Pensionados WHERE Num_tarjeta = {Num_tarjeta}"

            # Se ejecuta la consulta y se obtiene el resultado.
            resultado = self.execute_query(query)

            return resultado

    def ver_pensionados(self):
        if self.connection:
            query = f"SELECT Num_tarjeta, Cortesia, Nom_cliente, Estatus, Fecha_vigencia, Tolerancia, Id_cliente, Vigencia FROM Pensionados ORDER BY Id_cliente DESC"

            # Se ejecuta la consulta y se obtiene el resultado.
            resultado = self.execute_query(query)

            return resultado

    def eliminar_pensinado(self, id):
        if self.connection:
            query = f"DELETE FROM Usuarios WHERE Id_usuario = {id}"

            # Se ejecuta la consulta
            self.execute_query(query)

    def actualizar_pensionado(self, datos_pensionado, Num_tarjeta):
        datos_pensionado = tuple(datos_pensionado)
        vigencia = datos_pensionado[17]
        if vigencia == None:vigencia ='Null'
        else: vigencia = f"""'{vigencia}'"""


        query =f"""UPDATE Pensionados SET Num_tarjeta = '{datos_pensionado[0]}', Nom_cliente = '{datos_pensionado[1]}', Apell1_cliente = '{datos_pensionado[2]}', Apell2_cliente = '{datos_pensionado[3]}', Telefono1 = '{datos_pensionado[4]}', Telefono2 = '{datos_pensionado[5]}', Ciudad = '{datos_pensionado[6]}', Colonia = '{datos_pensionado[7]}', CP = '{datos_pensionado[8]}', Calle_num = '{datos_pensionado[9]}', Placas = '{datos_pensionado[10]}', Modelo_auto = '{datos_pensionado[11]}', Color_auto = '{datos_pensionado[12]}', Monto = '{datos_pensionado[13]}', Cortesia = '{datos_pensionado[14]}', Tolerancia = {datos_pensionado[15]}, Ult_Cambio = '{datos_pensionado[16]}', Fecha_vigencia = {vigencia}, Vigencia = '{datos_pensionado[18]}' WHERE Num_tarjeta = '{Num_tarjeta}';"""

        # Se ejecuta la consulta
        self.execute_query(query)


