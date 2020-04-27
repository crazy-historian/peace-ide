from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from widgets.common_widgets import ScrolledTextWidget, DefaultColorTheme, DarkColorTheme
from pce_processing.pce_file_processing import get_current_time
from settings.settings_widgets import SettingsWindow


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

        # color_theme
        self.color_theme_enum = DefaultColorTheme
        self.color_theme = "default"

        # data from .ini file
        self.font = self.ini_process.get_from_config_file("settings", "font")
        self.font_size = self.ini_process.get_from_config_file("settings", "font_size")

        # text widgets
        self.file_text = ScrolledTextWidget(self, (self.font, self.font_size))
        self.gpss_text = ScrolledTextWidget(self, (self.font, self.font_size))
        self.gpss_text['state'] = DISABLED
        self.console = ScrolledTextWidget(self, (self.font, self.font_size))
        self.console['state'] = DISABLED

        # sub windows
        self.settings = None
        self.report_window = None
        self.report_panel = None
        self.reports = []
        self.num_of_tubs = 0

        # menu widgets
        self.main_menu = Menu(self)
        self.file_menu = Menu(self.main_menu, tearoff=0)
        self.edit_menu = Menu(self.main_menu, tearoff=0)
        self.run_menu = Menu(self.main_menu, tearoff=0)
        self.gpss_menu = Menu(self.main_menu, tearoff=0)
        self.settings_menu = Menu(self.main_menu, tearoff=0)

    def configure_color_theme(self):
        self.configure(background=self.color_theme_enum.widget_background.value)
        for menu in (self.file_menu, self.edit_menu, self.run_menu, self.gpss_menu, self.settings_menu):
            menu.configure(background=self.color_theme_enum.widget_background.value)
            menu.configure(foreground=self.color_theme_enum.code_color.value)
            menu.configure(activebackground=self.color_theme_enum.selection_color.value)

        for widget in (self.file_text, self.gpss_text, self.console):
            widget.change_color(self.color_theme_enum)

        if self.settings:
            self.settings.configure_color_theme(self.color_theme_enum)

        if len(self.reports) != 0:
            for report in self.reports:
                report.configure(background=self.color_theme_enum.widget_background.value)
                report.configure(foreground=self.color_theme_enum.code_color.value)
                report.configure(selectbackground=self.color_theme_enum.selection_color.value)

        self.console.tag_config('normal',
                                foreground=self.color_theme_enum.console_color.value)
        self.console.tag_config('external_message',
                                foreground=self.color_theme_enum.error_color.value)
        self.console.tag_config('successful',
                                foreground=self.color_theme_enum.success_color.value)

    # FixMe: refactor
    def insert_to_console(self, text, source=None, tag='normal'):
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
        elif source == "GIT":
            if self.data_process.stdout:
                self.console.insert(END, f"{get_current_time()} [{source}] {self.data_process.stdout}")
                if "Already up to date" in self.data_process.stdout:
                    self.data_process.stdout = None
                    return 0
                else:
                    self.data_process.stdout = None
                    return 1
            if self.data_process.stderr:
                self.console.insert(END, f"{get_current_time()} [{source}] {self.data_process.stderr}\n",
                                    "external_message")
                self.data_process.stderr = None

        self.console.see(END)
        self.console['state'] = DISABLED

    # -*- external commands -*-
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

    def update_ide(self):
        code = self.data_process.execute_external_command("git", "pull")
        update = self.insert_to_console("поиск обновлений", source="GIT")
        if code == 0:
            if update == 1:
                self.insert_to_console("приложение обновлено", source="GIT", tag='successful')
                messagebox.showinfo("Restart IDE", "To apply changes you have to restart IDE")
                exit()
            else:
                messagebox.showinfo("Updates", "No IDE updates")
        else:
            messagebox.showerror("Error!", "Some problem with update or git")

    # -*- file processing -*-
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

    def file_open(self, event=None):
        returned_code = self.data_process.file_open()
        if returned_code != 1:
            self.file_text.edit_modified(False)
            self.insert_to_console("открыт новый файл")
            if isinstance(returned_code, str):
                self.update_title(gpss=returned_code)
            else:
                self.update_title(gpss=True)

    def file_close(self, event=None):
        self.data_process.file_close()
        if self.data_process.file_close() == 0:
            self.insert_to_console("текущий файл закрыт")
            self.update_title(gpss=True)

    def copy_to_buffer(self):
        code = self.data_process.copy_to_buffer()
        self.file_text.clipboard_clear()
        self.clipboard_append(code)
        if code:
            self.insert_to_console("GPSS код скопирован в буфер обмена")

    # -*- window closing -*-
    def close_window(self, event=None):
        if self.settings:
            self.settings.destroy()
        if self.report_window:
            self.report_window.destroy()

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

    def close_report_window(self):
        self.report_window.destroy()
        self.reports=[]
        self.report_window = None
        self.report_panel = None

    def close_settings_window(self):
        self.settings.destroy()
        self.settings = None

    def apply_settings_changes(self):
        self.data_process.peace_interpreter_path = self.ini_process.get_from_config_file("settings", "peace_core_path")
        self.data_process.gpssh_interpreter_path = self.ini_process.get_from_config_file("settings", "gpss_path")
        self.font_size = self.ini_process.get_from_config_file("settings", "font_size")

        print(self.data_process.gpssh_interpreter_path)
        self.file_text.configure(font=(self.font, self.font_size))
        self.gpss_text.configure(font=(self.font, self.font_size))
        self.console.configure(font=(self.font, self.font_size))
        self.close_settings_window()

    # -*- sub windows -*-
    def open_report(self, event=None):
        if self.data_process.simulation_report is not None:
            if self.report_window is None:
                self.report_window = Tk()
                self.report_window.title(f"{self.data_process.pce_path} - simulation reports")
                self.report_window.configure(background=self.color_theme_enum.widget_background.value)
                self.report_panel = ttk.Notebook(self.report_window)

            report = ScrolledTextWidget(self.report_panel, (self.font, self.font_size))
            # - color configure -
            report.configure(background=self.color_theme_enum.widget_background.value)
            report.configure(foreground=self.color_theme_enum.code_color.value)
            report.configure(selectbackground=self.color_theme_enum.selection_color.value)
            #
            self.reports.append(report)
            report_text = self.data_process.open_report()
            report.insert(1.0, report_text)
            report['state'] = DISABLED
            self.report_panel.add(report, text=f"[{get_current_time()}]  {self.data_process.common_name}")
            self.report_panel.pack(expand=1, fill='both')
            self.report_window.protocol("WM_DELETE_WINDOW", self.close_report_window)
            self.report_window.deiconify()
            self.report_window.mainloop()
        else:
            messagebox.showerror("Error!", "There is no .lis file")

    def open_settings(self):
        if self.settings is None:
            self.settings = SettingsWindow(self.ini_process, self.apply_settings_changes)
            self.settings.configure_color_theme(self.color_theme_enum)
        self.settings.protocol("WM_DELETE_WINDOW", self.close_settings_window)
        self.settings.show()

    def build_menu(self):
        self.main_menu = Menu(self)
        self.config(menu=self.main_menu)
        # file toolbar
        self.file_menu.add_command(label="New file          Ctrl-N", command=self.file_close)
        self.file_menu.add_command(label="Open file        Ctrl-O", command=self.file_open)
        self.file_menu.add_command(label="Close file        Ctrl-Q", command=self.file_close)
        self.file_menu.add_command(label="Save file          Ctrl-S", command=self.file_save)
        self.file_menu.add_command(label="Save file as...", command=self.file_save_as)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit                  Alt-F4", command=self.close_window)
        self.main_menu.add_cascade(label='File', menu=self.file_menu)
        # edit toolbar
        self.edit_menu.add_command(label="Copy              Ctrl-C", command=self.copy)
        self.edit_menu.add_command(label="Paste              Ctrl-V", command=self.paste)
        self.edit_menu.add_command(label="Cut                 Ctrl-X", command=self.cut)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Undo              Ctrl-Z", command=self.undo)
        self.edit_menu.add_command(label="Redo               Ctrl-R", command=self.redo)
        self.main_menu.add_cascade(label='Edit', menu=self.edit_menu)
        # run toolbar
        self.run_menu.add_command(label="Compile              F5", command=self.compile)
        self.run_menu.add_command(label="Run model          F6", command=self.run_model)
        self.run_menu.add_command(label="Open report        F7", command=self.open_report)
        self.main_menu.add_cascade(label='Run', menu=self.run_menu)
        # settings toolbar
        self.settings_menu.add_command(label="Open settings", command=self.open_settings)
        self.settings_menu.add_command(label="Update IDE", command=self.update_ide)
        self.settings_menu.add_command(label="Change color theme", command=self.change_color_theme)
        self.main_menu.add_cascade(label="Settings", menu=self.settings_menu)
        # gpss toolbar
        self.gpss_menu.add_command(label="Copy All", command=self.copy_to_buffer)

    def change_color_theme(self, event=None):
        if self.color_theme == "default":
            self.color_theme_enum = DarkColorTheme
            self.color_theme = "dark"
        elif self.color_theme == "dark":
            self.color_theme_enum = DefaultColorTheme
            self.color_theme = "default"
        self.configure_color_theme()

    # -*- packing widgets -*-
    def show(self):
        self.build_menu()
        self.file_text.place(relx=0, rely=0, relw=0.6, relh=0.7)
        self.gpss_text.place(relx=0.6, rely=0, relw=0.4, relh=0.7)
        self.gpss_text['state'] = DISABLED
        self.console.place(relx=0, rely=0.7, relw=1, relh=0.3)

    # -*- events in widgets -*-

    # context menu
    def context_file_menu(self, event):
        self.edit_menu.post(event.x_root, event.y_root)

    def context_gpss_menu(self, event):
        self.gpss_menu.post(event.x_root, event.y_root)

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

    # edit tools
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
        try:
            self.file_text.edit_undo()
        except TclError as error:
            if str(error) == "nothing to undo":
                pass

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

        self.bind("<Control-n>", self.file_close)
        self.bind("<Control-o>", self.file_open)
        self.bind("<Control-q>", self.file_close)
        self.bind("<Control-s>", self.file_save)
        self.bind("<Control-z>", self.undo)

        self.file_text.bind("<Control-r>", self.redo)

        self.bind("<F5>", self.compile)
        self.bind("<F6>", self.run_model)
        self.bind("<F7>", self.open_report)
