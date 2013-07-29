"""
Configuration class for bridge, controls supports .ini
file type that you know and love from windows.
"""
import configparser
import os

class BridgeConfiguration():
    """
    Reads in a .ini file and sets the relevant information as properties.

    :param conf_file: Path to configuration file.
    :type conf_file: str

    :param stderr: If the log should be output to STDERR
    :param stderr: bool
    """

    def __init__(self, conf_file, stderr):
        self.file = conf_file
        self.stderr = stderr

        #let the ini have a keyword in the file section
        #of the model driver
        self.conf_dir = os.path.dirname(self.file)

        self.data_dir = ''
        self.io_services = {}
        self.log_file = ''

        if self.file is not None:
            self.load_from_file()

    def load_from_file(self):
        """
        Load configuration from stored path.
        """
        config = configparser.ConfigParser()
        config.read(self.file)

        self.log_file = config['general']['log'].format(this_dir = self.conf_dir)
        self.data_dir = config['general']['dir'].format(this_dir = self.conf_dir)

        for io_service in config['io']['services'].split():
            name = config[io_service]['name']
            protocol = config[io_service]['protocol']
            file_name = config[io_service]['file name']

            self.io_services[name] = (protocol, file_name)
