import os 
import cups
from datetime import datetime, date, time, timedelta
import qrcode	
import time, pprint, cups 
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
fechaEntro = datetime.today()

fSTR=str(fechaEntro)
print("fSTR",fSTR)
masuno=str(1)
imgqr=(fSTR + masuno)
print("imgqr",imgqr)		
img = qrcode.make(imgqr)
img.save("qr.png")
page_width = 195
page_height = 200
canvas = canvas.Canvas("PdfGen.pdf", pagesize=(page_width, page_height)) 
#canvas = canvas.Canvas("PdfGen.pdf", pagesize=letter)
canvas.setLineWidth(.3)
canvas.setFont('Helvetica', 12)

canvas.drawString(30,160,'CARTA DE PRUEBA')
canvas.line(30,159,200,159)
canvas.drawString(30,145,fSTR)
canvas.drawString(50,130,"24/10/2020")
canvas.drawString(30,115,'Aurelio Guarneros  inteligente:')
canvas.drawString(30,100,"<NOMBRE>")
#canvas.create_image(30, 300, image=oso.jpg, anchor="nw")
#canvas.drawString(30,85,'ETIQUETA:')
#canvas.drawString(30,70,"<ASUNTO DE LA CARTA >")
#canvas.line(30,65,200,65)
# Dibujamos una imagen (IMAGEN, X,Y, WIDTH, HEIGH)
canvas.drawImage('oso.jpg', 80, 30, 60, 60)
canvas.line(30,95,200,95)
canvas.drawImage('qr.png', 30, 30, 60, 60)
canvas.line(30,29,200,29)
canvas.save()
print("se genero el archivo PdfGen.pdf")
conn = cups.Connection()
printers = conn.getPrinters ()
pprint.pprint(printers)
print()
 
printer = conn.getDefault()
print("Default1:", printer)
 
if printer == None:
    printer = list(printers.keys())[0]
    print("Default2:", printer)
 
myfile = "./PdfGen.pdf"
pid = conn.printFile(printer, myfile, "test", {})
while conn.getJobs().get(pid, None) is not None:
    time.sleep(1)
#done
