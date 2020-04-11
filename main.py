from settings.ini_processing import IniProcessing
from pce_processing.pce_file_processing import PceFileProcessing
from widgets.main_window import UIWindow

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
    window.bind("<Control-s>", window.file_save)
    window.text_editor.bind("<Button-3>", window.context_menu)

    window.protocol("WM_DELETE_WINDOW", window.close_window)
    window.mainloop()
