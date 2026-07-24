# CLAUDE

use `/init` in CLAUDE for directly create this doc.

## Global setting

1. 行为配置
   1. 所有回复都以 “Hello, `TODO`” 开头，回复均用中文。
   2. 当我没有明确说可以开始写代码的情况下，默认都先给方案
2. 代码风格
   1. 参数配置
      1. 所有全局参数在 config.yaml 中编写
      2. config.yaml 用一个config类进行读取，后续传参也尽量用 config 类传参，减少函数写死或写了默认的传入参数
   2. 面向对象编程
      1. 代码: 如果一个函数的代码量达到100行及以上的量级，则需要评估是否独立成一个类
      2. 配置信息: config.yaml 这类配置文件中某个字段的子属性数量过多，且归属的功能不一致，则需要考虑进行继续分组
   3. 调用层次
      1. code/utils 下的代码只能调用 code/utils 下的代码 或 python package 下的，不允许调用对项目中其他代码有依赖关系
3. 信息更新
   1. 写代码需要附带注释
   2. 每次写完代码后咨询是否将代码调整写入结构文档(e.g. docs/architecture.md)

## Repo setting

1. 代码说明
   1. 代码结构见 docs/architecture.md
2. 运行配置
   1. conda运行环境: `TODO`
   2. docker路径映射：
      1. docker外: /newdata/workspace_kaisheng
      2. docker内: /workspace
   3. 主程序入口: `TODO`
3. 分支配置
   1. 当前项目基于git进行管理
   2. 当前分支: `TODO`
