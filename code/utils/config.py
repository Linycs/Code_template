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
    #     TODO

def recursive_create_dirs(path_cfg, parent_dir: str):
    """
    根据 output.structure.sub_dirs 创建目录结构，并返回扁平 alias->path 映射。
    说明：alias 只来自叶子节点（str），中间层目录名（如 vis）不作为 alias。
    """
    path_dict = {}

    if isinstance(path_cfg, dict):
        for key, sub_cfg in path_cfg.items():
            sub_dir = os.path.join(parent_dir, key)
            os.makedirs(sub_dir, exist_ok=True)

            new_dict = recursive_create_dirs(sub_cfg, sub_dir)
            _check_conflict(path_dict, new_dict)
            path_dict.update(new_dict)

    elif isinstance(path_cfg, list):
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


def initialize_paths(cfg_parser: CfgParser, ):
    """
    创建本次输出目录并写回配置：
    同时保存 config.yaml 快照并备份代码目录（output.backup.dir_list）。
    """
    output_dir = cfg_parser["output.concrete_dir"]

    sub_cfg = cfg_parser["output.structure.sub_dirs"]
    path_dict = recursive_create_dirs(sub_cfg, output_dir)
    cfg_parser.add_cfg("output.structure.paths", path_dict, mode="override")

    cfg_parser.dump(os.path.join(output_dir, "config.yaml"))

    if cfg_parser["output.backup.do_backup"]:
        backup_dir = path_dict["backup"]
        for folder in cfg_parser["output.backup.dir_list"]:
            src = os.path.join(os.path.dirname(__file__), "../..", folder)
            dst = os.path.join(backup_dir, folder)

            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print(f" [+] Backup: {src} -> {dst}")
