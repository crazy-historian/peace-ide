from settings.ini_processing import IniProcessing
from pce_processing.pce_file_processing import PceFileProcessing
from widgets.main_window import UIWindow


if __name__ == "__main__":
    ini_process = IniProcessing(path="settings.ini")
    window = UIWindow(ini_process=ini_process)
    data_process = PceFileProcessing(ini_process=ini_process, text_editor=window.file_text)

    window.ini_process = ini_process
    window.data_process = data_process
    window.bind_events()
    window.geometry("1366x768+500+100")
    window.show()
    window.protocol("WM_DELETE_WINDOW", window.close_window)
    window.mainloop()

