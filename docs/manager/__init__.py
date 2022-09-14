# -*- coding: utf-8 -*-

name = 'manager'

from .__config__ import *

config: managerConfig = None
if enable_config:
    config = managerConfig()

import sys
from QuickProject import user_pip, _ask


def external_exec(cmd: str, without_output: bool = False):
    """
    外部执行命令

    :param cmd: 命令
    :param without_output: 是否不输出
    :return: status code, output
    """
    from subprocess import Popen, PIPE
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, encoding='utf-8')
    ret_code = p.wait()
    stdout, stderr = p.communicate()
    content = stdout.strip() + stderr.strip()
    if ret_code and content and not without_output:
        QproDefaultConsole.print(content)
    elif content and not without_output:
        QproDefaultConsole.print(content)
    return ret_code, content


def requirePackage(pname: str,
                   module: str = "",
                   real_name: str = "",
                   not_exit: bool = True,
                   not_ask: bool = False,
                   set_pip: str = user_pip):
    """
    获取本机上的python第三方库，如没有则询问安装

    :param not_ask: 不询问，无依赖项则报错
    :param set_pip: 设置pip路径
    :param pname: 库名
    :param module: 待引入的模块名，可缺省
    :param real_name: 用于 pip3 install 的名字
    :param not_exit: 安装后不退出
    :return: 库或模块的地址
    """
    try:
        exec(f'from {pname} import {module}' if module else f"import {pname}")
    except (ModuleNotFoundError, ImportError):
        if not_ask:
            return None
        if _ask({
                'type': 'confirm',
                'message':
                f"""{name} require {pname + (' -> ' + module if module else '')}, confirm to install?
  {name} 依赖 {pname + (' -> ' + module if module else '')}, 是否确认安装?""",
                'default': True
        }):
            with QproDefaultConsole.status(
                    'Installing...' if user_lang != 'zh' else '正在安装...'):
                external_exec(
                    f'{set_pip} install {pname if not real_name else real_name} -U',
                    True)
            if not_exit:
                exec(f'from {pname} import {module}'
                     if module else f"import {pname}")
            else:
                QproDefaultConsole.print(
                    QproInfoString, f'just run again: "{" ".join(sys.argv)}"' if user_lang != 'zh' else f'请重新运行: "{" ".join(sys.argv)}"'
                )
                exit(0)
        else:
            exit(-1)
    finally:
        return eval(f'{module if module else pname}')
