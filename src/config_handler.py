# src/config_handler.py
import configparser

class ConfigReader:
    def get_selected_property(self):
        config = configparser.ConfigParser()
        config.read('src/settings.cfg')
        return config.get('GoogleAPI', 'selected_property', fallback=None)

class ConfigWriter:
    def save_selected_property(self, site_url):
        config = configparser.ConfigParser()
        config.read('src/settings.cfg')
        config['GoogleAPI']['selected_property'] = site_url
        with open('src/settings.cfg', 'w') as configfile:
            config.write(configfile)
