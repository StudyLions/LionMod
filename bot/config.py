import configparser as cfgp


conf = None  # type: Conf


class Conf:
    def __init__(self, configfile, section_name="DEFAULT"):
        self.configfile = configfile

        self.config = cfgp.ConfigParser(
            converters={
                "intlist": self._getintlist,
                "list": self._getlist,
            }
        )
        self.config.read(configfile)

        self.section_name = section_name if section_name in self.config else 'DEFAULT'

        self.default = self.config["DEFAULT"]
        self.section = self.config[self.section_name]
        self.bot = self.section

        global conf
        conf = self

    def __getitem__(self, key):
        return self.section[key].strip()

    def __getattr__(self, section):
        return self.config[section]

    def get(self, name, fallback=None):
        result = self.section.get(name, fallback)
        return result.strip() if result else result

    def _getintlist(self, value):
        return [int(item.strip()) for item in value.split(',')]

    def _getlist(self, value):
        return [item.strip() for item in value.split(',')]

    def write(self):
        with open(self.configfile, 'w') as conffile:
            self.config.write(conffile)
