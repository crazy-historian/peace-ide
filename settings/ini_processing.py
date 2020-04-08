from os import getcwd
import configparser
import sys


class IniProcessing:
    def __init__(self, path=None):
        self.path = path
        self.config_file = None

    def create_config_file(self):
        self.config_file = configparser.ConfigParser()
        self.config_file.add_section("settings")

        # default settings
        self.config_file.set("settings", "font", "Consolas")
        self.config_file.set("settings", "font_size", "12")
        self.config_file.set("settings", "gpssh_path", "None")
        self.config_file.set("settings", "gpssh_path", "None")


        if not self.path:
            self.path = f"{getcwd()}\\settings.ini"
        else:
            self.path += "\\settings.ini"

        with open(self.path, "w") as ini_file:
            self.config_file.write(ini_file)

    def return_config_file(self):
        if not self.config_file:
            self.create_config_file()

        self.config_file.read(self.path)
        return self.config_file

    def insert_to_config_file(self, section, setting, value):
        if self.config_file:
            self.config_file.set(section, setting, value)
            with open(self.path, "w") as config_file:
                self.config_file.write(config_file)
        else:
            print("Error: there is no .ini file.", file=sys.stderr)

    def get_from_config_file(self, section, setting):
        try:
            return self.config_file.get(section, setting)
        except configparser.NoOptionError or configparser.NoSectionError:
            print("Error: no section or option.", file=sys.stderr)

    def delete_from_config_file(self, section, setting):
        try:
            self.config_file.remove_option(section, setting)
            with open(self.path, "w") as ini_file:
                self.config_file.write(ini_file)
        except configparser.NoSectionError:
            print("Error: no section.", file=sys.stderr)

