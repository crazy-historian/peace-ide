import os
import subprocess
import datetime
from tkinter import *
from tkinter import filedialog, messagebox
from widgets.common_widgets import TextWidgetContainer, ScrolledTextWidget
from settings.ini_processing import IniProcessing


class UIWindow(Tk):

    def __init__(self):
        # main window object
        super().__init__()
        self.title("Peace. It is a STST for GPSS code.")
        self.changes_in_file = False

        # data from .ini file
        self.settings_file = IniProcessing(path=f"{os.getcwd()}\\settings.ini")
        self.font = self.settings_file.get_from_config_file("settings", "font")
        self.font_size = self.settings_file.get_from_config_file("settings", "font_size")
        self.gpss_interpreter = self.settings_file.get_from_config_file("settings", "gpssh_path")
        self.peace_interpreter = self.settings_file.get_from_config_file("settings", "peace_core_path")

        # widgets sizes
        self.indent = 5
        self.editor_size = [0, 0]
        self.info_size = [0, 0]
        self.window_width = 0
        self.window_height = 0
        self.correct_window_size()

        # current file
        self.pygpss_full_file_name = None
        self.pygpss_file_path = None
        self.common_file_name = None
        self.gpss_file = None
        self.report_file = None
        self.current_time = None

        # containers for widgets
        self.editor_container = TextWidgetContainer(self, self.editor_size, (self.font, self.font_size))
        self.gpss_container = TextWidgetContainer(self, self.editor_size, (self.font, self.font_size))
        self.info_container = TextWidgetContainer(self, self.info_size, (self.font, self.font_size))

        # widgets
        self.text_editor = ScrolledTextWidget(self.editor_container, self.editor_size)
        self.gpss_text = ScrolledTextWidget(self.gpss_container, self.editor_size)
        self.info_text = ScrolledTextWidget(self.info_container, self.editor_size)

        # buttons
        self.save_button = Button(self.editor_container, text="Save file", command=self.file_save)
        self.compile_button = Button(self.editor_container, text="Compile", command=self.compile)
        self.copy_button = Button(self.gpss_container, text="Copy to buffer", command=self.copy_to_buffer)
        self.run_button = Button(self.gpss_container, text="Run model", command=self.run_model)
        self.open_report_button = Button(self.gpss_container, text="Open review", command=self.open_report)

        # menu widgets

    def correct_window_size(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        self.window_width = round(screen_width // 2)
        self.window_height = round(screen_height * (2 / 3))

        self.editor_size[0] = round((self.window_width - self.indent * 4) // 2)
        self.editor_size[1] = round((self.window_height - self.indent * 5) * (2 / 3))

        self.info_size[0] = self.editor_size[0] * 2 + self.indent * 2
        self.info_size[1] = self.window_height - self.editor_size[1]

    def get_current_time(self):
        self.current_time = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")

    def update_title(self, text):
        if self.changes_in_file:
            self.title(f"Peace *{text}")
        else:
            self.title(f"Peace {text}")

    def insert_to_info_text(self, text):
        self.get_current_time()
        self.info_text['state'] = NORMAL
        self.info_text['foreground'] = "red"
        self.info_text.insert(END, self.current_time + text + '\n')
        self.info_text['foreground'] = "black"
        self.info_text['state'] = DISABLED

    def execute_external_command(self, command, *parameters):
        argument_list = [command]
        argument_list.extend(parameters)
        command_call = subprocess.run(argument_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                      text=True)
        self.insert_to_info_text(command_call.stderr)
        self.insert_to_info_text(command_call.stdout)
        return command_call.returncode

    def update_file_info(self, new_file=None):
        self.changes_in_file = False
        if not new_file:
            self.update_title("No file")
            self.pygpss_full_file_name = None
            self.pygpss_file_path = None
            self.common_file_name = None
            self.gpss_file = None
            self.report_file = None
        else:
            self.update_title(new_file)
            self.pygpss_full_file_name = new_file
            file_path = new_file.split('/')
            self.pygpss_file_path = '/'.join(file_path[:-1])
            self.common_file_name = file_path[-1].split('.')[0]

        self.gpss_text['state'] = NORMAL
        self.gpss_text.delete(1.0, END)
        self.gpss_text['state'] = DISABLED

    def get_new_file_name(self, extension):
        temp_short = ".".join((self.common_file_name, extension))
        new_file_name = "/".join((self.pygpss_file_path, temp_short))
        return new_file_name

    def build_menu(self):
        self.main_menu = Menu(self)
        self.config(menu=self.main_menu)
        # file toolbar
        self.file_menu = Menu(self.main_menu, tearoff=0)
        self.file_menu.add_command(label="New file", command=self.file_close)
        self.file_menu.add_command(label="Open...", command=self.file_open)
        self.file_menu.add_command(label="Close...", command=self.file_close)
        self.file_menu.add_command(label="Save...", command=self.file_save)
        self.file_menu.add_command(label="Save as...", command=self.file_save_as)
        self.file_menu.add_command(label="Exit", command=self.close_window)
        self.main_menu.add_cascade(label='File', menu=self.file_menu)

    def close_window(self):
        answer = messagebox.askyesnocancel("Выход из PyGPSS", "Вы действительно хотите выйти?")
        if answer is True:
            answer = messagebox.askyesnocancel("Выход из PyGPSS", "Сохранить файл перед закрытием?")
            if answer is True:
                self.file_save()
            elif answer is None:
                return
            self.destroy()
        else:
            return

    def compile(self):
        if self.peace_interpreter == "None":
            self.peace_interpreter = os.path.normpath(filedialog.askopenfilename())
            self.settings_file.insert_to_config_file("settings", "peace_core_path", self.peace_interpreter)

        if self.pygpss_full_file_name:
            self.file_save()
            self.gpss_text['state'] = NORMAL

            return_code = self.execute_external_command(
                "python", "D:/Python training/pyss/src/main.py", self.pygpss_full_file_name)
            if return_code == 1:
                messagebox.showerror("Error", "There are some problems with file")
                return
            elif return_code == 2:
                messagebox.showerror("Error", "There are some problems with compilation")
                return

            self.gpss_file = os.path.normpath(self.get_new_file_name("gpss"))
            code = open(self.gpss_file, 'r').read()
            self.gpss_text.delete(1.0, END)
            self.gpss_text.insert(1.0, code)
            self.gpss_text['state'] = DISABLED
            self.insert_to_info_text(" - текущий файл скомпилирован")
        else:
            messagebox.showerror("Error!", "There is no file to compile")

    def file_save(self):
        # TODO: correct file and file name with example? https://younglinux.info/tkinter/dialogbox.php
        code = self.text_editor.get(1.0, END)
        self.changes_in_file = False
        if self.pygpss_full_file_name:
            pygpss_file = open(self.pygpss_full_file_name, 'w+')
            self.insert_to_info_text(" - текущий файл успешно сохранен")
            pygpss_file.write(code)
            pygpss_file.close()
        else:
            full_file_name = filedialog.asksaveasfilename(defaultextension=".pce")
            if full_file_name is None:
                return
            pygpss_file = open(full_file_name, 'w+')
            pygpss_file.write(code)
            self.update_file_info(full_file_name)
            self.insert_to_info_text(
                " - новый файл c именем '{}' создан и успешно сохранен".format(self.pygpss_full_file_name))
        self.update_title(self.pygpss_full_file_name)

    def file_save_as(self):
        self.update_file_info()
        self.file_save()

    def file_open(self):
        self.file_close()
        file_name = filedialog.askopenfilename(filetypes=[('PyGPSS files', '.pce')])
        if file_name:
            pygpss_file = open(file_name, 'r')
            self.text_editor.insert(1.0, pygpss_file.read())
            pygpss_file.close()
            self.update_file_info(file_name)
            self.insert_to_info_text(" - открыт новый файл с именем '{}'".format(file_name))
        else:
            return

    def file_close(self):
        if self.pygpss_full_file_name:
            answer = messagebox.askyesnocancel("Открыть новый файл", "Сохранить текущий файл перед закрытием?")
            if answer is True:
                self.file_save()
            elif answer is None:
                return
            self.text_editor.delete(1.0, END)
            self.insert_to_info_text(" - текущий файл был закрыт")
            self.update_file_info()

    def run_model(self):
        if self.gpss_interpreter == "None":
            self.gpss_interpreter = os.path.normpath(filedialog.askopenfilename(initialdir=".", title="Select file"))
            self.settings_file.insert_to_config_file("settings", "gpssh_path", self.gpss_interpreter)

        if self.gpss_file:
            self.insert_to_info_text(" - запуск интерпретатора")
            self.execute_external_command(self.gpss_interpreter, self.gpss_file)
            self.report_file = self.get_new_file_name("lis")
            self.open_report()
        else:
            messagebox.showerror("Error!", "There is not current GPSS file.")

    def copy_to_buffer(self):
        gpss_code = self.gpss_text.get(1.0, END)
        self.clipboard_append(gpss_code)
        self.insert_to_info_text(" - GPSS-код скопирован в буфер обмена")

    def open_report(self):
        if self.report_file is not None:
            sub_window = Tk()
            sub_window_parameters = "{}x{}+100+100".format(self.window_width, self.window_height + self.indent * 2)
            sub_window.geometry(sub_window_parameters)

            review_container = TextWidgetContainer(sub_window,
                                                   (self.window_width, self.window_height + self.indent * 2),
                                                   (self.font, self.font_size))
            review_container.show(row=0, column=0, indent_x=self.indent)
            review_widget = ScrolledTextWidget(review_container,
                                               (self.window_width, self.window_height + self.indent * 2))
            review_widget.show(row=0, column=0)

            lis_file = open(self.report_file, "r")
            review_widget.insert(1.0, lis_file.read())

            review_widget['state'] = DISABLED
            lis_file.close()
            sub_window.mainloop()
        else:
            messagebox.showerror("Error!", "There is not .lis file")

    def show_text_editor(self):
        # text editor
        self.editor_container.add_buttons([self.compile_button, self.save_button])
        self.editor_container.show(row=0, column=0, indent_x=self.indent)
        self.text_editor.show(row=0, column=0)

    def show_gpss_label(self):
        # gpss code
        self.gpss_container.add_buttons([self.run_button, self.copy_button, self.open_report_button])
        self.gpss_container.show(row=0, column=3, indent_x=self.indent)
        self.gpss_text.show(row=0, column=3)

    def show_compile_info(self):
        self.info_container.show(row=2, column=0, indent_x=self.indent, indent_y=self.indent, columnspan=6)
        self.info_text.show(row=2, column=0)

    def pack(self):
        self.build_menu()
        self.show_text_editor()
        self.show_gpss_label()
        self.show_compile_info()

    # events in widgets
    def search_for_update(self, event):
        self.changes_in_file = True
        self.update_title(self.pygpss_full_file_name)


if __name__ == "__main__":
    window = UIWindow()
    window.geometry("{}x{}+100+100".format(window.window_width, window.window_height + window.indent * 2))
    window.resizable(False, False)
    window.pack()

    window.text_editor.bind("<Key>", window.search_for_update)
    window.protocol("WM_DELETE_WINDOW", window.close_window)
    window.mainloop()
