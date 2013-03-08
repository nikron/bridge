"""
Configuration class for bridge, controls supports .ini
file type that you know and love from windows.
"""
import configparser
import os

class BridgeConfiguration():
    """
    Takes in a file path to an ini file, and becomes the configuration for the 
    bridge.

    .model_file   -- File model service should use for storage.
    .model_driver -- Storage driver model should use for storage.
    .io_services  -- List of IO services bridge should create.
    """
    def __init__(self, conf_file=None):
        self.file = conf_file

        #let the ini have a keyword in the file section
        #of the model driver
        self.conf_dir = os.path.dirname(conf_file)

        self.model_file = ''
        self.model_driver = ''
        self.io_services = []

        if self.file is not None:
            self.load_from_file()


    def load_from_file(self):
        """Load configuration from stored file."""
        config = configparser.ConfigParser()
        config.read(self.file)

        self.model_file = config['model']['file'].format(this_dir=self.conf_dir)
        self.model_driver = config['model']['driver']


        for io_service in config['io']['services'].split():
            name = config[io_service]['name']
            protocol = config[io_service]['protocol']
            io_con = config[io_service]['connection']
            io_con_args = config[io_service]['connection arguments']

            self.io_services.append((name, protocol, io_con, io_con_args))

