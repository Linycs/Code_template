# Code_template 设计文档

> 文档维护信息
>
> - 更新规则：[doc-maintenance.md](./doc-maintenance.md)
> - 管辖范围：`code/**`、`env/**`、`run_entrance.sh`、`run_entrance.bat`
> - 更新条件：系统目标、设计原则、数据契约、算法、配置语义、执行流程或关键输入输出发生变化

本文档提供复制模板后的设计基线。新项目应删除不适用的模板说明，并补齐实际目标和约束。

当前 `run_entrance.sh` 是空占位，复制模板后必须按 `AGENTS.md` 中的 `code_entrance` 补齐实际入口；`run_entrance.bat` 同样应按目标平台核对。

## 1. 系统目标

- TODO：描述项目解决的问题、用户和交付结果。
- TODO：说明范围内功能以及明确不处理的内容。

## 2. 设计原则

- 全局配置集中在 `code/configs/default.yaml`，通过 `CfgParser` 访问。
- 运行时配置通过 OmegaConf 合并，并保存展开后的快照，保证实验可追溯。
- 通用能力放在 `code/utils/`，不得反向依赖项目业务模块。
- 主流程只负责编排；可复用算法、数据适配和持久化应落在职责明确的模块或类中。
- 一次性测试/debug 代码放在 `code/test_debug/`，长期回归测试另建 `tests/`。

## 3. 配置与运行

```text
default.yaml + CLI overrides
            ↓
         Planner
            ↓
output/<run>/config.yaml
            ↓
CfgParser → initialize_paths → Logger → project workflow
```

默认输出结构由 `output.structure.sub_dirs` 声明。复制模板后新增的全局开关、路径和算法参数均应进入配置，并在本节说明其语义。

## 4. 通用统计

`StatisticsSeq` 面向任意 1-N 维 NumPy 数值：

- `values` 保存原始数值；
- `valid` 和 `weights` 与 values 同形或可广播；
- `axis_names` 给每个维度命名；
- `info` 保存单位、阶段、来源等非结构化说明；
- `analyze` 支持全部轴、轴编号或轴名归约。

`weighted_mean` 使用 weights；median 和 quantile 是排除 invalid/非有限值后的非加权分布统计。`StatisticsManager` 负责多个具名序列的 snapshot、分析和 JSON 持久化，不解释具体 loss 或业务含义。

## 5. 通用三维可视化

`VisMultiShape` 支持在同一坐标系中加入任意数量的 point cloud 和三角 mesh。每个 shape 独立指定 RGB、label、alpha，以及点云的 point size。调用方显式指定输出路径、视角、显示缩放、轴名和显示单位。

- `export_ply` 合并全部顶点，自动修正 mesh face offset，并保存颜色、geometry type 和 shape index。
- `export_image` 对组合几何居中，以统一尺度渲染一个或多个观察视角。

工具类不读取项目配置，也不预设 depth、MANO、相机或 world 坐标等业务语义。

## 6. 项目数据契约

- TODO：列出输入文件、数组 shape、坐标系、单位和有效性规则。
- TODO：列出输出格式、命名规则和兼容性要求。

## 7. 项目算法与验证

- TODO：描述核心算法、loss、优化参数和 stage 语义。
- TODO：描述单元测试、集成测试和人工 review 方式。
