import logging

from termcolor import colored

class Logger:
    def __init__(
        self, 
        fpath: str = None,
        level: int = logging.INFO,
        fmt: str = '%(asctime)s - %(levelname)s - %(message)s',
    ):
        if fpath is None:
            fpath = 'debug.log'

        logging.basicConfig(
            filemode='w', 
            level=level,
            format=fmt,
            filename=fpath,
            # handlers=[
            #     logging.FileHandler(fpath)
            # ],
            encoding='utf-8'
        )
        self.logger = logging.getLogger()
        self.print_ = True
    
    def message(self, line:str):
        self.logger.info(line)
        print(colored(line, 'green'))

    def info(self, line:str):
        self.logger.info(line)

    def warning(self, line:str, print_: bool = None):
        self.logger.warning(line)
        if print_ is not None and print_:
            print(colored(line, 'yellow'))
        elif self.print_:
            print(colored(line, 'yellow'))
    
    def error(self, line:str, print_: bool = None):
        self.logger.error(line)
        if print_ is not None and print_:
            print(colored(line, 'red'))
        elif self.print_:
            print(colored(line, 'red'))
    
    def debug(self, line:str):
        self.logger.debug(line)
    
    def exception(self, line:str):
        self.logger.exception(line)
