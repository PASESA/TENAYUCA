import ezodf2
from ezodf2 import newdoc, Paragraph, Heading 
odt = newdoc(doctype='odt', filename='doct.odt') 
odt.body += Heading("Capítulo 1") 
odt.body += Paragraph("Este es el principio de la historia.") 
odt.body += Paragraph("aqui va la imagen .") 
odt.body += image_cget('oso.jpg')
odt.save()
