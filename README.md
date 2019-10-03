# QuickProject
## Project description

[![](https://img.shields.io/badge/version-0.3.6-green)]()
[![](https://img.shields.io/badge/Author-RhythmLian-blue)]()

## 安装:

  - `pip3 install Qpro [--upgrade]`

## 使用:

| Command | Result |
| :----- | :----- |
| `Qpro -init` | 为项目添加[配置表](#配置表)和相关文件，令下面命令可执行 |
| `refresh` | 调用[刷新脚本](#刷新脚本)，刷新项目中的默认源文件 |
| `run *` | 使用[运行脚本](#运行脚本)运行你的项目 |
| `detector [-[p/f][p/f]]` | 运行[对拍器](#对拍器)（对拍器只能在`Qpro -init`后的文件夹下运行） |

添加配置表后的项目，可以手动编辑`project_configure.csv`来调整配置。

### 配置表

  - 修改`project_configure.csv`来调整脚本默认配置
  
      | 键值 | 含义 | 默认 |
      | :----- | :----- | :----- |
      | `compile_tool` | (编译工具, 编译后缀) | (gcc, '') / (g++, '') / ... |
      | `compile_filename` | 待编译的文件 | main.cpp / main.c |
      | `executable_filename` | 编译出的可执行文件名 | 项目名 |
      | `input_file` | 默认的输入文件 | `./cmake-build-debug/input.txt`|
      | `template_file` | 默认的快照位置 | `template/main` |

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
    
      - 可以编辑 `./cmake-build-debug/input.txt` 来设置默认输入
      - 运行 `run [...] > output.txt` 使程序输出到 `./output.txt`
      
      | 参数 | 效果 |
      | :----- | :----- |
      | -i | 使用`./cmake-build-debug/input.txt`作为输入 |
      | -if `*.*` | 更改输入文件 |
      | -if -paste | 使用粘贴板内容作为输入 |
      
  - 程序的额外命令行参数:
  
      - 在符合上述命令规则情况下，你可以在任意位置加入参数，这些参数将传递给编译出的程序。
      
  - 查看帮助
    
      - `run -h` : 可以查看使用帮助(Windows系统不支持颜色显示)
        ![help](https://github.com/Rhythmicc/QuickProject/blob/master/img/2.png?raw=true)
  
  - 推荐的命令示例:
    
      | 命令 | 效果 |
      | :----- | :----- |
      | `run -i` | 使用默认输入文件并运行 |
      | `run`| 运行 |
      | `run -br -i` |  编译且使用输入文件运行 |

### 刷新脚本:

  - 运行 `refresh` 来初始化 `main.cpp` 为存储在 `./template/main` 文件中的内容。

### 对拍器

  - 使用: `detector` 来进行两个源程序运行结果的对拍，结果存储在当前目录下的`./res.html`。
  
  | 命令 | 效果 |
  |:---|:---|
  | `detector (-pp)` | 打开默认对拍器(`文件1`与`文件2`都是程序) |
  | `detector -pf` | 运行`文件1`程序并将结果与`文件2`对比 |
  | `detector -fp` | 运行`文件2`程序并将结果与`文件1`对比 |
  | `detector -ff` | 对比`文件1`与`文件2`的内容 |
  - 如果脚本未能自动打开`./res.html`, 你可以用浏览器打开它。
    ![GUI](https://github.com/Rhythmicc/QuickProject/blob/master/img/1.png?raw=true)
