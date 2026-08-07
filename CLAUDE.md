# CLAUDE

use `/init` in CLAUDE for directly create this doc.

## Global namespace

- USER: TODO
- conda_env: TODO
- git_branch: TODO
- code_entrance: TODO

## Global setting

1. 行为配置
   1. 所有回复都以 “Hello, `USER`” 开头，回复均用中文。
   2. 当我没有明确说可以开始写代码的情况下，默认都先给方案
      1. 给方案的时候，涉及代码调整的部分不要模棱两可的说思路，至少需要将修改的代码文件/类/函数/位置简要说明。
2. 代码风格
   1. 参数配置
      1. 所有全局参数在 config.yaml 中编写
      2. config.yaml 用一个config类进行读取，后续传参也尽量用 config 类传参，减少函数写死或写了默认的传入参数
   2. 面向对象编程
      1. 代码: 如果一个函数的代码量达到100行及以上的量级，则需要评估是否独立成一个类
      2. 配置信息: config.yaml 这类配置文件中某个字段的子属性数量过多，且归属的功能不一致，则需要考虑进行继续分组
      3. 函数/配置信息复用: 对于已有的函数、类、配置信息，如修改内容较少可做复用，则尽量复用。若功能接近但复用会导致代码大量改动，考虑将功能调整为类，或暂时避免复用，不确定的情况下应与我确认。
      4. 部分场景下的面向对象编程与数量有关，例如单/双/多视角的相机类、单/双数量的人/手参数化类。
   3. 调用层次
      1. code/utils 下的代码只能调用 code/utils 下的代码 或 python package 下的，不允许调用对项目中其他代码有依赖关系
3. 信息更新
   1. 写代码需要附带注释
   2. 每次写完代码后咨询是否将代码调整写入结构文档(e.g. docs/architecture.md)

## Repo setting

1. 代码说明
   1. 代码结构见 docs/architecture.md
2. 运行配置
   1. conda运行环境: `conda_env`
   2. docker路径映射：
      1. docker外: /newdata/workspace_kaisheng
      2. docker内: /workspace
   3. 主程序入口: `code_entrance`
3. 分支配置
   1. 当前项目基于git进行管理
      1. 每次读取代码内容之前注意先 `git branch` 读取当前所在分支
   2. 当前分支: `git_branch`
4. 文件系统
   1. _`USER` 用来放需要 git 追踪且与项目代码关联较弱的实验性代码、文档等
   2. _local 用来放不应被 git 追踪的本地运行代码、文档等
      1. _local/ai_log 用于存放 ai 工作过程的输出，文件格式为 "{Agent_name}_{timestamp}.log", 比如 claude_260731-140800.log
