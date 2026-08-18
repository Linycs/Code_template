# AGENTS

use `/init` in AGENTS for directly create this doc.

## Global namespace

- conda_env: TODO
- git_branch: TODO
- code_entrance: run_entrance.sh / run_entrance.bat

## Global setting

1. 行为配置
   1. 所有回复都以 “Hello, linycs” 开头，回复均用中文。
   2. 当我没有明确说可以开始写代码的情况下，默认都先给方案
      1. 给方案的时候，涉及代码调整的部分不要模棱两可的说思路，至少需要将修改的代码文件/类/函数/位置简要说明。
2. 代码风格
   1. 参数配置
      1. 所有全局参数在 `code/configs/default.yaml` 中编写
      2. `default.yaml` 用 `CfgParser` 类读取，后续传参也尽量使用 `CfgParser`，减少函数写死或重复传入默认参数
   2. 面向对象编程
      1. 代码: 如果一个函数的代码量达到100行及以上的量级，则需要评估是否独立成一个类
      2. 配置信息: `default.yaml` 这类配置文件中某个字段的子属性数量过多，且归属的功能不一致，则需要考虑继续分组
      3. 函数/配置信息复用: 对于已有的函数、类、配置信息，如修改内容较少可做复用，则尽量复用。若功能接近但复用会导致代码大量改动，考虑将功能调整为类，或暂时避免复用，不确定的情况下应与我确认。
      4. 部分场景下的面向对象编程与数量有关，例如单/双/多视角的相机类、单/双数量的人/手参数化类。
   3. 调用层次
      1. code/utils 下的代码只能调用 code/utils 下的代码 或 python package 下的，不允许调用对项目中其他代码有依赖关系
   4. 临时测试与调试
      1. 一次性测试、调试所需的类和函数统一放在 `code/test_debug/`，该目录默认不进入 Git；需要长期保留的回归测试应放入单独的、受 Git 跟踪的 `tests/`。
      2. 测试期间可以从正式代码临时 import `code/test_debug/` 中的实现，并插入最小调用 hook；不要在 `code/test_debug/` 中复制一套完整主流程。
      3. 测试专用的统计、断言、日志和输出组织应收敛在 `code/test_debug/`；正式代码只传递测试确实需要的最小运行上下文，不承载测试分析逻辑。
      4. 正式代码中的临时 import、参数和调用必须使用成对的 `TEST_DEBUG_BEGIN` / `TEST_DEBUG_END` 注释标记，便于集中 review 和删除。
      5. 测试结束后应同时删除 `code/test_debug/` 中的一次性实现、正式代码中的全部临时 hook，以及仅为该测试增加的配置和依赖。
      6. 清理后运行 `rg -n "test_debug|TEST_DEBUG" code` 检查残留，并确认正式代码可在没有 `code/test_debug/` 实现的情况下独立运行。
      7. 不允许提交依赖被忽略 `code/test_debug/` 文件的正式代码。
   5. 易读性与代码精简
      1. 禁止过度数据校验
3. 信息更新
   1. 写代码需要附带注释
   2. 代码文档维护统一遵循 `_linycs/docs/doc-maintenance.md`
   3. 受代码变更维护的文档：
      1. `_linycs/docs/architecture.md`
      2. `_linycs/docs/design.md`
   4. 读取受维护文档时，只先读取开头的维护信息；按其管辖范围执行 freshness 检查后，再将正文作为当前代码依据
   5. 用户明确授权修改某受维护文档管辖范围内的代码时，该授权同时包含按维护规则判断为必要的文档同步，无需另行询问；该授权不扩展代码修改范围
   6. 修改完成后若判断文档无需更新，则保持文档不变，不通过无意义改动刷新其 Git 记录
   7. 任何对受维护文档本身的修改都必须同时完成 freshness 检查；提交该文档即表示其正文已按声明范围整体核对，不能只改局部链接或措辞而忽略已过时内容

## Repo setting

1. 代码说明
   1. 代码结构见 `_linycs/docs/architecture.md`
   2. 系统设计见 `_linycs/docs/design.md`
   3. 编程风格与设计原则见 `_linycs/docs/coding_style.md`
   4. 用户要求分析、检查、评估、给方案或询问建议时，只允许执行只读操作。
   5. 修改文件、创建文件、移动数据、安装依赖、运行会产生输出的程序前，必须获得用户对该事项的明确授权。
   6. 混合请求需要拆分：已明确授权的部分可以执行，其余部分只给方案。
   7. 授权仅覆盖用户明确指定的范围，不得自行扩展到相关但未授权的修改。
   8. 第一次写操作前，需要先说明“本轮授权范围”；如果没有明确授权，则给出方案并结束当前轮等待确认。
   9. 用户确认方案后才能执行；在 commentary 中描述方案不等于获得授权。
2. 运行配置
   1. conda运行环境: `conda_env`
   2. docker路径映射：
      1. docker外: /newdata/workspace_kaisheng
      2. docker内: /workspace
   3. 主程序入口: `code_entrance`
      1. bash/bat 文件没有用户明确要求时，默认使用 "顶部定义变量" + "代码运行使用变量" 的方式，而不是在终端运行 bash/bat 文件时传入变量
3. 分支配置
   1. 当前项目基于git进行管理
      1. 每次读取代码内容之前注意先 `git branch` 读取当前所在分支
   2. 当前分支: `git_branch`
4. 文件系统
   1. _linycs 用来放需要 git 追踪且与项目代码关联较弱的实验性代码、文档等
      1. 项目维护文档统一放在 `_linycs/docs/`
   2. _local 用来放不应被 git 追踪的本地运行代码、文档等
      1. _local/ai_log 用于存放 ai 工作过程的输出，文件格式为 "{Agent_name}_{timestamp}.log", 比如 claude_260731-140800.log
