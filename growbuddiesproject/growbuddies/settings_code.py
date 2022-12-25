import json
import os

settings_filename = "growbuddies_settings.json"


class Settings:
    def __init__(self):
        # Set the working directory to where the Python files are located.
        # self.logger.debug(
        #     f"--> Current Directory prior to setting to the file location is {os.getcwd()}"
        # )
        cfd = os.path.dirname(os.path.realpath(__file__))
        os.chdir(cfd)
        # self.logger.debug(f"--> Current Directory is {os.getcwd()}")
        self.settings = {}

    def load(self) -> None:
        try:
            with open(settings_filename) as json_file:
                self.settings = json.load(json_file)
        except Exception as e:
            raise Exception(f"Could not open the settings file named {settings_filename}.  Error: {e}")

    def get(self, key) -> str:
        value = self.settings.get(key)
        if not value:
            raise Exception(f"The value for Key {key} is {value}")
        return value

    def get_callbacks(self, key, obj):
        methods = {}
        t_f = self.get(key)
        for k in t_f.keys():
            if t_f[k]:
                methods[k] = getattr(obj, t_f[k])
            else:
                methods[k] = None
        return methods
