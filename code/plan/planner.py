import argparse
import os, sys
import time
import yaml
from omegaconf import OmegaConf

cwd = os.path.abspath(os.path.dirname(__file__))
code_root = os.path.abspath(os.path.join(cwd, '..'))# code
if code_root not in sys.path:
    sys.path.insert(0, code_root)

class Planner:
    def __init__(self, args, extras=None):
        '''
        功能：
        1. 读取配置参数，接受命令行参数覆盖
        2. 创建输出目录，保存配置快照
        3. 告知用户新参数保存位置，令其确认，之后会由 config.py 负责根据配置进行输出文件夹创建等的任务
        '''
        # 将命令行参数覆盖写回配置
        yaml_configs = OmegaConf.load(args.config)
        cli_configs = OmegaConf.from_cli(extras)
        configs = OmegaConf.merge(yaml_configs, cli_configs)
        OmegaConf.resolve(configs)

        # 同时写入命令行参数覆盖的配置
        self.new_cfg_path = self.init_output_dir(args, configs)

        if args.check_updated_yaml:
            print(f"[Planner] Configuration snapshot saved at: {self.new_cfg_path}\n\tModify it if need. Have you finished checking?(y/n)")
            user_input = input().strip().lower()
            if user_input != 'y':
                print("[Planner] User aborted due to configuration mismatch.")
                sys.exit(1)
            else:
                print("[Planner] User confirmed the configuration.")

    def init_output_dir(self, args, configs):
        # 创建输出目录
        if (args.prefix == '' and args.suffix == '') \
            or args.use_timestamp:
            timestamp = time.strftime("%Y%m%d-%H%M%S")
        else:
            timestamp = ""
        names = []
        if args.prefix != '': names.append(args.prefix)
        if timestamp != '': names.append(timestamp)
        if args.suffix != '': names.append(args.suffix)

        output_dir = os.path.join(configs.output.root, '-'.join(names))
        os.makedirs(output_dir, exist_ok=True)
        configs.output.concrete_dir = output_dir

        # 保存配置快照
        snapshot_path = os.path.join(output_dir, "config.yaml")
        with open(snapshot_path, 'w') as f:
            yaml.dump(OmegaConf.to_container(configs), f, default_flow_style=False)

        return snapshot_path

    # more task planning methods can be added here

def parse_args():
    parser = argparse.ArgumentParser(description="Hand-Object Optimization Config Parser")
    parser.add_argument("--config", type=str, default="configs/config.yaml")
    parser.add_argument("--prefix", type=str, default='', help="prefix of exp output dir")
    parser.add_argument("--suffix", type=str, default='', help="suffix of exp output dir")
    parser.add_argument("--use_timestamp", default=1, type=int, help="whether to use timestamp in output dir")
    parser.add_argument("--check_updated_yaml", default=1, type=int, help="whether to check if the yaml config has been updated")

    args, extras = parser.parse_known_args()
    planner = Planner(args, extras)

    return planner

if __name__ == "__main__":
    planner = parse_args()
    print(f"Configuration snapshot saved at: {planner.new_cfg_path}")
