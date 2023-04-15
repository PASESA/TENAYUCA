
import os
file = open("qq.txt", "w")
file.write("Primera línea" + os.linesep)
file.write("Segunda línea")
file.close()
