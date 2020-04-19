from tkinter import Frame, Text, Scrollbar
from tkinter import GROOVE
import tkinter.ttk as ttk


class TextWidgetContainer(Frame):

    def __init__(self, window, sizes, font):
        super().__init__(window, width=sizes[0], height=sizes[1], borderwidth=5, relief=GROOVE)
        self.window = window
        self.font = font
        self.buttons = None
        self.num_of_buttons = 0

    def add_buttons(self, buttons):
        self.buttons = buttons
        self.num_of_buttons = len(buttons)

    def show(self, row, column, columnspan=1, indent_x=0, indent_y=0):
        self.grid_propagate(False)
        self.grid(row=row, column=column, columnspan=columnspan, padx=indent_x, pady=indent_y)

        if self.buttons is not None:
            self.grid_rowconfigure(row + 1, weight=1)

            for i in range(len(self.buttons)):
                self.grid_columnconfigure(column + i, weight=1)
        else:
            self.grid_rowconfigure(row, weight=1)
            self.grid_columnconfigure(column, weight=1)


class ScrolledTextWidget(Text):
    def __init__(self, parent_widget, sizes):
        self.parent_widget = parent_widget
        self.text_scrollbar = Scrollbar(parent_widget, orient="vertical", command=self.yview)
        super().__init__(parent_widget, width=sizes[0], height=sizes[1], borderwidth=1, relief=GROOVE,
                         font=parent_widget.font, tabs=40, undo=True)
        self.edit_modified(False)

    def show(self, row, column):
        disp = 0
        if self.parent_widget.num_of_buttons == 0:
            columnspan = 1
            rowspan = 1
        else:
            rowspan = 2
            columnspan = self.parent_widget.num_of_buttons + 1
            disp = 1

        for i in range(self.parent_widget.num_of_buttons):
            self.parent_widget.buttons[i].grid(row=0, column=column + i, sticky="we")

        self.grid(row=row + disp, column=column, columnspan=columnspan)
        self.text_scrollbar.grid(row=row, column=(column + columnspan), rowspan=rowspan, sticky='ns')
        self.config(yscrollcommand=self.text_scrollbar.set)
