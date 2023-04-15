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
page_width = 160
page_height = 160
canvas = canvas.Canvas("PdfGen.pdf", pagesize=(page_width, page_height)) 
canvas.setLineWidth(.3)
canvas.drawImage('LOGO.jpg', 80, 115, 40, 40)
canvas.setFont('Helvetica', 8)
canvas.drawString(70,110,"PASE S.A DE C.V.")
canvas.setFont('Helvetica', 6)
canvas.drawString(70,100,"R.F.C PAS-780209-I24")
canvas.drawString(70,90,"Paseo de la Reforma 300-05")
canvas.drawString(70,80,"Colonia Juarez CP 06600")
canvas.drawString(70,70,"Alcaldia Cuauhtemoc")
canvas.drawString(70,60,"CDMX 55-25-01-08")
canvas.drawString(70,50,"Suc Tenayuca M laurent 961")
canvas.drawString(70,40,'Col Sta Cruz Atoyac 03310')
canvas.drawString(70,30,'Delegacion Benito Juarez ')
canvas.drawImage('qr.png', 0, 45, 70, 70)
canvas.setFont('Helvetica', 8)
fechasindeci=(fSTR[:19])
print(fechasindeci)
canvas.setFont('Helvetica', 8)
canvas.drawString(20,18,"Entro:")
canvas.drawString(45,18,fechasindeci)
canvas.setFont('Helvetica', 9)
canvas.drawString(20,8,"Folio:")
canvas.drawString(20,0,'Placas:')
canvas.line(20,-5,200,-5)
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
