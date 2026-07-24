import os
import time
import argparse
import yaml
import shutil
from yaml.loader import SafeLoader


class CfgParser:
    """
    YAML 配置包装器：
    - 支持点分 key 访问：cfg['output.root'] 等价于 cfg.cfg['output']['root']
    - 支持点分 key 写入：add_cfg('optimization.stage', 'stage1', mode='override')
    - cfg.cfg 保存原始 dict（必要时可直接取原始 stage 配置）
    """

    def __init__(self, config_path=None, cfg_dict=None):
        if config_path is not None:
            self.cfg = self.load_config(config_path)
        else:
            self.cfg = {} if cfg_dict is None else cfg_dict

    def load_config(self, path: str):
        with open(path, "r") as f:
            return yaml.load(f, Loader=SafeLoader)

    def get_cfg(self, key: str, split: str = "."):
        """读取点分 key；缺失 key 直接报错，避免 silent fallback。"""
        keys = key.split(split)
        out = self.cfg
        for k in keys:
            if k not in out:
                raise KeyError(f"[CfgParser] Key '{k}' not found while accessing '{key}'")
            out = out[k]
        return out

    def add_cfg(self, key: str, value, mode: str = "add", split: str = "."):
        """
        写入点分 key：
        - add：只允许新增，不允许覆盖
        - override：允许覆盖（命令行 runtime 参数应使用 override）
        """
        if mode not in ("add", "override"):
            raise ValueError("mode must be 'add' or 'override'")

        keys = key.split(split)
        # import pdb; pdb.set_trace()

        out = self.cfg

        # 走到最终写入位置的父 dict（中间层级不存在则自动创建）
        for k in keys[:-1]:
            if k not in out:
                out[k] = {}
            elif not isinstance(out[k], dict):
                raise KeyError(f"[CfgParser] Conflict at key '{k}', expecting dict")
            out = out[k]

        final_key = keys[-1]
        if final_key in out and mode == "add":
            raise KeyError(f"[CfgParser] Key exists '{key}', use override")
        out[final_key] = value

    def dump(self, path: str):
        """保存本次运行的最终配置快照（强制 block style，便于阅读与 diff）。"""
        with open(path, "w") as f:
            yaml.dump(self.cfg, f, default_flow_style=False)

    def __getitem__(self, key: str):
        return self.get_cfg(key)

    def __setitem__(self, name, value):
        self.add_cfg(name, value, mode="override")

    # def tree(self, cfg:None, max_depth=None, depth=0):
    #     if cfg is None:
    #         cfg = self.cfg
        
    #     if isinstance(cfg, dict):
    #         for k, v in cfg.items():
    #             print(f"{k}:")
    #             self.tree(v, max_depth, depth+1)

def recursive_create_dirs(path_cfg, parent_dir: str):
    """
    根据 output.structure.sub_dirs 创建目录结构，并返回扁平 alias->path 映射。
    说明：alias 只来自叶子节点（str），中间层目录名（如 vis）不作为 alias。
    """
    path_dict = {}

    if isinstance(path_cfg, dict):
        # e.g. {"vis": ["initial", "optimized"]}
        for key, sub_cfg in path_cfg.items():
            sub_dir = os.path.join(parent_dir, key)
            os.makedirs(sub_dir, exist_ok=True)

            new_dict = recursive_create_dirs(sub_cfg, sub_dir)
            _check_conflict(path_dict, new_dict)
            path_dict.update(new_dict)

    elif isinstance(path_cfg, list):
        # e.g. ["log", "backup", {"vis": [...]}, "results"]
        for item in path_cfg:
            new_dict = recursive_create_dirs(item, parent_dir)
            _check_conflict(path_dict, new_dict)
            path_dict.update(new_dict)

    elif isinstance(path_cfg, str):
        # e.g. "log"
        sub_dir = os.path.join(parent_dir, path_cfg)
        os.makedirs(sub_dir, exist_ok=True)
        path_dict[path_cfg] = sub_dir

    return path_dict


def _check_conflict(base_dict, new_dict):
    """防止不同分支生成相同 alias，导致路径索引歧义。"""
    for k in new_dict:
        if k in base_dict:
            raise KeyError(f"[PathConflict] Duplicate directory alias key: {k}")


def initialize_paths(cfg_parser: CfgParser, stage: str):
    """
    创建本次输出目录并写回配置：
    - output.output_dir：outputs/<stage>/<timestamp>
    - output.structure.concrete_dir：alias->path 扁平路径索引
    同时保存 config.yaml 快照并备份代码目录（output.backup）。
    """
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    
    root = cfg_parser["output.root"]
    prefix = cfg_parser["output.prefix"]
    suffix = cfg_parser["output.suffix"]
    if not prefix:
        if 'mano_param_seq_dir' in cfg_parser['input']:
            prefix = cfg_parser['input.mano_param_seq_dir'].split('/')[-1] + '-'
        elif 'hoi_param_fpath' in cfg_parser['input']:
            prefix = cfg_parser['input.hoi_param_fpath'].split('/')[-1] + '-'
        else:
            prefix = ''
    suffix = ('-' + suffix) if suffix else ''
    output_dir = os.path.join(root, stage, f'{prefix}{timestamp}{suffix}')

    cfg_parser.add_cfg("output.output_dir", output_dir, mode="override")

    sub_cfg = cfg_parser["output.structure.sub_dirs"]
    path_dict = recursive_create_dirs(sub_cfg, output_dir)
    cfg_parser.add_cfg("output.structure.concrete_dir", path_dict, mode="override")

    cfg_parser.dump(os.path.join(output_dir, "config.yaml"))

    backup_dir = path_dict["backup"]
    for folder in cfg_parser["output.backup"]:
        src = os.path.join(os.path.dirname(__file__), "../..", folder)
        dst = os.path.join(backup_dir, folder)

        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        print(f" [+] Backup: {src} -> {dst}")


def parse_args():
    """命令行参数 > YAML：stage/start/end 作为 runtime 覆盖写回 optimization.*。"""
    parser = argparse.ArgumentParser(description="Hand-Object Optimization Config Parser")
    parser.add_argument("--config", type=str, default="configs/config.yaml")
    parser.add_argument("--stage", type=str, default="stage1", help="format= stage[num] or stage[num]-[num]")
    parser.add_argument("--hoi_param_fpath", type=str, default=None)
    # parser.add_argument("--start_frame", type=int, default=0)
    # parser.add_argument("--end_frame", type=int, default=None)
    parser.add_argument("--prefix", type=str, default=None)

    args = parser.parse_args()
    cfg_path = args.config

    cfg_parser = CfgParser(config_path=cfg_path)
    if args.hoi_param_fpath is not None:
        cfg_parser['input.hoi_param_fpath'] = args.hoi_param_fpath
    if args.prefix is not None:
        cfg_parser['output.prefix'] = args.prefix

    if '-' in args.stage:
        first_stage_name = args.stage.split('-')[0]
    else:
        first_stage_name = args.stage
    cfg_parser.add_cfg("optimization.stage", first_stage_name, mode="override")
    cfg_parser.add_cfg("optimization.all_stage", args.stage, mode="override")
    # cfg_parser.add_cfg("optimization.start_frame", args.start_frame, mode="override")
    # cfg_parser.add_cfg("optimization.end_frame", args.end_frame, mode="override")

    initialize_paths(cfg_parser, args.stage)
    return cfg_path, cfg_parser


if __name__ == "__main__":
    cfg_path, cfg_parser = parse_args()
    print(f"[Config] Loaded config from: {cfg_path}")
