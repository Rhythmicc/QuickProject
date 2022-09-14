---
sidebar_position: 3
---

# 命令 APP 框架

基于命令装饰类，你可以轻松开发`支持跨平台`、`样式丰富`的命令行工具。

## 快速开始

```python
from QuickProject.Commander import Commander
from QuickProject import QproDefaultConsole as console

app = Commander()


@app.command()
def hello(name: str, color: str = 'cyan'):
    """
    echo Hello <name>

    :param name: str
    :param color: str
    """
    console.print(f"Hello [bold {color}]{name}[/]!")


def main():
    """
    注册为全局命令时, 默认采用main函数作为命令入口, 请勿将此函数用作它途.
    When registering as a global command, default to main function as the command entry, do not use it as another way.
    """
    app()


if __name__ == '__main__':
    main()

```

### 样例

> ```sh
> qrun --help
> ```
>
> ![](https://cos.rhythmlian.cn/ImgBed/c138ff47c2e21cf329f315db746d60ab.png)
>
> ```sh
> qrun hello world
> ```
>
> ![](https://cos.rhythmlian.cn/ImgBed/ef75e5e6f8ccc587b08d48bb0a364ead.png)
>
> ```sh
> qrun hello world --color red
> ```
>
> ![](https://cos.rhythmlian.cn/ImgBed/ea3839a84ba5a2c0f35ee1345aea6cce.png)

## 创建自己的命令工具

通过`Qpro create <项目名>`命令，在`内置模板`中查询并选择`commander`以创建。

下面是 Commander 对 Python 基本类型的支持能力:

1. Commander 完整支持`str`, `int`, `float`, `bool`类型的参数。

:::tip

Commander 对 bool 类型的参数支持方式

:::

> 当 bool 类型的参数为必填参数时
>
> - 这些值将被判定为 True：`[True, 'True', 'true', 'yes', 1, 't', 'T', 'y', 'Y']`
> - 这些值将被判定为 False: `[False, 'False', false, 'n', 0, 'f', 'F', 'n', 'N']`
>
> 当 bool 类型的参数为可选参数时（假设参数名为`flag`)
>
> - 推荐（强制要求）flag 默认设为 False。
> - 在调用时加入`--flag`标志时，Commander 将把其解释为设置 flag 为 True。

2. Commander 对 list 类型的参数支持方式

:::caution
list 类型仅支持设置为必填参数，且在调用时必须在命令的末尾赋值。
:::

> 现假设 list 的参数命名为`ops`，则赋值方式为: `qrun <sub_cmd> [若干其他参数] -ops a b c d`，此样例命令中的`a b c d`都将作为字符串传递给 ops 列表。

:::danger
Commander 暂不支持解析`dict`, `set`类型的参数（未来也不打算支持）。
:::

## 将 Commander 应用注册为全局命令

想随处运行自己刚刚开发的命令吗？将它注册为全局命令叭！

```sh
Qpro register
```

### 第一次注册全局命令

1. 你需要创建一个“Qpro 全局文件夹”，比如`~/.local/QuickProject/`，并将其作为`QproGlobalDir`的环境变量。

   ```sh
   mkdir ~/.local/QuickProject
   # 打开你的 .*shrc 文件
   vim .zshrc
   # 填入如下内容
   export QproGlobalDir="$HOME/.local/QuickProject"
   ```

2. 设置`$PATH`, 用于执行 Qpro 注册的全局命令。

   ```sh
   # 打开你的 .*shrc 文件
   vim .zshrc
   # 填入如下内容
   export PATH="$PATH:$QproGlobalDir/bin"
   ```

注册方式：`Qpro register`

## 自动补全脚本生成与应用

进入 Commander APP 文件夹下执行`Qpro gen-complete`，将创建一个`complete`文件夹并生成 ZSH 和 FIG 的补全插件，你需要手动将它们拷贝至相应位置并应用。通常：

Fig 脚本路径为`~/.fig/user/autocomplete/src`或`~/.fig/autocomplete/src`，执行`npm run build` 应用。

ZSH 脚本路径为`$fpath`，通常为`/usr/local/share/zsh/site-functions`。

### 自定义补全内容

Commander 会自动解析函数头部的注释部分，比如在上述的样例程序中，补全内容为:

![](https://cos.rhythmlian.cn/ImgBed/21130e4348e4e51309c817e18e885f0c.png)

### 自定义可选项

将上述样例代码改为如下内容（添加了`@app.custom_complete('color')`修饰的`hello`函数），则在 Fig 的补全中会限制 color 的内容。(注意，`custom_complete`必须在子命令之前定义才会生效)

```python
from QuickProject.Commander import Commander
from QuickProject import QproDefaultConsole as console

app = Commander()

@app.custom_complete('color')
def hello():
    """
    自定义补全函数, 请勿将此函数用作它途.
    Custom completion function, do not use it as another way.
    """
    return ['red', 'green', 'blue', 'cyan', 'magenta', 'yellow', 'black', 'white']


@app.command()
def hello(name: str, color: str = 'cyan'):
    """
    echo Hello <name>

    :param name: str
    :param color: str
    """
    console.print(f"Hello [bold {color}]{name}[/]!")


def main():
    """
    注册为全局命令时, 默认采用main函数作为命令入口, 请勿将此函数用作它途.
    When registering as a global command, default to main function as the command entry, do not use it as another way.
    """
    app()


if __name__ == '__main__':
    main()

```

## 有哪些基于 Commander 开发的 APP？

| 链接                                            | 描述                                                  |
| ----------------------------------------------- | ----------------------------------------------------- |
| https://github.com/Rhythmicc/jav                | Jav 工具箱                                            |
| https://github.com/Rhythmicc/CUP_Network        | 一个 selenium 脚本，用于在命令行中登录 CUP 校园网。   |
| https://github.com/Rhythmicc/pypi               | A pypi Assistant for QproPypiTemplate                 |
| https://github.com/Rhythmicc/DrawMtxAsThumbnail | 绘制 mtx 的缩略图                                     |
| https://github.com/Rhythmicc/Amy                | 本地的 Amy Surge 订阅链接转换，并保存至腾讯云对象存储 |
| https://github.com/Rhythmicc/orders             | 你的程序代写订单助手                                  |
| https://github.com/Rhythmicc/ClassFlower        | 小红花榜                                              |
| https://github.com/Rhythmicc/tgpd               | 在终端里下载和预览 telegra.ph 文章里的套图！          |
