from tkinter import GROOVE
from enum import Enum
import tkinter.scrolledtext as scrlltxt


class ScrolledTextWidget(scrlltxt.ScrolledText):
    def __init__(self, parent_widget, font):
        super().__init__(master=parent_widget, borderwidth=2, relief=GROOVE)
        self['undo'] = True
        self['font'] = font
        self.frame['padx'] = 5
        self.frame['pady'] = 5
        self.edit_modified(False)

    def show(self, relx, rely, relw, relh):
        self.place(relx=relx, rely=rely, relwidth=relw, relheight=relh)

    def change_color(self, color_theme):
        self.frame.configure(background=color_theme.widget_background.value)
        self.configure(background=color_theme.text_background_color.value)
        self.configure(foreground=color_theme.code_color.value)
        self.configure(selectbackground=color_theme.selection_color.value)
        self.configure(insertbackground=color_theme.code_color.value)


class DefaultColorTheme(Enum):
    code_color = '#2E3440'
    console_color = '#2E3440'
    error_color = 'red'
    success_color = 'green'
    text_background_color = '#ECEFF4'
    widget_background = '#ECEFF4'
    selection_color = '#5E81AC'


class DarkColorTheme(Enum):
    code_color = '#D8DEE9'
    console_color = '#88C0D0'
    error_color = '#BF616A'
    success_color = '#A3BE8C'
    text_background_color = '#2E3440'
    widget_background = '#2E3440'
    selection_color = '#4C566A'
