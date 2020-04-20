from tkinter import Frame, Text, Scrollbar
from tkinter import GROOVE
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.scrolledtext as scrlltxt

class ScrolledTextWidget(scrlltxt.ScrolledText):
    def __init__(self, parent_widget, font):
        super().__init__(master=parent_widget, borderwidth=5, relief=GROOVE)
        self['font'] = font
        self.frame['padx'] = 5
        self.frame['pady'] = 5
        self.edit_modified(False)

    def show(self, relx, rely, relw, relh):
        self.place(relx=relx, rely=rely, relwidth=relw, relheight=relh)

if __name__ == "__main__":
    win = tk.Tk()

    text = ScrolledTextWidget(win, ("Consolas", 18))
    text.show(0, 0, 1, 1)
    # text.place(relx=0, rely=0, relwidth=0.6, relheight=0.7)
    # text2.place(relx=0.6, rely=0, relwidth=0.4, relheight=0.7)
    # text3.place(relx=0.0, rely=0.7, relwidth=1.0, relheight=0.3)
    win.geometry("800x600")
    win.mainloop()
