from tkinter import Tk
from tkinter import filedialog, messagebox
from os.path import isfile
import tkinter as tk
import tkinter.ttk as ttk


class SettingsWindow(Tk):
    def __init__(self, ini_file, apply_callback):
        super().__init__()
        self.title("Settings")
        self.apply_changes = apply_callback
        self.ini_file = ini_file
        self.font_size = self.ini_file.get_from_config_file("settings", "font_size")

        self.peace_path_label = tk.Label(self, text="Путь до Peace:")
        self.gpss_path_label = tk.Label(self, text="Путь до gpssh.exe:")
        self.font_size_label = tk.Label(self, text="Размер шрифта:")

        self.peace_path_entry = tk.Entry(self)
        self.gpss_path_entry = tk.Entry(self)
        self.font_size_scale = tk.Scale(self, from_=8, to=24, resolution=1, orient=tk.HORIZONTAL,
                                        command=self.on_scale)

        self.peace_path_button = tk.Button(self, text="...",
                                           command=lambda widget=self.peace_path_entry, name="peace_core_path":
                                           self.choose_file(widget, name))
        self.gpss_path_button = tk.Button(self, text="...",
                                          command=lambda widget=self.gpss_path_entry, name="gpss_path":
                                          self.choose_file(widget, name))
        self.font_size_button = tk.Button(self, text="Apply changes", command=self.apply)

    def on_scale(self, value):
        self.font_size = value

    def configure_color_theme(self, color_theme):
        self.configure(background=color_theme.widget_background.value)
        for widget in (self.peace_path_label, self.peace_path_entry, self.peace_path_button,
                       self.gpss_path_label, self.gpss_path_entry, self.gpss_path_button,
                       self.font_size_label, self.font_size_button, self.font_size_scale):
            widget.configure(background=color_theme.text_background_color.value)
            widget.configure(foreground=color_theme.code_color.value)
        self.font_size_scale.configure(activebackground=color_theme.text_background_color.value)
        self.font_size_scale.configure(troughcolor=color_theme.text_background_color.value)

    def show(self):
        self.peace_path_label.place(x=10, y=10, height=15, width=100)
        self.gpss_path_label.place(x=10, y=40, height=15, width=120)
        self.font_size_label.place(x=10, y=70, height=15, width=111)

        self.peace_path_entry.place(x=150, y=10, height=25, width=350)
        self.peace_path_entry.insert(0, self.ini_file.get_from_config_file("settings", "peace_core_path"))
        self.gpss_path_entry.place(x=150, y=40, height=25, width=350)
        self.gpss_path_entry.delete(0, tk.END)
        self.gpss_path_entry.insert(0, self.ini_file.get_from_config_file("settings", "gpss_path"))

        self.font_size_scale.place(x=150, y=70, height=45, width=350)
        self.font_size_scale.set(self.ini_file.get_from_config_file("settings", "font_size"))

        self.peace_path_button.place(x=505, y=10, height=25, width=25)
        self.gpss_path_button.place(x=505, y=40, height=25, width=25)
        self.font_size_button.place(x=220, y=130, height=35, width=120)

        self.geometry("550x180+600+400")
        self.resizable(False, False)
        self.mainloop()

    def choose_file(self, entry, setting_name):
        file_name = filedialog.askopenfilename(title="Открытие")
        entry.delete(0, tk.END)
        if isfile(file_name):
            entry.insert(0, file_name)
            self.ini_file.insert_to_config_file("settings", setting_name, file_name)
        else:
            entry.insert(0, "No file")

        self.deiconify()
        self.grab_set()

    def apply(self):
        peace_path = self.peace_path_entry.get()
        gpss_path = self.gpss_path_entry.get()
        self.ini_file.insert_to_config_file("settings", "peace_core_path", peace_path)
        self.ini_file.insert_to_config_file("settings", "gpss_path", gpss_path)
        self.ini_file.insert_to_config_file("settings", "font_size", self.font_size)
        self.apply_changes()



