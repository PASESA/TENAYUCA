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
page_width = 185
page_height = 200
canvas = canvas.Canvas("PdfGen.pdf", pagesize=(page_width, page_height)) 
#canvas = canvas.Canvas("PdfGen.pdf", pagesize=letter)
canvas.setLineWidth(.3)
canvas.setFont('Helvetica', 12)
canvas.drawString(50,190,'Boleto de Entrada')
canvas.line(30,185,200,185)
# Dibujamos una imagen (IMAGEN, X,Y, WIDTH, HEIGH)
canvas.drawImage('LOGO.jpg', 20, 120, 60, 60)
canvas.setFont('Helvetica', 8)
canvas.drawString(80,170,"PASE S.A DE C.V.")
canvas.drawString(80,160,"R.F.C PAS-780209-I24")
canvas.drawString(80,150,"Paseo de la Reforma 300-05")
canvas.drawString(80,140,"Col Juarez 06600")
canvas.drawString(80,130,"Alcaldia Cuauhtemoc")
canvas.drawString(80,120,"CDMX 5525-0108")

canvas.setFont('Helvetica', 12)
canvas.drawString(30,105,"Entro:")
fechasindeci=(fSTR[:19])
print(fechasindeci)
canvas.drawString(70,105,fechasindeci)
canvas.drawString(30,93,"Folio")
canvas.drawString(30,81,'Placas')
# Dibujamos una imagen (IMAGEN, X,Y, WIDTH, HEIGH)
canvas.drawImage('qr.png', 20, 20, 60, 60)
canvas.setFont('Helvetica', 8)
canvas.drawString(80,65,"Suc. Tenayuca M laurent 961")
canvas.drawString(80,55,'Col Sta Cruz Atoyac 03310')
canvas.drawString(80,45,'Delegacion Benito Juarez ')
canvas.line(30,19,200,19)
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
