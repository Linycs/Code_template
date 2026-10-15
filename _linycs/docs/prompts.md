# prompts for daily coding

## Global namespace

## 环境配置

1. 使用docker?
   1. 不使用：不必使用docker，创建conda环境即可
   2. 使用：创建docker file & docker-compose.yml，具体配置:`TODO`
2. conda环境
   1. 可创建新conda环境
   2. 不必严格遵循readme.md中的环境配置，分析是否可以适配本机 gpu & nvcc 版本
3. GUI
   1. 尽量避免使用GUI可视化，除非我明确要求，从而避免对渲染库、GUI界面的过多要求
   2. 可视化：对于2d序列输出，对每帧打上足够信息后加上帧索引，然后导出为视频。对于3d序列，至少需要保存几何信息。可视化的具体设置应与我确认
4. 环境配置
   1. 环境安装记录写入 _linycs/env/install.md
   2. 环境安装脚本写入 _linycs/env/install.sh，便于复现、分段执行和问题定位
5. 运行脚本
   1. 项目根目录下创建 run_lin.sh，填充项目demo运行命令，附带使用说明注释
6. 结果输出
   1. 缓存和临时文件存入 _local 下，其下code/放置临时代码，env/放置环境相关内容，output/放输出结果，根据需要可进一步分级

## 组合prompt

1. 开源项目运行：
   1. 读README.md, 配置必要的环境(e.g. conda配置或uv)和下载权重，并跑通项目提供的demo(最小验证即可，比如一个完整序列，不要下整个数据集). 不必严格遵循readme.md中的环境配置，主要是适配本机 gpu & nvcc 版本(e.g. 可参考 conda xxx 环境，有uv则直接用uv)，缓存和临时文件存入 _local 下，其下code/放置临时代码，env/放置环境相关内容，output/放输出结果，根据需要可进一步分级。配置环境之前，先检查必要的checkpoint等应存在/可下载，否则暂停配置环境等复现任务。对于数据和环境，应有分别的bash脚本管理，方便移植。
2. 重构
   1. 重构过程不确定、有歧义的部分应输出记录文档，等用户review
