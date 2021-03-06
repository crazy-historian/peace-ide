from os.path import isfile
import configparser
import sys


class IniProcessing:
    def __init__(self, path):
        self.path = path
        self.config_file = configparser.ConfigParser()
        self.create_config_file()

    # FixMe: check .ini file
    def create_config_file(self):
        # default settings
        if isfile(self.path) is False:
            self.path = "settings.ini"
            self.config_file.add_section("settings")
            self.config_file.set("settings", "font", "Consolas")
            self.config_file.set("settings", "font_size", "14")
            self.config_file.set("settings", "gpssh_path", "None")
            self.config_file.set("settings", "peace_core_path", "None")

            with open(self.path, "w") as ini_file:
                self.config_file.write(ini_file)
        else:
            self.config_file.read(self.path)

    def get_config_file(self):
        if not self.config_file:
            self.create_config_file()

        self.config_file.read(self.path)
        return self.config_file

    def insert_to_config_file(self, section, setting, value):
        if self.config_file:
            self.config_file.set(section, setting, value)
            with open(self.path, "w+") as config_file:
                self.config_file.write(config_file)
        else:
            print("Error: there is no .ini file.", file=sys.stderr)

    def get_from_config_file(self, section, setting):
        try:
            setting = self.config_file.get(section, setting)
        except configparser.NoOptionError or configparser.NoSectionError:
            print("Error: no section or option.", file=sys.stderr)
        finally:
            return setting

    def delete_from_config_file(self, section, setting):
        try:
            self.config_file.remove_option(section, setting)
            with open(self.path, "w") as ini_file:
                self.config_file.write(ini_file)
        except configparser.NoSectionError:
            print("Error: no section.", file=sys.stderr)

