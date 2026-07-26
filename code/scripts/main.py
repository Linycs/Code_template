import os, sys

cwd = os.path.abspath(os.path.dirname(__file__)) # core
code_root = os.path.abspath(os.path.join(cwd, '..'))# code
if code_root not in sys.path:
    sys.path.insert(0, code_root)

from utils.config import parse_args
from utils.logger import Logger

# args
cfg_path, cfg_parser = parse_args()

# log
logger = Logger(os.path.join(
            cfg_parser['output.structure.paths.log'], 
            cfg_parser['logging.filename'], 
        ))

# 主函数部分
