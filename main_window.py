import os
import subprocess
import datetime
from tkinter import *
from tkinter import filedialog, messagebox
from widgets.common_widgets import TextWidgetContainer, ScrolledTextWidget
from settings.ini_processing import IniProcessing
from pce_processing.pce_file_processing import PceFileProcessing, get_current_time


class UIWindow(Tk):

    def __init__(self, data_process=None, ini_process=None):
        # main window object
        super().__init__()
        self.data_process = data_process
        self.ini_process = ini_process
        self.title("Peace. It is a simple and useful IDE for Peace interpreter.")
        self.changes_in_text_editor = False

        # data from .ini file
        self.font = self.ini_process.get_from_config_file("settings", "font")
        self.font_size = self.ini_process.get_from_config_file("settings", "font_size")

        # widgets sizes
        self.indent = 5
        self.editor_size = [0, 0]
        self.info_size = [0, 0]
        self.window_width = 0
        self.window_height = 0
        self.correct_window_size()

        # containers for widgets
        self.editor_container = TextWidgetContainer(self, self.editor_size, (self.font, self.font_size))
        self.gpss_container = TextWidgetContainer(self, self.editor_size, (self.font, self.font_size))
        self.info_container = TextWidgetContainer(self, self.info_size, (self.font, self.font_size))

        # widgets
        self.text_editor = ScrolledTextWidget(self.editor_container, self.editor_size)
        self.gpss_text = ScrolledTextWidget(self.gpss_container, self.editor_size)
        self.console = ScrolledTextWidget(self.info_container, self.editor_size)

        # buttons
        self.save_button = Button(self.editor_container, text="Save file", command=self.file_save)
        self.compile_button = Button(self.editor_container, text="Compile", command=self.compile)
        self.copy_button = Button(self.gpss_container, text="Copy to buffer", command=self.copy_to_buffer)
        self.run_button = Button(self.gpss_container, text="Run model", command=self.run_model)
        self.open_report_button = Button(self.gpss_container, text="Open review", command=self.open_report)

        # menu widgets
        self.main_menu = Menu(self)
        self.file_menu = Menu(self.main_menu, tearoff=0)

    def correct_window_size(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        self.window_width = round(screen_width // 2)
        self.window_height = round(screen_height * (2 / 3))

        self.editor_size[0] = round((self.window_width - self.indent * 4) // 2)
        self.editor_size[1] = round((self.window_height - self.indent * 5) * (2 / 3))

        self.info_size[0] = self.editor_size[0] * 2 + self.indent * 2
        self.info_size[1] = self.window_height - self.editor_size[1]

    def insert_to_console(self, text, stdout=False, stderr=False):
        self.console['state'] = NORMAL
        self.console['foreground'] = "red"
        self.console.insert(END, f"{get_current_time()} {text}\n")
        if stdout:
            self.console.insert(END, f"{get_current_time()} {self.data_process.stdout}\n")
            self.data_process.stdout = None
        if stderr:
            self.console.insert(END, f"{get_current_time()} {self.data_process.stderr}\n")
            self.data_process.stderr = None
        self.console['foreground'] = "black"
        self.console['state'] = DISABLED

    def update_title(self):
        if self.changes_in_text_editor:
            self.title(f"Peace *{self.data_process.pce_full_name}")
        else:
            self.title(f"Peace {self.data_process.pce_full_name}")

    # event processing
    def compile(self):
        ret_code = self.data_process.compile()
        if ret_code == 1:
            messagebox.showerror("Error", "There are some problems with file")
        elif ret_code == 2:
            messagebox.showerror("Error", "There are some problems with compilation")
        elif ret_code == -1:
            messagebox.showerror("Error!", "There is no file to compile")
        else:
            self.gpss_text['state'] = NORMAL
            self.gpss_text.delete(1.0, END)
            self.gpss_text.insert(1.0, ret_code)
            self.gpss_text['state'] = DISABLED
            self.insert_to_console(" - текущий .pce файл скомпилирован", stdout=True, stderr=True)

    def run_model(self):
        if self.data_process.run_model() == 0:
            self.insert_to_console(" -- запущен .gpss код", stdout=True, stderr=True)
            self.open_report()
        else:
            messagebox.showerror("Error!", "There is not current GPSS file.")

    def file_save(self):
        if self.data_process.file_save() == 0:
            self.insert_to_console(
                " - файл успешно сохранен")
            self.changes_in_text_editor = False
            self.update_title()

    def file_save_as(self):
        if self.data_process.file_save() == 0:
            self.insert_to_console(
                " - файл сохранен с другим именем")
            self.changes_in_text_editor = False
            self.update_title()

    def file_open(self):
        self.changes_in_text_editor = False
        if self.data_process.file_open() == 0:
            self.insert_to_console(" - открыт новый файл")
            self.changes_in_text_editor = False
            self.update_title()

    def file_close(self):
        if self.data_process.file_close() == 0:
            self.insert_to_console(" - текущий файл закрыт")
            self.changes_in_text_editor = False
            self.update_title()

    def open_report(self):
        if self.data_process.simulation_report is not None:
            sub_window = Tk()
            sub_window_parameters = "{}x{}+100+100".format(self.window_width, self.window_height + self.indent * 2)
            sub_window.geometry(sub_window_parameters)
            sub_window.title(f"Simulation report {self.data_process.simulation_report}")

            review_container = TextWidgetContainer(sub_window,
                                                   (self.window_width, self.window_height + self.indent * 2),
                                                   (self.font, self.font_size))

            review_container.show(row=0, column=0, indent_x=self.indent)
            review_widget = ScrolledTextWidget(review_container,
                                               (self.window_width, self.window_height + self.indent * 2))
            review_widget.show(row=0, column=0)

            report_text = self.data_process.open_report()
            review_widget.insert(1.0, report_text)
            review_widget['state'] = DISABLED
            sub_window.mainloop()
        else:
            messagebox.showerror("Error!", "There is not .lis file")

    def copy_to_buffer(self):
        code = self.data_process.copy_to_buffer()
        self.clipboard_append(code)
        self.insert_to_console(" - GPSS код скопирован в буфер обмена")

    def build_menu(self):
        self.main_menu = Menu(self)
        self.config(menu=self.main_menu)
        # file toolbar
        self.file_menu.add_command(label="New file", command=self.file_close)
        self.file_menu.add_command(label="Open...", command=self.file_open)
        self.file_menu.add_command(label="Close...", command=self.file_close)
        self.file_menu.add_command(label="Save...", command=self.file_save)
        self.file_menu.add_command(label="Save as...", command=self.file_save_as)
        self.file_menu.add_command(label="Exit", command=self.close_window)
        self.main_menu.add_cascade(label='File', menu=self.file_menu)

    def close_window(self):
        answer = messagebox.askyesnocancel("Выход из Peace", "Вы действительно хотите выйти?")
        if answer is True:
            answer = messagebox.askyesnocancel("Выход из Peace", "Сохранить файл перед закрытием?")
            if answer is True:
                self.file_save()
            elif answer is None:
                return
            self.destroy()
        else:
            return

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
        self.console.show(row=2, column=0)

    def pack(self):
        self.build_menu()
        self.show_text_editor()
        self.show_gpss_label()
        self.show_compile_info()

    # events in widgets
    def search_for_update(self, event):
        self.changes_in_text_editor = True
        self.update_title()


if __name__ == "__main__":

    ini_process = IniProcessing(path="settings.ini")
    window = UIWindow(ini_process=ini_process)
    data_process = PceFileProcessing(ini_process=ini_process, text_editor=window.text_editor)

    window.ini_process = ini_process
    window.data_process = data_process

    window.geometry("{}x{}+100+100".format(window.window_width, window.window_height + window.indent * 2))
    window.resizable(False, False)
    window.pack()

    window.text_editor.bind("<Key>", window.search_for_update)
    window.protocol("WM_DELETE_WINDOW", window.close_window)
    window.mainloop()
