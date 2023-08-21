import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from escpos.printer import Usb
from zipfile import ZipFile, ZIP_DEFLATED
from subprocess import run, CalledProcessError
from os import path, getcwd, remove
from requests import get
from requests.exceptions import RequestException
from operacion import Operacion


class ToolsEmail:
    """Clase que proporciona herramientas relacionadas con el correo electrónico y archivos."""

    def __init__(self):
        """Constructor de la clase"""
        self.DB = Operacion()

    def check_internet_connection(self, url: str = "http://www.google.com", timeout: int = 10) -> bool:
        """Comprueba si hay una conexión activa a Internet mediante una petición HTTP a la URL dada.

        Args:
            url (str, optional): La URL a la que se realizará la petición. Por defecto es "http://www.google.com".
            timeout (int, optional): El tiempo máximo en segundos para esperar la respuesta. Por defecto es 5.

        Returns:
            bool: True si hay una conexión activa a Internet, False si no se puede establecer la conexión.
        """
        try:
            response = get(url, timeout=timeout)
            # Lanza una excepción si la respuesta HTTP no es exitosa
            response.raise_for_status()
            print("Conexión a Internet activa.")
            return True

        except RequestException:
            print("No se pudo establecer conexión a Internet.")
            return False

    def compress_file_to_zip(self, source_file: str, output_filename: str = None) -> str or None:
        """Comprime un archivo en un archivo ZIP.

        Args:
            source_file (str): Ruta al archivo que se comprimirá.
            output_filename (str): Nombre del archivo ZIP de salida. Si no se proporciona, se usará el nombre del archivo fuente con extensión ".zip".

        Returns:
            str or None: Ruta absoluta del archivo ZIP si la compresión es exitosa, None si hay algún error.
        """
        try:
            if output_filename is None:
                # Si no se proporciona un nombre de archivo de salida, usamos el nombre del archivo fuente con extensión ".zip"
                output_filename = source_file + '.zip'

            with ZipFile(output_filename, 'w', ZIP_DEFLATED) as zipf:
                arcname = path.basename(source_file)
                zipf.write(source_file, arcname)
                absolute_path_zip = path.abspath(output_filename)
                print("Archivo comprimido correctamente")
                return absolute_path_zip

        except Exception as e:
            print(f'Error al comprimir el archivo: {e}')
            return None

    def is_file_empty(self, file_path) -> bool:
        """Verifica si un archivo está vacío o no.

        Args:
            file_path (str): La ruta del archivo que se va a verificar.

        Returns:
            bool: True si el archivo está vacío, False si no lo está.
        """
        try:
            # Obtiene el tamaño del archivo en bytes y verifica si es cero
            return True if path.getsize(file_path) == 0 else False

        except Exception as e:
            # Maneja cualquier error que pueda ocurrir
            print(f"Error al verificar el archivo: {e}")
            return False

    def remove_file(self, path_file: str) -> None:
        """
        Elimina un archivo del sistema.

        Esta función toma la ruta de un archivo como entrada y trata de eliminarlo del sistema de archivos.

        Args:
            path_file (str): La ruta del archivo que se va a eliminar.

        """
        try:
            # Intenta eliminar el archivo
            remove(path_file)
            print(f"Archivo [{path_file}] fue eliminado exitosamente.")
        except Exception as e:
            # Maneja cualquier error que pueda ocurrir al intentar eliminar el archivo
            print(f"No se pudo eliminar el archivo [{path_file}]: {e}")


    def get_DB(self, backup_path: str = '/ruta/de/respaldo/Parqueadero1.sql') -> str or None:
        """Genera un respaldo de la base de datos utilizando el comando mysqldump.

        Args:
            backup_path (str, optional): La ruta donde se guardará el archivo de respaldo. Por defecto es '/ruta/de/respaldo/Parqueadero1.sql'.

        Returns:
            str or None: La ruta del archivo de respaldo si se crea exitosamente, None si ocurre un error.
        """
        try:
            # Configuración de la base de datos
            host = self.DB.host
            user = self.DB.user
            password = self.DB.password
            database = self.DB.database

            # Comando mysqldump (dependiendo del sistema operativo)
            command = f"mysqldump -h {host} -u {user} -p{password} {database} > {backup_path}"
            # command = f"cd C:/xampp/mysql/bin && mysqldump -h {host} -u {user} -p{password} {database} > {backup_path}"

            run(command, shell=True)

            if path.exists(backup_path) and not self.is_file_empty(backup_path):
                print("Base de datos respaldada exitosamente.")
                backup_path = path.abspath(backup_path)
                return backup_path
            else:
                print("El archivo de respaldo no se creó correctamente.")
                self.remove_file(backup_path)
                return None

        except CalledProcessError:
            print("Error al crear el respaldo.")
            self.remove_file(backup_path)
            return None

class SendEmail:
    """Clase que permite enviar correos electrónicos con archivos adjuntos."""

    def __init__(self, username: str, password: str, estacionamiento: str, smtp_server: str = "smtp.pasesa.com.mx", smtp_port: int = 1025) -> None:
        """Inicializa una instancia de la clase SendEmail para enviar correos electrónicos con archivos adjuntos.

        Args:
            username (str): El nombre de usuario para la cuenta de correo electrónico.
            password (str): La contraseña para la cuenta de correo electrónico.
            estacionamiento (str): Nombre del estacionamiento, utilizado en el nombre del archivo adjunto.
            smtp_server (str, opcional): El servidor SMTP para el envío de correos. Por defecto es "smtp.pasesa.com.mx".
            smtp_port (int, opcional): El puerto del servidor SMTP. Por defecto es 1025.
        """
        self.username = username
        self.password = password
        self.estacionamiento = estacionamiento
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port

        self.tools = ToolsEmail()

    def send_mail(self, to_email: str, subject: str, message: str, file: str) -> bool:
        """Envía un correo electrónico con un archivo adjunto.

        Args:
            to_email (str): La dirección de correo electrónico del destinatario.
            subject (str): El asunto del correo electrónico.
            message (str): El contenido del correo electrónico.
            file (str): Ruta al archivo que se adjuntará al correo.

        Returns:
            bool: True si el correo se envía exitosamente, False si hay algún error.
        """
        from_email = self.username

        # Verificar la conexión a Internet antes de intentar enviar el correo
        if not self.tools.check_internet_connection():
            return False
        else:
            try:
                # Crea la estructura del correo
                msg = MIMEMultipart()
                msg['From'] = from_email
                msg['To'] = to_email
                msg['Subject'] = subject

                msg.attach(MIMEText(message, 'plain'))

                zip_file = self.tools.compress_file_to_zip(file)
                self.tools.remove_file(file)

                if zip_file is None:
                    return False

                # Adjuntar el archivo al correo
                with open(zip_file, 'rb') as f:
                    attached_file = MIMEApplication(f.read(), _subtype="zip")
                    attached_file.add_header('content-disposition', 'attachment', filename=f'{self.estacionamiento}_DB.zip')
                    msg.attach(attached_file)

                # Conectar al servidor SMTP y enviar el correo
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    # Iniciar la conexión segura TLS
                    server.starttls()
                    # Inicio de sesión
                    server.login(self.username, self.password)
                    # Enviar correo
                    server.sendmail(from_email, to_email, msg.as_string())
                    # Terminar la sesión
                    server.quit()

                print('Correo enviado exitosamente.')
                self.tools.remove_file(zip_file)
                return True

            except Exception as e:
                print(e)
                return False

def call_process() -> str:
    """
    Envía la base de datos por correo electrónico.

    Returns:
        str: Mensaje informativo sobre el resultado del envío del correo.
    """
    # Nombre del estacionamiento
    nombre_estacionamiento = 'Tenayuca'

    # Datos de acceso a la cuenta de correo
    username = 'tenayuca200@pasesa.com.mx'
    password = '@Tenayuca200'
    EMAIL = "enviocorreospasesa@outlook.com"

    # Inicializar herramientas de correo electrónico y envío
    tools = ToolsEmail()
    email = SendEmail(
        username=username, 
        password=password, 
        estacionamiento=nombre_estacionamiento)

    # Generar ruta y obtener el archivo de respaldo de la base de datos
    path_db = getcwd() + f'/db_{nombre_estacionamiento}.sql'
    db_file = tools.get_DB(path_db)

    if db_file is None:
        return "Error: No se pudo generar el respaldo de la base de datos\n"

    # Crear el asunto y mensaje del correo
    hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subject = f"[{nombre_estacionamiento}][{hora}] Envio de Base de datos"
    message = f"Base de datos del estacionamiento {nombre_estacionamiento}."

    # Enviar el correo y manejar el resultado
    if email.send_mail(to_email=EMAIL, subject=subject, message=message, file=db_file):
        return "Base de datos enviada exitosamente.\n"
    else:
        return "Error: No se pudo enviar la base de datos por correo electrónico.\n"


def main() -> None:
    """
    Función principal del programa para enviar la base de datos por correo electrónico y mostrar el resultado.
    """
    try: 
        # Ejecutar la función para enviar el correo electrónico
        message_info = call_process()

        # Instanciar el objeto Usb para imprimir el resultado
        printer = Usb(0x04b8, 0x0e15, 0)

        # Alinea al centro el texto
        printer.set(align = "center")

        # Imprimir separadores y mensaje de resultado en la consola
        printer.text("-" * 30 + "\n")
        printer.text(f"{message_info}\n")
        printer.text("-" * 30 + "\n")
        printer.cut()
        printer.close()

        # Imprimir el mensaje en la consola
        print(message_info)
    except Exception as e:
        print(e)



if __name__ == "__main__":
    """
    Punto de entrada principal del programa.
    """
    # Ejecutar la función principal
    main()

