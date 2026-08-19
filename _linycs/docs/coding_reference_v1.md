# Coding reference

## 使用说明

本文档是从历史项目中积累的跨项目编码参考，用于说明代码结构调整背后的判断依据，不描述任何当前项目的代码事实。Agent 不应因为本文出现了某个目录、文件、类、函数、数据格式或第三方组件，就推断当前项目存在相同内容或需要创建相同结构。

### 规则解释

- “必须”“禁止”表示默认编码约束，但当前项目的 `AGENTS.md` 和用户本轮明确要求具有更高优先级。
- “应”“建议”“优先”表示通常采用的默认选择，需要结合当前代码、修改范围和复用成本判断。
- 标记为“历史示例（非当前项目事实）”的内容只用于解释原则，不要求机械复现示例结构。
- 标记为“待补充”的章节尚未形成规则，Agent 不应自行补全或推断。

### 阅读方式

Agent 首次使用本文档时，只读取本节和各二级标题，再根据当前任务读取对应章节，不要一次性读取无关案例。若本文作为 Codex 全局参考文件使用，应由全局 `AGENTS.md` 提供这条按需读取规则，而不是把本文全文直接写入全局 `AGENTS.md`。

- 文件结构：说明项目目录、文件职责及复用范围。
- 调用关系：说明不同层级代码之间允许的依赖方向。
- 代码结构：说明函数、类和功能模块的组织与调整。
- 代码复用：说明值得复用的通用能力和输出形式。
- 代码重构：预留说明已有代码需要重组时的处理方式，当前待补充。
- 数据流 & 数据校验：说明数据传递、数据契约和校验边界。
- 脚本：说明项目运行脚本的组织方式。
- 文档维护：说明如何服从当前项目声明的文档维护机制。

## 文件结构

下面是一种 Python 项目目录组织的完整示例。没有“举例”前缀的条目表示作者通常希望在同类项目中复用的稳定结构；以“举例”开头的条目只展示一种业务落地方式。

稳定结构表示默认偏好，不表示必须为当前任务创建尚不需要的目录。已有项目应优先遵循其现有结构、项目级 `AGENTS.md` 和架构文档。

```text
project/
├── AGENTS.md                         # Codex 项目规则
├── README.md                         # 项目说明
├── run_entrance.sh                            # 项目统一运行入口
├── .gitignore                        # Git 忽略规则
│
├── code/                             # 项目 Python 代码
│   ├── __init__.py                   # code 包标记
│   │
│   ├── configs/                      # 项目配置
│   │   └── default.yaml              # 全局默认参数配置：输入、输出、主要算法部分、可视化等
│   │
│   ├── scripts/                      # 程序入口和流程编排
│   │   ├── main.py                   # 举例：执行当前项目的主优化流程
│   │   └── detect_2d.py              # 举例：执行独立的 2D 检测和缓存生成流程
│   │
│   ├── plan/                         # 举例：需要运行前配置规划时使用
│   │   └── planner.py                # 举例：合并 YAML 与命令行配置并保存运行快照
│   │
│   ├── dataio/                       # 外部文件格式和数据源的读取、保存与适配
│   │   ├── calibration.py            # 举例：读取相机标定并转换为项目内部相机数据
│   │   ├── depth.py                  # 举例：适配 FoundationStereo 深度结果
│   │   ├── detection.py              # 举例：适配 HaMeR 检测输出和检测缓存
│   │   ├── frame_range.py            # 举例：统一处理时序数据的帧区间
│   │   └── recon_init.py             # 举例：适配 HandFlow 的 MANO 初始重建结果
│   │
│   ├── preprocess/                   # 输入数据的预处理
│   │   ├── mask_cache.py             # 举例：提供可复用的序列 mask 压缩缓存
│   │   └── rgbd.py                   # 举例：在 RGB-D 项目中生成去噪的 world 点云
│   │
│   ├── core/                         # 项目的核心数据结构、模型和算法
│   │   ├── cameras.py                # 举例：在多视角项目中封装相机和投影计算
│   │   └── hand_model.py             # 举例：在手部项目中封装 MANO 模型
│   │
│   ├── optim/                        # 举例：具有后优化流程时，存放优化参数、loss 和优化过程
│   │   ├── data_provider.py          # 举例：为当前优化过程组织参数和多视角观测
│   │   ├── depth_provider.py         # 举例：为当前优化过程提供深度观测
│   │   └── optimizer.py              # 举例：实现当前项目的分阶段优化和各项 loss
│   │
│   ├── utils/                        # 不依赖具体业务的通用工具
│   │   ├── config.py                 # 通用配置读取、输出路径初始化和配置快照
│   │   ├── logger.py                 # 通用日志和进度显示
│   │   ├── statistics.py             # 通用数值序列统计和结果管理
│   │   ├── render.py                 # 举例：几何项目可复用的 mesh 渲染能力
│   │   ├── visualization.py          # 举例：几何项目可复用的点云和 mesh 导出能力
│   │   └── blender_ply_import.py     # 举例：为当前几何序列生成 Blender 时间轴预览
│   │
│   └── test_debug/                   # 一次性测试和调试代码，测试完成后删除且不进入 Git
│       └── .gitignore                # 忽略目录内全部内容，仅保留目录和使用规则
│
├── data/                             # 项目数据入口和数据说明
│
├── env/                              # 环境安装和依赖记录
│   └── requirements.txt              # Python 依赖列表
│
├── output/                           # 运行产物根目录，不进入 Git
│   └── <run_name>/                   # 举例：按运行名称隔离一次实验的全部产物
│       ├── config.yaml               # 举例：本次运行解析后的配置快照
│       ├── log/                       # 举例：运行日志
│       ├── backup/                    # 举例：本次运行对应的代码备份
│       ├── preprocess/                # 举例：检测、mask 和点云等中间缓存
│       ├── results/                   # 举例：最终数值结果
│       ├── vis_2d/                    # 举例：二维可视化结果
│       └── vis_3d/                    # 举例：三维可视化结果
│
├── _linycs/                          # 需要 Git 跟踪、但与项目主体代码关联较弱的内容
│   └── docs/                         # 项目文档
│       ├── architecture.md            # 项目代码结构、模块职责和依赖关系
│       ├── design.md                  # 项目实现的数据流、算法设计和关键约定
│       ├── doc-maintenance.md         # 受维护文档的 freshness 检查和同步规则
│       ├── coding_style.md            # 项目代码风格与设计原则
│       ├── linycs-requirements.md     # 用户需求和约束记录
│       └── TODO.md                    # 项目待办事项
│
└── _local/                           # 不进入 Git 的本地工作内容
    ├── ai_log/                        # AI 工作过程日志
    └── docs/                          # 本地分析、方案、实验记录和未定稿文档
```

## 调用关系

### 默认原则

- 入口与业务编排可以调用稳定的底层能力，底层能力不应反向依赖入口或具体业务流程。
- 无论是否属于同一文件夹，具体代码的调用关系都不能成环。
- 通用工具只能调用其他通用工具或 Python package，不能依赖项目业务模块。
- 当前项目可以定义不同于下方示例的目录层级；此时以项目级架构说明为准。

### 历史目录层级示例（非当前项目事实）

| 等级 | 文件夹 |
| --- | --- |
| 入口 | `run_entrance.sh` |
| L5 | `code/scripts` |
| L4 | `code/plan`、`code/execute` |
| L3 | `code/dataio`、`code/preprocess`、`code/optim` |
| L2 | `code/core` |
| L1 | `code/utils` |
| L0 | Python package |

- `run_entrance.sh` 只调用 `code/scripts`。
- 高等级文件夹可以调用低等级文件夹，低等级不能调用高等级。
- 同等级的不同文件夹可以相互调用，不需要为了调用关系继续细分等级。
- `utils` 只能调用自身或 Python package。
- 项目有明确的不同分层时，以项目级说明替换这张目录映射表，但仍应保持依赖无环和通用层不反向依赖业务层。

## 代码结构

> 核心问题：
> 为了实现一个功能而调整类、函数或模块时，功能怎么分解/整合/复用？
> 增加的内容达到一定量之后，如何判断是否应调整代码结构？如何调整？

代码结构需要在职责归属、耦合度、复用程度、接口复杂度、代码量和可读性之间取舍。这里的“调整”包括新增、提取、移动、拆分、合并和删除。

### 数据内容与结构分离

业务代码负责决定处理什么、何时处理以及如何解释结果；通用代码只负责稳定的数据结构和处理机制。

例如，“内容”包括数据来源、业务含义、处理开关和输出位置；“结构”包括几何表示、文件写出、相机投影和 ray-casting 等可以脱离具体业务复用的能力。

#### 例一（历史示例，非当前项目事实）：mesh 与 point cloud 的几何导出

`ManoProvider` 决定导出可见点、完整点或完整 mesh，`DepthProvider` 决定导出哪些有效深度点。两者各自准备几何内容，再交给同一个 `VisMultiShape`：

```python
# ManoProvider：业务代码决定顶点、面片和显示信息
visualization.add_shape(current, faces=current_faces, color=color, label=label)

# DepthProvider：没有面片时，同一接口表示 point cloud
visualization.add_shape(current, faces=None, color=color, label=label)
```

`VisMultiShape` 不判断数据来自 MANO 还是 depth，只根据是否提供 `faces` 组织 mesh 或 point cloud，并统一完成 PLY 写出。这种拆分会在两个 Provider 中保留少量相似的调用代码，但不会让通用导出代码依赖两个业务对象。

#### 例二（历史示例，非当前项目事实）：mesh 渲染

MANO 可见性和 HaMeR mask 都需要 mesh 渲染，但对结果的使用不同：

```python
# ManoProvider：将可见面解释为后续采样的可见顶点
visible_faces = renderer.visible_face_indices(vertices, faces)

# HaMeRBackend：将 silhouette 解释为检测输出的手部 mask
mask = renderer.render_silhouette(vertices, faces)
```

`MeshRenderer` 只保存相机参数并实现坐标变换、投影和 ray-casting，不知道输入是 MANO 还是 HaMeR，也不解释输出的业务意义。

如果通用代码开始依赖具体 Provider、数据来源或大量业务开关，说明复用边界过高；如果多个业务模块重复实现写出、投影或渲染，说明复用边界过低。

### 调整函数

#### 例一（历史示例，非当前项目事实）：提取结果透传字段的读取函数

最初，`code/scripts/main.py` 在保存优化结果时直接打开源 NPZ，列出将被重新生成的几何字段，再将其他字段按 `FrameRange` 截取后传给 `save_result()`。这些代码位于主流程中，但实际处理的是 HandFlow NPZ 的字段规则。

调整时，字段判断和帧区间截取被提取为 `code/dataio/recon_init.py` 中的 `load_passthrough_fields(source_path, frame_range, sides)`。`ManoProvider.save_result()` 使用自身状态组织保存流程，`scripts/main.py` 只负责调用。

当一段代码具有明确输入输出、不依赖对象状态，并且属于特定数据格式时，可以提取为对应数据模块中的函数，不应留在入口脚本中。

### 调整类

#### 例一（历史示例，非当前项目事实）：将网格渲染函数调整为 `MeshRenderer`

最初，手部 mask 的渲染由 `code/preprocess/hand_observation.py` 中的 `_render_mesh_mask()` 完成。调用时需要传入顶点、面片、相机内参和图像尺寸，函数内部实现 Open3D ray-casting，输出 silhouette。

后来计算 MANO 可见顶点时，同样需要相机投影和 ray-casting，但输出变成了可见面索引。如果继续增加独立函数，相机坐标变换、投影范围和射线生成都会重复。

调整后，`code/utils/render.py` 中的 `MeshRenderer` 保存相机内参、图像尺寸和坐标变换，分别通过 `render_silhouette()` 和 `visible_face_indices()` 提供两种输出。该类不理解 MANO、深度或检测业务，因此可以放入 `utils` 复用。

当一个函数扩展出多个共享固定状态的相关操作时，可以调整为类；业务信息仍应由调用方解释。

### 调整功能模块

#### 例一（历史示例，非当前项目事实）：增加几何序列导出功能

原先，`code/preprocess/geometry_preview.py` 中的 `export_depth_sequence_preview(...)` 同时接收 `ManoProvider` 和 `DepthProvider`，逐帧取出手部网格与深度点云，再将它们合并导出。这样可以共用帧遍历和导出流程。

随着导出类型和可视化开关增加，该函数既要读取两个 Provider 的内部状态，又要决定两类几何的组合方式。继续统一这个流程，会让参数传递和条件分支逐渐集中在一个函数中。

调整时，数据获取与序列组织被分别放回 `ManoProvider.export_geometry_sequence()` 和 `DepthProvider.export_point_cloud_sequence()`。两个 Provider 各自处理自己的状态，调用方也可以分别控制两类几何的导出与查看。

`code/utils` 中的 `VisMultiShape` 只保留通用的可视化与几何写出能力。这种结构会在两个 Provider 中保留少量相似的逐帧处理代码，但避免了为复用整个流程而增加跨对象依赖。

当复用要求传入多个业务对象、大量状态或控制参数时，不必强行统一整个流程；可以由各业务对象组织数据，只复用稳定的底层能力。

#### 例二（历史示例，非当前项目事实）：删除手部观测预处理模块

`code/preprocess/hand_observation.py` 原本计划统一准备 2D joints 和手部 mask。其中 `prepare_2d_joints()` 没有实际实现，已有流程主要是从初始重建 NPZ 读取网格、渲染 mask 并写入缓存，由 `scripts/main.py` 在优化前调用。

后来 HaMeR 检测在同一次前向中已经生成了关节和网格，mask 可以直接由这份网格渲染，并与未校正的深度输入保持相同图像网格。因此 mask 生成被移入检测流程，通过 `DetectionOutput` 返回，再由检测脚本写入 `PackedMaskCache`。

原模块删除后，缓存和渲染仍分别复用 `PackedMaskCache` 与 `MeshRenderer`，`scripts/main.py` 也不再负责准备 mask。调整的是业务流程所属位置，而不是重写底层能力。

当一个模块的核心数据已经由其他流程自然产生，而自身只剩下转发和编排时，应将流程并回数据生产位置，不必为已有的模块结构继续保留空间。

## 代码复用

### 复用判断

- 优先复用职责稳定、业务无关、接口清楚的底层机制，不为复用而合并具有不同业务含义的完整流程。
- 如果通用代码开始依赖具体 Provider、数据来源或大量业务开关，说明复用边界可能过高。
- 如果多个业务模块重复实现文件写出、投影、渲染、日志或配置读取等稳定机制，说明复用边界可能过低。
- 少量相似的业务编排可以保留；消除表面重复不应以增加跨对象依赖和复杂参数为代价。

### 历史项目中的可复用资产示例（非当前项目事实）

下列复用代码的具体实现可以在远程仓库 `git@github.com:Linycs/Code_template.git` 中找到。

#### 示例：配置与运行规划

`code/plan/planner.py`、`code/utils/config.py` 和 YAML 配置文件作为一组复用。YAML 保存全局参数和输出目录结构；运行规划负责合并命令行覆盖、确定实验目录并保存当次配置快照；配置读取负责在后续代码中统一传递参数、创建输出子目录并备份代码。

新增全局参数或输出路径时，应继续扩展这套流程，不在业务代码中重复读取 YAML、设置默认参数或拼接实验目录。

#### 示例：日志与进度显示

`code/utils/logger.py` 统一处理日志文件、终端输出、日志级别和序列处理进度。业务代码只提供消息内容和进度描述，不自行配置日志器、混用直接打印或重复创建进度条。这样可以保证同一次运行中的输出格式、保存位置和显示方式一致。

#### 示例：Mesh 渲染

`code/utils/render.py` 复用的是基于相机的通用 mesh 渲染逻辑，包括坐标转换、投影范围、射线生成、silhouette 和可见面计算。调用方提供相机、顶点和面片，并负责解释渲染结果；渲染代码不区分 MANO、检测结果或其他几何来源。

新增 mesh mask、可见性或其他基于相机的网格计算时，应优先复用或扩展这套底层机制，不在业务模块中重复实现 ray-casting。

#### 示例：3D 数据可视化

`code/utils/visualization.py` 统一表示和导出 mesh 与 point cloud。调用方负责准备顶点、可选面片、颜色、标签、坐标系和单位；通用可视化逻辑负责组织几何、合并多个 shape 并写出文件。有面片时按 mesh 处理，没有面片时按 point cloud 处理，不为不同业务来源重复实现导出。

3D 几何序列需要交互查看时，可以保留逐帧几何文件，但应同时保存序列索引与原始帧名的映射，便于外部可视化工具按时间加载。

#### 示例：2D 序列与必要数据保存

用于人工查看的连续 2D 图片不应长期保存为逐帧图片。应按帧顺序组成 H.264 编码的视频，每帧至少写入 frame index，并可按需要加入原始帧名、处理阶段或其他说明。单张诊断图仍可直接保存为图片。

如果逐帧内容需要被后续程序读取、精确计算或无损复现，应将其视为数据而不是可视化结果：单个数组保存为 NPY，多个相关数组打包为 NPZ，并保留帧名、有效性等对齐信息。H.264 视频只用于查看，不作为数据缓存。

## 代码重构

> 状态：待补充。本节当前不形成额外规则。已有的函数、类和功能模块调整案例暂时保留在“代码结构”章节。

## 数据流 & 数据校验

同一份数据应在进入系统或跨越模块边界时完成必要校验，后续代码依赖已经建立的数据契约，不在每层重复校验。

从外部文件、旧缓存、用户输入或第三方组件重新取得数据时，应将其视为新的边界并重新建立必要契约；进入可信的内部表示后，不在每层重复确认相同格式。

#### 例一（历史示例，非当前项目事实）：同一份配置被重复校验

调整前，参数配置在阶段入口、参数读取和 loss 计算中分别校验：

```python
# 阶段入口
validate_parameter_config(parameters)

# 参数读取
validate_parameter_config(params_require_grad)
params = get_params(params_require_grad)

# loss 计算
validate_parameter_config(params_require_grad)
```

调整后，阶段入口完整校验一次，参数读取和 loss 计算直接使用校验结果。

```python
validate_parameter_config(parameters)
params = get_params(parameters)
loss = compute_loss(params, parameters)
```

#### 例二（历史示例，非当前项目事实）：计算函数重复检查上游已经确定的 shape

早期 depth 计算中包含：

```python
if points_world.ndim != 4 or vertices_world.ndim != 4:
    raise ValueError("必须为 (H,T,N|V,3)")

if points_world.shape[:2] != vertices_world.shape[:2]:
    raise ValueError("H,T 不一致")

if distances.shape != point_valid.shape:
    raise ValueError("distances 与 point_valid shape 必须一致")
```

这些数据由固定的准备流程生成，shape 和帧序应在进入优化前确定。迭代内部只保留计算：

```python
observations = prepare_observations(...)
loss = compute_depth_loss(observations, vertices)
```

#### 例三（历史示例，非当前项目事实）：为单一实现增加类型校验和分支

历史代码为尚未存在明确需求的平滑模式增加了开关、类型校验和条件分支：

```python
if type(smooth_all) is not bool:
    raise TypeError(...)

if not smooth_all:
    return loss_joint

return loss_joint + loss_trans
```

后来直接根据实际参与优化的参数选择平滑项，删除这个额外开关。不为假设中可能出现的模式提前增加参数、校验和分支。

#### 例四（历史示例，非当前项目事实）：应保留的校验

```python
if not valid_observations.any():
    raise RuntimeError("当前区间没有有效观测")
```

这类校验决定当前计算能否成立，不能删除。其与过度校验的区别在于，它检查当前数据内容，而不是重复确认上游已经保证的数据格式。

## 脚本

运行脚本只负责选择运行步骤、复用已有结果和传递参数，不在其中实现数据处理、模型或优化逻辑。项目全局参数由项目配置系统管理，脚本只保留与某次运行组合相关的选项。

### 历史脚本组织示例（非当前项目事实）

假设 `run_entrance.sh` 是项目的使用脚本，也是终端运行入口。脚本开头集中编写当次运行的默认参数，例如配置文件、输出名称、时间戳开关和运行阶段；后半部分按流程调用 `code/scripts` 中的代码，并将前面的参数统一传入。若当前项目使用其他入口文件名，应替换示例名称，不要求额外创建 `run_entrance.sh`。

使用时应能够直接在终端执行 `bash run_entrance.sh`，不再手动输入必要参数。需要改变本次运行方式时，直接修改 Bash 脚本开头的默认参数，避免每次从终端重复组合长命令。

Bash 脚本仍只负责流程编排，项目级说明可以进一步约定 Bash、Bat 或其他入口脚本的变量位置和调用方式。

## 文档维护

文档维护参考远程仓库 `git@github.com:Linycs/Code_template.git` 中的：

- `_linycs/docs/doc-maintenance.md`
- `AGENTS.md`
