import tkinter as tk
import tkinter.font as tkFont
    
app = tk.Tk()

fontStyle = tkFont.Font(family="Lucida Grande", size=20)

labelExample = tk.Label(app, text="20", font=fontStyle)

def increase_label_font():
    fontsize = fontStyle['size']
    labelExample['text'] = fontsize+2
    fontStyle.configure(size=fontsize+2)

def decrease_label_font():
    fontsize = fontStyle['size']
    labelExample['text'] = fontsize-2
    fontStyle.configure(size=fontsize-2)
    
buttonExample1 = tk.Button(app, text="Increase", width=30,
                          command=increase_label_font)
buttonExample2 = tk.Button(app, text="Decrease", width=30,
                          command=decrease_label_font)

buttonExample1.pack(side=tk.LEFT)
buttonExample2.pack(side=tk.LEFT)
labelExample.pack(side=tk.RIGHT)
app.mainloop()
