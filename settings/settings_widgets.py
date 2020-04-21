from tkinter import Tk
from tkinter import filedialog
from os.path import isfile
import tkinter as tk
import tkinter.ttk as ttk


class SettingsWindow(Tk):
    def __init__(self, ini_file, apply_callback):
        super().__init__()
        self.title("Settings")
        self.apply_changes = apply_callback
        self.ini_file = ini_file
        self.peace_path_label = tk.Label(self, text="Путь до Peace:")
        self.gpss_path_label = tk.Label(self, text="Путь до gpssh.exe:")
        self.font_size_label = tk.Label(self, text="Размер шрифта:")

        self.peace_path_entry = tk.Entry(self)
        self.gpss_path_entry = tk.Entry(self)
        self.font_size_combobox = ttk.Combobox(self, values=[str(i) for i in range(8, 23)])
        self.font_size_combobox.insert(0, "14")
        self.peace_path_button = tk.Button(self, text="...",
                                           command=lambda widget=self.peace_path_entry, name="peace_core_path":
                                           self.choose_file(widget, name))
        self.gpss_path_button = tk.Button(self, text="...",
                                          command=lambda widget=self.gpss_path_entry, name="gpss_path":
                                          self.choose_file(widget, name))
        self.font_size_button = tk.Button(self, text="Apply changes", command=self.apply)

    def show(self):
        self.peace_path_label.place(x=10, y=10, height=15, width=100)
        self.gpss_path_label.place(x=10, y=40, height=15, width=120)
        self.font_size_label.place(x=10, y=70, height=15, width=111)

        self.peace_path_entry.place(x=150, y=10, height=15, width=350)
        self.peace_path_entry.insert(0, self.ini_file.get_from_config_file("settings", "peace_core_path"))
        self.gpss_path_entry.place(x=150, y=40, height=15, width=350)
        self.gpss_path_entry.insert(0, self.ini_file.get_from_config_file("settings", "gpssh_path"))
        self.font_size_combobox.place(x=150, y=70, height=20, width=40)

        self.peace_path_button.place(x=505, y=10, height=15, width=15)
        self.gpss_path_button.place(x=505, y=40, height=15, width=15)
        self.font_size_button.place(x=200, y=70, height=20, width=100)

        self.geometry("550x100+600+400")
        self.resizable(False, False)
        self.mainloop()

    def choose_file(self, entry, setting_name):
        file_name = filedialog.askopenfilename(title="Открытие")
        entry.delete(0, tk.END)
        if isfile(file_name):
            entry.insert(0, file_name)
            self.ini_file.insert_to_config_file("settings", setting_name, file_name)
            entry['background'] = '#7CFC00'
        else:
            entry['background'] = '#8B0000'
        self.deiconify()
        self.grab_set()

    def apply(self):
        number = self.font_size_combobox.get()
        self.ini_file.insert_to_config_file("settings", "font_size", number)
        self.apply_changes()


