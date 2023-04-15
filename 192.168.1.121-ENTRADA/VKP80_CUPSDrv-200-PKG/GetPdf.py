from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
page_width = 250
page_height = 400
canvas = canvas.Canvas("PdfGen.pdf", pagesize=(page_width, page_height)) 
#canvas = canvas.Canvas("PdfGen.pdf", pagesize=letter)
canvas.setLineWidth(.3)
canvas.setFont('Helvetica', 12)

canvas.drawString(30,360,'CARTA DE PRUEBA')
canvas.line(30,359,200,359)
canvas.drawString(30,345,'SABADO')
canvas.drawString(50,330,"24/10/2020")
canvas.drawString(30,315,'Aurelio Guarneros  inteligente:')
canvas.drawString(30,300,"<NOMBRE>")
#canvas.create_image(30, 300, image=oso.jpg, anchor="nw")
canvas.drawString(30,285,'ETIQUETA:')
canvas.drawString(30,270,"<ASUNTO DE LA CARTA >")
canvas.line(30,265,200,265)
# Dibujamos una imagen (IMAGEN, X,Y, WIDTH, HEIGH)
canvas.drawImage('oso.jpg', 50, 200, 60, 60)
canvas.line(30,195,200,195)
canvas.drawImage('qr.png', 50, 130, 60, 60)
canvas.line(30,129,200,129)
print("se genero el archivo PdfGen.pdf")
canvas.save()
