# 编程风格与设计原则

## 0. 定位

本文档定义本项目的编程思维、模块边界和代码审查标准，而不只是缩进、引号等表面格式。

总体目标是：以稳定的数据契约为边界，以单向分层控制依赖；通用模块处理数据形式，
业务模块解释数据内容；配置表达策略，类封装状态与行为，命名直接暴露语义。

---

## 1. 低耦合与复用优先

### 1.1 数据格式与业务内容解耦

通用模块只理解数据形式，不理解其业务含义：

| 数据形式 | 可能承载的内容 | 通用模块应理解的内容 |
|---|---|---|
| mask | hand、person、tool、object | shape、dtype、序列索引、压缩格式 |
| point cloud | hand surface、scene、object | 坐标、单位、valid、采样与邻域 |
| mesh | MANO、body、object | vertices、faces、坐标系 |
| image sequence | RGB、normal、residual、mask | 帧顺序、分辨率、编码与 tag |

如果把 `hand` 换成 `body`、`tool` 或 `object` 后，一个类仍然成立，那么该类的命名、
成员和接口中就不应写死 `hand`。业务语义由更上层的 adapter 或 preprocessor 解释。

例如：

- `PackedMaskCache` 只按 `stream_id` 保存 mask，不理解 left/right hand；
- `HandObservationPreprocessor` 负责生成手部 mask，并决定各 stream 的业务命名；
- mesh renderer 接受 mesh/camera/image，不依赖 MANO 或 HaMeR；
- depth loss 消费满足契约的点云 tensor，不依赖 FoundationStereo 的目录结构。

### 1.2 依赖稳定接口，不依赖内部状态

模块间优先传递 dataclass、tensor schema 或明确的公共方法，避免跨模块读取私有属性。
调用方只依赖它实际需要的最小接口，使上游算法或文件格式可以独立替换。

### 1.3 优先组合，谨慎继承

通用能力通过组合提供：业务类持有 cache、renderer、sequence 等对象并进行编排。
只有存在稳定的“is-a”关系和明确替换需求时才使用继承，不为减少少量重复建立复杂类树。

### 1.4 抽象以真实变化为依据

不因两个函数当前看起来相似就强行复用。只有当数据契约和变化方向一致时才抽象；
如果复用需要大量条件分支，说明它们通常不是同一职责。

---

## 2. 分层管理与单向依赖

### 2.1 推荐层次

```text
scripts / execute             入口与运行编排
        ↓
optim                         参数、loss、优化策略
        ↓
preprocess / dataio           观测准备与外部格式适配
        ↓
core                          通用几何与模型计算
        ↓
utils / Python packages       无业务基础能力
```

允许上层组合下层，禁止下层反向 import 上层。`preprocess` 与 `dataio` 可根据职责并列：
前者负责数据变换，后者负责外部格式和设备适配。二者不应包含优化策略。

`code/utils` 只能依赖自身或 Python package；设备、数据集和 HandFlow 相关逻辑不得下沉到
`utils` 或 `core`。

### 2.2 文件、类和函数的拆分标准

拆分首先依据“变化原因”，其次才是代码行数：

- 因文件格式变化而修改的逻辑放在 `dataio`；
- 因预处理算法变化而修改的逻辑放在 `preprocess`；
- 因几何公式变化而修改的逻辑放在 `core`；
- 因训练阶段或 loss 权重变化而修改的逻辑放在 `optim/config`。

一个类包含的逻辑若会因多种无关原因分别变化，应拆分职责。多个小函数若共享状态、
总是共同变化，则可以由一个类统一管理。

---

## 3. 面向对象与状态归属

类用于封装“稳定职责 + 相关状态”，不是简单地给函数加一层壳。

- 参数由参数拥有者管理，例如 MANO 参数统一归 `ManoProvider`；
- 单帧 RGB-D 状态归 `RGBDFrame`，序列编排归 `RGBDSequence`；
- cache 负责序列化状态，不负责生成数据；
- optimizer 负责优化编排，不负责解析外部数据格式。

可优化参数应只有一个权威实例。其他模块消费其 forward 结果，不复制参数，也不维护
含义相同的第二份状态。

---

## 4. 命名规范与可读性

### 4.1 基本规则

- 类名用名词表达职责：`RGBDFrame`、`RGBDSequence`、`PackedMaskCache`；
- 方法用动词表达行为：`load`、`sample`、`denoise`、`export_video`；
- 避免宽泛名称：`Manager`、`Helper`、`Data`、`process`，除非上下文已完全限定；
- 同一概念全项目使用同一名称，不随文件更换缩写。

### 4.2 几何名称必须暴露语义

涉及几何时，变量名或紧邻注释应明确：

- 坐标系：`points_world`、`vertices_camera`、`camera_to_world`；
- 单位：`depth_meter`、`threshold_mm`；
- 维度含义：`(H,T,N,3)`、`(V,H,T,J,2)`；
- 有效性层级：`point_valid`、`frame_valid`，不使用含糊的单一 `mask`；
- 参数作用范围：逐帧、逐手、全时域共享或全局共享。

命名应让读者在大多数情况下无需跳转到实现，就能判断数据的内容和作用域。

---

## 5. 配置与实现分离

配置表达策略，类执行策略，runtime object 保存运行状态。

- 路径、阈值、算法选择、stage 参数开关和 loss 权重放入 config；
- tensor、点云、optimizer state 等运行状态不放入静态 config；
- 全局配置通过 `CfgParser` 共享，避免函数层层传递零散标量；
- 派生值在一个权威位置计算，避免多个模块分别解释同一配置；
- 参数配置采用严格 schema：缺字段、未知字段、错误类型均应尽早报错；
- 单位和合法范围应在配置注释及校验中明确。

算法默认值与具体数据集路径可以分别维护，再由 planner 合并为最终配置快照；运行中的
所有模块仍只消费同一个 `CfgParser`。

---

## 6. 数据契约优先

在实现算法前先固定模块间的数据契约。契约至少应说明：

- shape 和各维含义；
- dtype、device、坐标系和单位；
- 帧序、视角和 stream 的对齐方式；
- padding 的填充值与 valid mask；
- confidence 的范围、作用层级和聚合方式；
- 空数据、缺帧和错误输入的处理规则。

例如优化层只依赖 `SampledDepthPoints`，不应理解 mask NPZ、深度文件名或点云去噪算法。
这样替换深度来源、采样方法或 cache 格式时，depth loss 无需修改。

---

## 7. 显式性、错误处理与日志

- 优先 fail fast；不使用 silent fallback 掩盖配置、shape 或帧序错误；
- 会改变数学语义的默认行为必须谨慎，参数开关应显式声明；
- 对可恢复的数据缺失使用 valid/confidence 表达，对契约错误直接抛异常；
- 日志记录关键 shape、有效帧数、点数分布、坐标系、单位和配置快照；
- 不用重复采样、零填充或默认值伪装成真实有效观测。

---

## 8. 测试与验证

研究代码优先测试高风险不变量，而不是只追求覆盖率：

- tensor shape 和广播方向；
- world/camera 坐标变换及米/mm 单位；
- pack/unpack、save/load 的无损往返；
- padding、invalid frame 不进入 loss；
- stage 参数开关只让目标参数获得梯度；
- 导出几何与 forward 几何一致；
- 新实现不改变关闭功能时的原有结果。

通用模块使用小型合成数据做单元测试，数据适配层再使用少量真实帧做集成测试。

---

## 9. Review 检查表

提交代码前检查：

1. 类名是否混入了本不属于它的业务内容？
2. 下层模块是否反向依赖上层或具体数据集？
3. 同一参数或状态是否出现了多个权威副本？
4. 配置是否显式、完整并经过类型/范围校验？
5. 名称是否说明坐标系、单位、维度和作用范围？
6. 模块间的数据契约是否足以独立替换实现？
7. invalid、padding、缺帧和空输入是否有明确语义？
8. 是否验证了梯度、坐标和序列对齐等高风险不变量？
