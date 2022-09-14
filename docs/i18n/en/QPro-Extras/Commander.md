---
sidebar_position: 2
---

# 命令行 APP 框架文档

正如前述的 Commander 样例中，一个 Commander APP 需要被设定一个入口，以便于它被注册至全局命令亦或者方便从 Pypi 安装。

因此，一个经典的 Commander APP 的目录结构为（以 test 为例）:

```sh title="tree"
📂 .
├── 📂 dist
│   └── 📒 input.txt
├── 📒 project_configure.json
├── 📒 README.md
├── 📂 template
│   └── 📒 main
└── 📂 test
    ├── 📒 __config__.py
    ├── 📒 __init__.py
    └── 📒 main.py
```

它的配置表内容为

```json title="project_configure.json"
{
  "build": "",
  "entry_point": "test/main.py",
  "executable": "python3 -m test.main",
  "input_file": "dist/input.txt",
  "template_root": "template/",
  "server_targets": [
    {
      "user": "",
      "host": "",
      "port": 22,
      "path": ""
    }
  ],
  "enable_complete": true
}
```

:::caution
`executable`部分的`python3 -m test.main`，它的作用是调用`test`包下的`main.py`文件中的`if __name__ == '__main__'`部分；但依据 python 的执行机制，它会先扫描第三方库中的内容，如果`test`与其他第三方库产生冲突，建议换一个名字。
:::

接下来将阐述`test`包下的内容。

## `test/__config__.py`

此文件是 Commander 模板提供，用于帮助命令行 APP 在本地存储配置信息的部分。它的内容为:

```python title="test/__config__.py"
import os
import json
from QuickProject import user_root, user_lang, QproDefaultConsole, QproInfoString, _ask

enable_config = False
config_path = os.path.join(user_root, ".test_config")

questions = {
    'name': {
        'type': 'input',
        'message': 'What is your name?',
    },
}

def init_config():
    with open(config_path, "w") as f:
        json.dump({i: _ask(questions[i]) for i in questions}, f, indent=4, ensure_ascii=False)
    QproDefaultConsole.print(QproInfoString, f'Config file has been created at: "{config_path}"' if user_lang != 'zh' else f'配置文件已创建于: "{config_path}"')


class testConfig:
    def __init__(self):
        if not os.path.exists(config_path):
            init_config()
        with open(config_path, "r") as f:
            self.config = json.load(f)

    def select(self, key):
        if key not in self.config and key in questions:
            self.update(key, _ask(questions[key]))
        return self.config[key]

    def update(self, key, value):
        self.config[key] = value
        with open(config_path, "w") as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)
```

从引入相关包以后，可以选择:

1. 项目是否启用配置文件（默认为不启用）
2. 设置配置文件存储位置（默认为用户根目录下的`.<项目名>_config`，并以 json 格式存储）
3. 自定义问题。

### 自定义问题

如上述代码所见，在`questions`字典中加入你需要在配置表存储的键值对，即可添加问题。

以下是问题的类型，你可以参照此[问题样例](https://github.com/CITGuru/PyInquirer#examples)来添加，常见的问题种类包括`input`（用户自行输入一串文本）、`list`（单选）、`checkbox`（多选）、`confirm`（是或否）。

## `test/__init__.py`

此文件提供若干基础 API，比如`引用依赖`的询问安装，`执行命令`等，如果启用了配置表，则可全局使用`config`对象来获取配置表信息。

## `test/main.py`

此文件是命令行 APP 的入口文件，它的结构如下

```python title="test/main.py"
from QuickProject.Commander import Commander


app = Commander()


@app.command()
def hello(name: str):
    """
    echo Hello <name>

    :param name: str
    """
    print(f"Hello {name}!")


def main():
    """
    注册为全局命令时, 默认采用main函数作为命令入口, 请勿将此函数用作它途.
    When registering as a global command, default to main function as the command entry, do not use it as another way.
    """
    app()


if __name__ == '__main__':
    main()
```

你可以实现多个函数，并用`@app.command()`来装饰它们，将它们变为 Commander APP 的子命令。

在调用方面，必填参数需要按顺序填写、可选参数需要以`--<参数名> balabala`方式设置。

:::danger 重要提示
Commander 不会支持解析 dict 和 set 类型的参数。
:::

### 自定义前置操作

您可能有一类子命令，它们的参数表一样，并且在开始工作前会先进行几乎一致的判断步骤（比如某文件是否存在、某前提是否满足等等），重复写这些逻辑是很烦人的，因此 Commander 支持绑定前置函数来实现。

在`app()`被调用前，添加你需要绑定的函数：

:::caution
前置函数的参数表需要与被绑定的子命令参数表保持一致，且前置函数需要返回 bool 类型来表示是否验证成功。
:::

```python
from QuickProject.Commander import Commander


app = Commander()

def check_hello(name: str):
    return name in ['Alice', "Bob", "Candy", "David"]

@app.command()
def hello(name: str):
    """
    echo Hello <name>

    :param name: str
    """
    print(f"Hello {name}!")


def main():
    """
    注册为全局命令时, 默认采用main函数作为命令入口, 请勿将此函数用作它途.
    When registering as a global command, default to main function as the command entry, do not use it as another way.
    """
    app.bind_pre_call('hello', check_hello)
    app()


if __name__ == '__main__':
    main()
```

### 调用其他子命令

当您想在当前子命令的实现中，调用之前实现的子命令，是无法通过直接调用被装饰的函数来实现的（因为它被`@app.command()`装饰起来了）。

因此可以：`app.real_call('command', *args, **kwargs)`来调用。

### 自定义补全提示

APP 某个子命令的参数可能是几个固定值中的一个，您可能希望在补全时直接提示这几个候选项。

```python
from QuickProject.Commander import Commander

app = Commander()


@app.custom_complete('name')
def hello():
    return ['Alice', "Bob", "Candy", "David"]
    # 或者
    return [
        {
            'name': 'Alice',
            'description': 'Alice',
            'icon': '👩'
        },
        {
            'name': 'Bob',
            'description': 'Bob',
            'icon': '👨'
        },
        {
            'name': 'Candy',
            'description': 'Candy',
            'icon': '👧'
        },
        {
            'name': 'David',
            'description': 'David',
            'icon': '👦'
        },
    ]


@app.command()
def hello(name: str):
    """
    echo Hello <name>

    :param name: str
    """
    print(f"Hello {name}!")


def main():
    """
    注册为全局命令时, 默认采用main函数作为命令入口, 请勿将此函数用作它途.
    When registering as a global command, default to main function as the command entry, do not use it as another way.
    """
    app()


if __name__ == '__main__':
    main()

```
