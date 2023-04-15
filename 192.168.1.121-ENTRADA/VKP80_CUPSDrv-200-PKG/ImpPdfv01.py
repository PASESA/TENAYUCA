#!/usr/bin/python3
import time, pprint, cups
 
conn = cups.Connection()
printers = conn.getPrinters ()
pprint.pprint(printers)
print()
 
printer = conn.getDefault()
print("Default1:", printer)
 
if printer == None:
    printer = list(printers.keys())[0]
    print("Default2:", printer)
#myfile = "./qq.txt" 
myfile = "./PdfGen.pdf"
pid = conn.printFile(printer, myfile, "test", {})
while conn.getJobs().get(pid, None) is not None:
    time.sleep(1)
#done
