---
sidebar_position: 1
---

# 快速开始

![menu](https://cos.rhythmlian.cn/ImgBed/ab671fdc0b86d7bed0f0043cea0955ff.png)

## 安装 QuickProject

```sh
pip3 install Qpro -U
```

> QuickProject（后简称 QPro），依赖`python3.7`或以上版本。

## 创建一个新项目

通过`Qpro create <项目名>`的方式，有三种渠道创建一个 QPro 项目。

1. 空白项目：此项目不包含任何代码，创建成功后项目内有一个`project_configure.json`文件，是 [QPro 的配置表](./QPro-Basics/Configure)，QPro 几乎完全依赖于此配置表工作。
2. 内置模板：QPro 提供了许多内置模板，它们有主流编程语言的`Hello World`实现样例，也有若干针对特定开发场景设计的`高级模板`。
3. 外部项目：此命令等价于`git clone <链接> <项目名>`。

如果您没有程序开发基础，为方便起见，可以选择`内置模板 -> python3`。

![select](https://cos.rhythmlian.cn/ImgBed/71ecc02ead4018fb7c3764287370dbe3.png)

如果希望此项目在远程服务器中使用，可以以此格式`用户@IP:路径`填写。

如已为 vscode 提供的`code`命令配置了环境变量，QPro 可以帮助自动使用 vscode 打开项目。

![vscode](https://cos.rhythmlian.cn/ImgBed/6ce853113ae7ebdb017a23e2d5a36ac7.png)

## Python 模板的项目结构

此处仅是为了更好地理解 QPro，并非所有模板都和`Python`模板类似，因此您需要阅读项目内的`README.md`文档。

![structure](https://cos.rhythmlian.cn/ImgBed/da6e7f6b82d34e813ea3fc6b38416e2f.png)

项目的树形结构如左侧展示，包含`dist`，`template`两个文件夹，通常`dist`文件夹存放结果或其它可执行程序，`template`文件夹存放您希望备份的代码文件，`project_configure.json`内容如下：

```json title="project_configure.json"
{
  "build": "",
  "entry_point": "main.py",
  "executable": "python3 main.py",
  "input_file": "dist/input.txt",
  "template_root": "template/",
  "server_targets": [
    {
      "user": "",
      "host": "",
      "port": 22,
      "path": ""
    }
  ]
}
```

此文件各处的含义可以参考[配置表](./QPro-Basics/Configure)部分。
