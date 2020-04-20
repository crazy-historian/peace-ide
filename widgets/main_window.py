from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from widgets.common_widgets import ScrolledTextWidget
from pce_processing.pce_file_processing import get_current_time


class UIWindow(Tk):
    def __init__(self, data_process=None, ini_process=None):
        # tk object
        super().__init__()

        # processing object
        self.data_process = data_process
        self.ini_process = ini_process

        # real-time title
        self.title("PeaceStorm. It is a simple and useful IDE for Peace interpreter.")
        self.changes_in_text_editor = False

        # data from .ini file
        self.font = self.ini_process.get_from_config_file("settings", "font")
        self.font_size = self.ini_process.get_from_config_file("settings", "font_size")

        # text widgets
        self.file_text = ScrolledTextWidget(self, (self.font, self.font_size))
        self.gpss_text = ScrolledTextWidget(self, (self.font, self.font_size))
        self.console = ScrolledTextWidget(self, (self.font, self.font_size))

        # report panel
        self.report_window = None
        self.report_panel = None
        self.num_of_tubs = 0

        # menu widgets
        self.main_menu = Menu(self)
        self.file_menu = Menu(self.main_menu, tearoff=0)
        self.edit_menu = Menu(self.main_menu, tearoff=0)
        self.gpss_menu = Menu(self.main_menu, tearoff=0)

        # text tags
        self.console.tag_config('external_message', background="white", foreground="red")
        self.console.tag_config('successful', background="white", foreground="green")

    def insert_to_console(self, text, source=None, tag=None):
        self.console['state'] = NORMAL
        self.console.insert(END, f"{get_current_time()} [IDE] :: {text}\n", tag)
        if source == "PEACE":
            if self.data_process.stdout:
                self.console.insert(END, f"{get_current_time()} [{source}] :: {self.data_process.stdout}", tag)
                self.data_process.stdout = None
            if self.data_process.stderr:
                self.console.insert(END, f"{get_current_time()} [{source}] :: {self.data_process.stderr}",
                                    'external_message')
                self.data_process.stderr = None
        elif source == "GPSSH" and "ERROR" in self.data_process.stderr:
            self.console.insert(END, f"{get_current_time()} [{source}] {self.data_process.stderr}\n",
                                "external_message")
            self.data_process.stderr = None
        self.console.see(END)
        self.console['state'] = DISABLED

    def insert_separator(self, event):
        if event.char or event.keysym == "Backspace":
            self.file_text.edit_separator()

    def update_title(self, event=None, gpss=False):
        if self.file_text.edit_modified():
            self.title(f"Peace *{self.data_process.pce_full_name}")
        else:
            self.title(f"Peace {self.data_process.pce_full_name}")
        if gpss:
            self.gpss_text['state'] = NORMAL
            self.gpss_text.delete(1.0, END)
            if isinstance(gpss, str):
                self.gpss_text.insert(1.0, gpss)
            self.gpss_text['state'] = DISABLED

    # external commands
    def compile(self, event=None):
        returned_code = self.data_process.compile()
        self.insert_to_console("начало компиляции", source="PEACE")
        if returned_code == 1:
            messagebox.showerror("Error", "There are some problems with file")
        elif returned_code == 2:
            messagebox.showerror("Error", "There are some problems with compilation")
        elif returned_code == -1:
            messagebox.showerror("Error!", "There is no file to compile")
        else:
            self.update_title(gpss=returned_code)
            self.insert_to_console("текущий .pce файл скомпилирован", tag='successful')

    def run_model(self, events=None):
        if self.data_process.run_model() == 0:
            self.insert_to_console("запущен .gpss код", source="GPSSH", tag='successful')
            self.open_report()
        else:
            messagebox.showerror("Error!", "There is not current GPSS file.")

    def file_save(self, event=None):
        if self.data_process.file_save() == 0:
            self.insert_to_console(
                "файл успешно сохранен")
            self.update_title()

    def file_save_as(self):
        if self.data_process.file_save_as() == 0:
            self.insert_to_console(
                "файл сохранен с другим именем")
            self.update_title(gpss=True)

    def file_open(self):
        returned_code = self.data_process.file_open()
        if returned_code != 1:
            self.insert_to_console("открыт новый файл")
            if isinstance(returned_code, str):
                self.update_title(gpss=returned_code)
            else:
                self.update_title(gpss=True)

    def file_close(self):
        self.data_process.file_close()
        if self.data_process.file_close() == 0:
            self.insert_to_console("текущий файл закрыт")
            self.update_title(gpss=True)

    def change_report_status(self):
        self.report_window.destroy()
        self.report_window = None
        self.report_panel = None

    def open_report(self):
        if self.data_process.simulation_report is not None:
            if self.report_window is None:
                self.report_window = Tk()
                self.report_window.title(f"{self.data_process.pce_path} - simulation reports")
                self.report_panel = ttk.Notebook(self.report_window)
            report = ScrolledTextWidget(self.report_panel, (self.font, self.font_size))
            report_text = self.data_process.open_report()
            report.insert(1.0, report_text)
            report['state'] = DISABLED
            self.report_panel.add(report, text=f"[{get_current_time()}]  {self.data_process.common_name}")
            self.report_panel.pack(expand=1, fill='both')
            self.report_window.protocol("WM_DELETE_WINDOW", self.change_report_status)
            self.report_window.mainloop()
        else:
            messagebox.showerror("Error!", "There is no .lis file")

    def copy_to_buffer(self):
        code = self.data_process.copy_to_buffer()
        self.file_text.clipboard_clear()
        self.clipboard_append(code)
        if code:
            self.insert_to_console("GPSS код скопирован в буфер обмена")

    def build_menu(self):
        self.main_menu = Menu(self)
        self.config(menu=self.main_menu)
        # file toolbar
        self.file_menu.add_command(label="New file", command=self.file_close)
        self.file_menu.add_command(label="Open file", command=self.file_open)
        self.file_menu.add_command(label="Close file", command=self.file_close)
        self.file_menu.add_command(label="Save file ", command=self.file_save)
        self.file_menu.add_command(label="Save file as...", command=self.file_save_as)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Compile", command=self.file_save_as)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.close_window)
        self.main_menu.add_cascade(label='File', menu=self.file_menu)
        # edit toolbar
        self.edit_menu.add_command(label="Copy", command=self.copy)
        self.edit_menu.add_command(label="Paste", command=self.paste)
        self.edit_menu.add_command(label="Cut", command=self.cut)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Undo", command=self.undo)
        self.edit_menu.add_command(label="Redo", command=self.redo)
        self.main_menu.add_cascade(label='Edit', menu=self.edit_menu)
        # gpss toolbar
        self.gpss_menu.add_command(label="Copy to buffer", command=self.copy_to_buffer)
        self.gpss_menu.add_command(label="Run model", command=self.run_model)
        self.gpss_menu.add_command(label="Open report", command=self.open_report)
        self.main_menu.add_cascade(label='GPSS', menu=self.gpss_menu)

    def close_window(self):
        answer = messagebox.askyesno("Выход из Peace", "Вы действительно хотите выйти?")
        if answer is True:
            if self.file_text.edit_modified():
                answer = messagebox.askyesnocancel("Выход из Peace", "Сохранить файл перед закрытием?")
                if answer is True:
                    self.file_save()
                elif answer is None:
                    return
                self.destroy()
            else:
                self.destroy()
        else:
            return

    def show(self):
        self.build_menu()
        self.file_text.place(relx=0, rely=0, relw=0.6, relh=0.7)
        self.gpss_text.place(relx=0.6, rely=0, relw=0.4, relh=0.7)
        self.console.place(relx=0, rely=0.7, relw=1, relh=0.3)

    # events in widgets
    def context_file_menu(self, event):
        self.edit_menu.post(event.x_root, event.y_root)

    def context_gpss_menu(self, event):
        self.gpss_menu.post(event.x_root, event.y_root)

    def copy(self):
        self.file_text.clipboard_clear()
        try:
            self.file_text.clipboard_append(self.file_text.selection_get())
        except TclError:
            pass

    def paste(self):
        self.file_text.insert(INSERT, self.file_text.clipboard_get())

    def cut(self):
        self.copy()
        self.file_text.delete("sel.first", "sel.last")

    def undo(self, event=None):
        self.file_text.edit_undo()

    def redo(self, event=None):
        try:
            self.file_text.edit_redo()
        except TclError as error:
            if str(error) == "nothing to redo":
                pass

    def bind_events(self):
        self.file_text.bind("<<Modified>>", self.update_title)
        self.file_text.bind("<Key>", self.insert_separator)
        self.file_text.bind("<Button-3>", self.context_file_menu)
        self.gpss_text.bind("<Button-3>", self.context_gpss_menu)
        self.file_text.bind("<Control-x>", self.redo)
        self.bind("<Control-s>", self.file_save)
        self.bind("<F5>", self.compile)
        self.bind("<F6>", self.run_model)
