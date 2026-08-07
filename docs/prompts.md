# prompts for daily coding

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
