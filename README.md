# QuickProject
## Project description

[![](https://img.shields.io/badge/version-0.5.84-green)]() [![](https://img.shields.io/badge/Author-RhythmLian-blue)]()

### 环境

- Qpro基于`gcc/g++/clang/...`与`python3`,
- 请确保电脑在拥有Python环境的同时, 至少安装了一套C/CPP编译指令.

### 功能

- 提供脚本在命令行里高效***运行C/CPP项目***。
- 提供***模板管理器***，轻松将代码保存和导出。
- 提供***对拍器***，轻松进行程序输出结果的对拍或进行文本文件的对比。

### 特殊说明

- **Qpro对CLion的特殊支持: 在CLion项目中，Qpro可以自动将其初始化为Qpro项目**

- **任意一个包含C/CPP文件的文件夹都可以成为Qpro项目, Qpro不会对原IDE项目产生影响**

- **一个文件夹可以同时是Qpro项目和其他IDE项目**


## 安装:

  - `pip3 install Qpro [--upgrade]`

## 使用:

| Command | Result |
| :----- | :----- |
| `Qpro -init` | 将当前文件夹初始化为Qpro项目 |
| `Qpro -h` | 查看帮助 |
| `Qpro -update` | 更新Qpro |
| `Qpro -adjust` | 修改配置表 |
| `Qpro -scp path` |将项目内文件夹或文件上传到默认服务器|
|`Qpro -scp-init`|将整个项目上传到默认服务器|
| `Qpro -c project` | 创建一个Qpro项目 |
| `tmpm *` | 调用[模板脚本](#模板脚本)，刷新项目中的默认源文件 |
| `run *` | 使用[运行脚本](#运行脚本)运行你的项目 |
| `detector [-[p/f][p/f]]` | 运行[对拍器](#对拍器)（对拍器只能在`Qpro -init`后的文件夹下运行） |

初始化后的项目，可以手动编辑配置表`project_configure.csv`来调整配置。

### 配置表

  - 修改`project_configure.csv`来调整脚本默认配置
  
      | 键值 | 含义 | 默认 |
      | :----- | :----- | :----- |
      | `compile_tool` | (编译工具, 编译后缀) | (gcc, '') / (g++, '') / ... |
      | `compile_filename` | 待编译的文件 | main.cpp / main.c |
      | `executable_filename` | 编译出的可执行文件名 | 项目名 |
      | `input_file` | 默认的输入文件 | `./cmake-build-debug/input.txt`|
      | `template_root` | 默认的模板库根目录 | `template/` |
      |`server_target`|默认的服务器映射位置|空/`user@ip:dir_path/`|

  - 运行`Qpro -adjust`修改配置表:
  ![GUI](https://github.com/Rhythmicc/QuickProject/blob/master/img/3.png?raw=true)
### 运行脚本:

  - 编译或运行
  
      | 参数 | 含义 |
      | :----- | :----- |
      | -b | 编译 |
      | -r | 运行 |
      | -br | 编译且运行 |
      
      如果上述三个命令都不存在，则默认运行当前编译好的程序
      
      | 参数 | 含义 |
      | :----- | :----- |
      | -f `*.c` / `*.cpp` | 设置目标源文件为`*.c` / `*.cpp` |

  - 输入输出:
    
      - 可以编辑 **默认的输入文件** 来设置默认输入
      - 运行 `run [...] > output.txt` 使程序输出到 `./output.txt`
      
      | 参数 | 效果 |
      | :----- | :----- |
      | -i | 使用**默认的输入文件**作为输入 |
      | -if `*.*` | 更改输入文件 |
      | -if -paste | 使用粘贴板内容作为输入 |
      
  - ***程序的额外命令行参数:***
  
      - ***所有未被run命令匹配的参数都将按顺序传递给源程序。***
      
  - 查看帮助
    
      - `run -h` : 可以查看使用帮助(Windows系统不支持颜色显示)
        ![help](https://github.com/Rhythmicc/QuickProject/blob/master/img/2.png?raw=true)
  
  - 推荐的命令示例:
    
      | 命令 | 效果 |
      | :----- | :----- |
      | `run -i` | 使用默认输入文件并运行 |
      | `run`| 运行 |
      | `run -br -i` |  编译且使用输入文件运行 |

### 模板脚本:

- 使用

  | 命令 | 效果 |
  |:---|:---|
  | `tmpm -h` | 查看帮助 |
  | `tmpm -r` | 选择备份并恢复 |
  | `tmpm -r backup` | 恢复为`template/backup` |
  | `tmpm -c backup` | 创建或覆盖`template/backup` |
  | `tmpm -c template algorithm` |拷贝指定位置, 创建模板集并写入算法|
  | `tmpm -a template algorithm` |拷贝指定位置, 向模板集追加算法|
  | `tmpm name`| 在`/// __TEMPLATE__`处插入`name`模板集内的模板|

- 关于指定位置: `tmpm` 将会把`compile_filename`中处于`/// __START__`和`/// __END__`之间的内容识别, 并拷贝

### 对拍器

  - 使用: `detector` 来进行两个源程序运行结果的对拍，结果存储在当前目录下的`./res.html`。

| 命令 | 效果 |
|:---|:---|
| `detector (-pp)` | 打开默认对拍器(`文件1`与`文件2`都是程序) |
| `detector -pf` | 运行`文件1`程序并将结果与`文件2`对比 |
| `detector -fp` | 运行`文件2`程序并将结果与`文件1`对比 |
| `detector -ff` | 对比`文件1`与`文件2`的内容(你可以在任何位置调用)|
  - 如果脚本未能自动打开`./res.html`, 你可以用浏览器打开它。

![GUI](https://github.com/Rhythmicc/QuickProject/blob/master/img/1.png?raw=true)
