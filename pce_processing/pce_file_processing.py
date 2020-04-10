import os
import subprocess
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, filedialog
from tkinter import END


def get_current_time():
    return datetime.now().strftime("%d-%m-%Y %H:%M")


class PceFileProcessing:
    # FixMe: суперконструктор с параметрами
    def __init__(self, ini_process=None, text_editor=None):

        self.ini_process = ini_process
        self.text_editor = text_editor

        self.peace_interpreter_path = self.ini_process.get_from_config_file("settings", "peace_core_path")
        self.gpssh_interpreter_path = self.ini_process.get_from_config_file("settings", "gpssh_path")

        self.pce_full_name = None
        self.title = self.pce_full_name
        self.pce_path = None
        self.common_name = None
        self.gpss_code = None
        self.simulation_report = None
        self.current_time = None
        self.changes = False
        self.stdout = None
        self.stderr = None

    def file_save(self):
        code = self.text_editor.get(1.0, END)
        self.changes = False
        if self.pce_full_name:
            file = open(self.pce_full_name, 'w+')
            file.write(code)
            file.close()
            return 0
        else:
            file_name = filedialog.asksaveasfilename(title="Сохранение файла с pce-кодом", defaultextension=".pce")
            if file_name is None:
                return 1
            file = open(file_name, 'w+')
            file.write(code)
            self.update_file_info(file_name)
            return 0

    def file_save_as(self):
        self.update_file_info()
        return self.file_save()

    def file_open(self):
        if self.file_close() <= 0:
            file_name = filedialog.askopenfilename(filetypes=[('Peace-code files', '.pce')])
            if file_name:
                file = open(file_name, 'r')
                self.text_editor.insert(1.0, file.read())
                file.close()
                self.update_file_info(file_name)
                return 0
            else:
                return 1

    def file_close(self):
        if self.pce_full_name:
            answer = messagebox.askyesnocancel("Закрытие .pce файла", "Сохранить текущий файл перед закрытием?")
            if answer is True:
                self.file_save()
            elif answer is None:
                return 1
            self.text_editor.delete(1.0, END)
            self.update_file_info()
            return 0
        return -1

    def update_file_info(self, new_file=None):
        self.changes = False
        if not new_file:
            self.pce_full_name = None
            self.pce_path = None
            self.common_name = None
            self.gpss_code = None
            self.simulation_report = None
        else:
            self.pce_full_name = new_file
            file_path = new_file.split('/')
            self.pce_path = '/'.join(file_path[:-1])
            self.common_name = file_path[-1].split('.')[0]

    def get_new_file_name(self, extension):
        temp_short = ".".join((self.common_name, extension))
        new_file_name = "/".join((self.pce_path, temp_short))
        return new_file_name

    def execute_external_command(self, command, *parameters):
        argument_list = [command]
        argument_list.extend(parameters)
        command_call = subprocess.run(argument_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                      text=True)
        self.stdout = command_call.stdout
        self.stderr = command_call.stderr
        return command_call.returncode

    def compile(self):
        if self.peace_interpreter_path == "None" or not os.path.isfile(self.peace_interpreter_path):
            self.peace_interpreter_path = os.path.normpath(filedialog.askopenfilename())
            self.ini_process.insert_to_config_file("settings", "peace_core_path", self.peace_interpreter_path)

        if self.pce_full_name:
            self.file_save()
            ret_code = self.execute_external_command(
                "python", self.peace_interpreter_path, self.pce_full_name)

            if ret_code != 0:
                return ret_code
            else:
                self.gpss_code = os.path.normpath(self.get_new_file_name("gpss"))
                code = open(self.gpss_code, 'r').read()
                return code
        else:
            return -1

    def run_model(self):
        if self.gpssh_interpreter_path == "None" or os.path.isfile(self.gpssh_interpreter_path):
            self.gpssh_interpreter_path = os.path.normpath(
                filedialog.askopenfilename(initialdir=".", title="Выбор gpssh.exe файла", defaultextension=".exe"))
            self.ini_process.insert_to_config_file("settings", "gpssh_path", self.gpssh_interpreter_path)

        if self.gpss_code:
            self.execute_external_command(self.gpssh_interpreter_path, self.gpss_code)
            self.simulation_report = self.get_new_file_name("lis")
            return 0
        else:
            return 1

    def copy_to_buffer(self):
        return open(self.gpss_code, "r").read()

    def open_report(self):
        file = open(self.simulation_report, "r")
        report_text = file.read()
        file.close()
        return report_text
