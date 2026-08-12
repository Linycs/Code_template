# Code_template 代码结构

> 文档维护信息
>
> - 更新规则：[doc-maintenance.md](./doc-maintenance.md)
> - 管辖范围：`code/**`、`env/**`、`run.sh`、`run.bat`
> - 更新条件：目录或模块增删改名、模块职责、依赖方向、主要调用链、配置结构、运行入口或输入输出位置发生变化

本仓库是项目初始化模板。具体项目复制后应保留分层原则，删除不需要的占位模块，并根据实际代码整体更新本文档。系统目标、数据契约和设计决策见 [design.md](./design.md)。

## 1. 目录结构

```text
Code_template/
├── _linycs/docs/              # Git 跟踪的项目维护文档
├── code/
│   ├── configs/default.yaml   # 全局配置模板
│   ├── execute/               # 可选的执行层占位
│   ├── plan/planner.py        # CLI 配置合并及运行目录初始化
│   ├── scripts/main.py        # Python 主流程模板
│   ├── test_debug/            # 被忽略的一次性测试/debug 代码占位
│   └── utils/
│       ├── config.py          # CfgParser、输出目录初始化及代码备份
│       ├── logger.py          # 文件日志和终端输出
│       ├── statistics.py      # 任意维数值序列统计与具名容器
│       └── visualization.py   # 多 point-cloud/mesh 的 PLY/PNG 导出
├── data/                      # 数据说明或小型示例占位
├── env/                       # 依赖、Docker 和环境初始化模板
├── AGENTS.md                  # AI 协作、授权和文档维护规则模板
├── README.md                  # 模板使用说明
├── run.sh                     # Linux 入口占位，复制模板后补齐
└── run.bat                    # Windows 入口模板
```

## 2. 依赖方向

- `code/utils/` 只依赖同目录模块或 Python package，不依赖项目业务模块。
- `code/plan/` 负责运行前的配置与目录规划。
- `code/scripts/` 负责组合各层能力，不承载可复用算法。
- `code/execute/` 是可选占位；若项目不需要独立执行层应删除。
- `code/test_debug/` 只放一次性测试或调试实现，默认不进入 Git；长期回归测试应使用项目单独建立的 `tests/`。

## 3. 运行链路

```text
run.sh / run.bat（入口模板，按项目补齐）
  └─ code/scripts/main.py
      ├─ plan.planner.parse_args
      ├─ CfgParser
      ├─ initialize_paths
      ├─ Logger
      └─ 项目业务流程（复制模板后补充）
```

`Planner` 使用 OmegaConf 合并 `default.yaml` 与命令行覆盖项，先建立运行目录和配置快照；`initialize_paths` 再按配置创建子目录、写回路径映射并备份代码。

## 4. 通用工具

- `StatisticsSeq` 保存任意 1-N 维 NumPy 数组、可广播的 valid/weights、命名轴和非结构化 info，支持任意轴的数量、均值、加权均值、median、std、min/max 与 quantile 分析。
- `StatisticsManager` 管理多个具名 `StatisticsSeq`，支持采集器、snapshot、查询、统一分析和 JSON 保存/恢复。
- `VisMultiShape` 管理任意数量的 point cloud 和三角 mesh，由调用方分别提供颜色、标签和显示属性，可将组合几何导出为 PLY 或多视角 PNG；不包含具体项目的坐标系和业务假设。

## 5. 输入输出模板

默认运行产物写入 `output/<run>/`，包含 `log/`、`backup/` 和 `results/`。复制模板后若改变目录结构、输入来源或输出格式，应同步更新本节及 `default.yaml`。
