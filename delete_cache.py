import os
import shutil

def limpiar_cache():
    """
    Elimina todos los archivos de caché '*.pyc' y directorios '__pycache__' 
    en todas las carpetas y subcarpetas del directorio actual.

    Args:
        None

    Returns
        None

    Raises:
        None
    """

    # Recorre recursivamente todas las carpetas y elimina los archivos de caché
    for root, dirs, files in os.walk(".", topdown=False):
        for name in files:
            # Verifica si el archivo es un archivo de caché '*.pyc'
            if name.endswith(".pyc"):
                print(f"{os.path.join(root, name)} -> Eliminando archivo de caché")
                os.remove(os.path.join(root, name))
        for name in dirs:
            # Verifica si el directorio es un directorio de caché '__pycache__'
            if name == "__pycache__":
                print(f"{os.path.join(root, name)} -> Eliminando directorio de caché")
                shutil.rmtree(os.path.join(root, name))


def main():
    limpiar_cache()

if __name__ == "__main__":
    main()
