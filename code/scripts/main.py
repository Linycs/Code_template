import os, sys

cwd = os.path.abspath(os.path.dirname(__file__))
code_root = os.path.abspath(os.path.join(cwd, '..'))# code
if code_root not in sys.path:
    sys.path.insert(0, code_root)

from plan.planner import parse_args
from utils.config import CfgParser, initialize_paths
from utils.logger import Logger

# args
planner = parse_args()
cfg_parser = CfgParser(config_path=planner.new_cfg_path)
initialize_paths(cfg_parser)

# log
logger = Logger(os.path.join(
            cfg_parser['output.structure.paths.log'], 
            cfg_parser['logging.filename'], 
        ))

# 主函数部分
