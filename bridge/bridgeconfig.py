import configparser
import os

class BridgeConfiguration():
    def __init__(self, conf_file):
        self.file = conf_file
        self.conf_dir = os.path.dirname(conf_file)
        self.load_from_file()

    def load_from_file(self):
        config = configparser.ConfigParser()
        config.read(self.file)

        self.model_dir = config['model']['dir'].format(this_dir=self.conf_dir)
        self.model_driver = config['model']['driver']


        self.io_services = []
        for io_service in config['io']['services'].split():
            name = config[io_service]['name']
            protocol = config[io_service]['protocol']
            io_con = config[io_service]['connection']
            io_con_args = config[io_service]['connection arguments']
            
            self.io_services.append((name, protocol, io_con, io_con_args))

