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
