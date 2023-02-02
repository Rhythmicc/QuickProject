from .__config__ import (
    _ask,
    _qpro_config,
    _lang,
    QproDefaultConsole,
    QproDefaultStatus,
    user_root,
    user_lang,
    dir_char,
    os,
    sys,
)

user_pip = _qpro_config.select("default_pip")
using_gitee = _qpro_config.select("using_gitee")
QproErrorString = f'[bold red][{_lang["error"]}][/]'
QproInfoString = f'[bold cyan][{_lang["information"]}][/]'
QproWarnString = f'[bold yellow][{_lang["warning"]}][/]'
name = "QuickProject"
configure_name = "project_configure.json"


def __latest_filename(filename):
    """
    获取最近的文件名 （不断向父目录遍历）

    :param filename: 文件名
    :return: 文件路径
    """
    cur = os.getcwd()
    while cur != os.path.dirname(cur):
        if os.path.exists(_path := os.path.join(cur, filename)):
            return _path
        cur = os.path.dirname(cur)
    if os.path.exists(_path := os.path.join(cur, filename)):
        return _path
    return ""


if " ".join(sys.argv[:2]) != "Qpro init":
    rt_dir = os.path.dirname(__latest_filename(configure_name)) + dir_char
    if rt_dir == dir_char:
        rt_dir = os.path.abspath(".") + dir_char
else:
    rt_dir = os.path.abspath(".")
project_configure_path = rt_dir + configure_name


def __sub_path(path, isExist=True):
    """
    计算路径在项目中的相对路径

    :param path: 路径
    :param isExist: 是否存在
    :return: 相对路径
    """
    if not os.path.exists(path) and isExist:
        return ""
    abs_path = os.path.abspath(path)
    return abs_path.replace(rt_dir, "") if abs_path.startswith(rt_dir) else ""


def remove(path):
    """
    删除文件或目录

    :param path: 路径
    :return:
    """

    if os.path.exists(path):
        if os.path.isdir(path):
            import shutil

            shutil.rmtree(path)
        else:
            os.remove(path)


def external_exec(
    cmd: str,
    without_output: bool = False,
    without_stdout: bool = False,
    without_stderr: bool = False,
    __expose: bool = False,
    __no_wait: bool = False,
):
    """
    外部执行命令

    :param cmd: 命令
    :param without_output: 是否不输出
    :param without_stdout: 是否不输出stdout
    :param without_stderr: 是否不输出stderr
    :param __expose: ⚠️是否暴露, 这意味着命令行输出可能会被截断和修改
    :param __no_wait: ⚠️是否不等待, 这意味着需要手动获取返回值和输出
    :return: status code, output | __no_wait 为 True 时返回进程对象
    """
    from rich.markdown import Markdown
    from subprocess import Popen, PIPE
    from concurrent.futures import ThreadPoolExecutor, wait

    class MixContent:
        def __init__(self):
            self.content = ""

        def __add__(self, other):
            self.content += other
            return self

        def __str__(self):
            return self.content

    content = MixContent()

    def _output(pipe_name: str, process: Popen, content: MixContent):
        ignore_status = (
            without_stdout if pipe_name == "stdout" else without_stderr
        ) or without_output
        for line in iter(eval(f"process.{pipe_name}.readline"), ""):
            if not __expose and (
                line.startswith("__START__")
                or line.startswith("__STOP__")
                or line.startswith("__SPLIT__")
            ):
                continue
            content += line
            if ignore_status:
                continue
            line = line.strip()
            if __expose and line.startswith("__START__"):
                QproDefaultStatus(line.replace("__START__", "")).start()
            elif __expose and line.startswith("__STOP__"):
                QproDefaultStatus.stop()
            elif __expose and line.startswith("__SPLIT__"):
                QproDefaultConsole.print(
                    Markdown("# " + line.replace("__SPLIT__", "").strip())
                )
            else:
                QproDefaultConsole.print(line)

    pool = ThreadPoolExecutor(2)
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, bufsize=1, encoding="utf-8")

    if __no_wait:
        return p

    wait(
        [
            pool.submit(_output, "stdout", p, content),
            pool.submit(_output, "stderr", p, content),
        ]
    )
    pool.shutdown()
    ret_code = p.wait()

    return ret_code, str(content)


def requirePackage(
    pname: str,
    module: str = "",
    real_name: str = "",
    not_exit: bool = True,
    not_ask: bool = False,
    set_pip: str = user_pip,
):
    """
    获取本机上的python第三方库

    :param pname: 库名
    :param module: 待引入的模块名，可缺省
    :param real_name: 用于 pip3 install 的名字
    :param not_exit: 安装后不退出
    :param not_ask: 不询问
    :param set_pip: pip3的路径
    :return: 库或模块的地址
    """
    try:
        exec(f"from {pname} import {module}" if module else f"import {pname}")
    except (ModuleNotFoundError, ImportError):
        if not_ask:
            return None
        if _ask(
            {
                "type": "confirm",
                "message": f"""Qpro require {pname + (' -> ' + module if module else '')}, confirm to install?"""
                if user_lang != "zh"
                else f"""Qpro 依赖 {pname + (' -> ' + module if module else '')}，确认安装吗？""",
                "default": True,
            }
        ):
            with QproDefaultStatus(
                f"Installing {pname if not real_name else real_name}"
                if user_lang != "zh"
                else f"正在安装 {pname if not real_name else real_name}"
            ):
                st, _ = external_exec(
                    f"{set_pip} install {pname if not real_name else real_name} -U",
                    True,
                )
            if st:
                QproDefaultConsole.print(
                    QproErrorString,
                    f"Install {pname + (' -> ' + module if module else '')} failed, please install it manually: "
                    if user_lang != "zh"
                    else f"安装 {pname + (' -> ' + module if module else '')} 失败，请手动安装: ",
                    f"'{set_pip} install {pname if not real_name else real_name} -U'",
                )
                exit(-1)
            if not_exit:
                exec(f"from {pname} import {module}" if module else f"import {pname}")
            else:
                QproDefaultConsole.print(
                    QproInfoString,
                    "Install complete! Run again:"
                    if user_lang != "zh"
                    else f"安装完成！再次运行:",
                    " ".join(sys.argv),
                )
                exit(0)
        else:
            exit(-1)
    return eval(f"{module if module else pname}")


class SshProtocol:
    @staticmethod
    def post_folder(user, domain, target, port, srcPath, dstPath):
        """
        发送目录

        scp -P {port} -r {srcPath} {user}@{domain}:{target}/{dstPath}

        :param user: 用户名，可省略
        :param domain: 目标机器地址
        :param target: 远程映射路径
        :param port: 端口
        :param srcPath: 本地文件路径
        :param dstPath: 远程映射子路径
        :return: 发送状态
        """
        if user:
            status = os.system(
                "scp -P %s -r %s %s"
                % (
                    port,
                    srcPath,
                    user + "@\\[" + domain + "\\]:" + os.path.join(target, dstPath),
                )
            )
        else:
            status = os.system(
                "scp -P %s -r %s %s"
                % (
                    port,
                    srcPath,
                    "\\[" + domain + "\\]:" + os.path.join(target, dstPath),
                )
            )
        return status

    @staticmethod
    def post_file(user, domain, target, port, srcPath, dstPath):
        """
        发送文件

        scp -P {port} {srcPath} {user}@{domain}:{target}/{dstPath}

        :param user: 用户名，可省略
        :param domain: 目标机器地址
        :param target: 远程映射路径
        :param port: 端口
        :param srcPath: 本地文件路径
        :param dstPath: 远程映射子路径
        :return: 发送状态
        """
        if user:
            status = os.system(
                "scp -P %s %s %s"
                % (
                    port,
                    srcPath,
                    user + "@\\[" + domain + "\\]:" + os.path.join(target, dstPath),
                )
            )
        else:
            status = os.system(
                "scp -P %s %s %s"
                % (
                    port,
                    srcPath,
                    "\\[" + domain + "\\]:" + os.path.join(target, dstPath),
                )
            )
        return status

    @staticmethod
    def post_all_in_folder(user, domain, target, port, dstPath):
        """
        发送当前目录

        scp -P {port} -r * {user}@{domain}:{target}/{dstPath}

        :param user: 用户名，可省略
        :param domain: 目标机器地址
        :param target: 远程映射路径
        :param port: 端口
        :param srcPath: 本地文件路径
        :param dstPath: 远程映射子路径
        :return: 发送状态
        """
        if user:
            status = os.system(
                "scp -P %s -r * %s"
                % (
                    port,
                    user + "@\\[" + domain + "\\]:" + os.path.join(target, dstPath),
                )
            )
        else:
            status = os.system(
                "scp -P %s -r * %s"
                % (port, "\\[" + domain + "\\]:" + os.path.join(target, dstPath))
            )
        return status

    @staticmethod
    def get_file_or_folder(user, domain, target, port, srcPath, dstPath):
        """
        下载文件或目录

        scp -P {port} -r {user}@{domain}:{target}/{srcPath} {dstPath}

        :param user: 用户名，可省略
        :param domain: 目标机器地址
        :param target: 远程映射路径
        :param port: 端口
        :param srcPath: 远程映射子路径
        :param dstPath: 本地文件路径
        :return: 发送状态
        """
        if user:
            return os.system(
                "scp -P %s -r %s %s"
                % (port, user + "@\\[" + domain + "\\]:" + target + srcPath, dstPath)
            )
        else:
            return os.system(
                "scp -P %s -r %s %s"
                % (port, "\\[" + domain + "\\]:" + target + srcPath, dstPath)
            )

    @staticmethod
    def command(user, domain, target, port, command):
        """
        在远程映射执行命令

        :param user: 用户名，可省略
        :param domain: 目标机器地址
        :param target: 远程映射路径
        :param port: 端口
        :param command: 命令
        :return: 命令执行状态, 命令执行结果
        """
        if not domain or not target:
            return 0
        status, content = external_exec(
            'ssh -p %s %s@%s "cd %s ; %s"' % (port, user, domain, target, command)
            if user
            else 'ssh -p %s %s "cd %s ; %s"' % (port, domain, target, command),
            without_output=True,
        )
        return status, content

    @staticmethod
    def ssh(user, domain, target, port, dstPath):
        """
        连接至远程映射控制台

        :param user: 用户名，可省略
        :param domain: 目标机器地址
        :param target: 远程映射路径
        :param port: 端口
        :param dstPath: 子路径
        :return:
        """
        if user:
            return os.system(
                "ssh -p {port} -t {user}@{domain} 'cd {aim} ; exec $SHELL -l'".format(
                    port=port,
                    user=user,
                    domain=domain,
                    aim=os.path.join(target, dstPath),
                )
            )
        else:
            return os.system(
                "ssh -p {port} -t {domain} 'cd {aim} ; exec $SHELL -l'".format(
                    port=port, domain=domain, aim=os.path.join(target, dstPath)
                )
            )


def menu_output(menu):
    from rich.table import Table, Column
    from rich.box import SIMPLE

    tb = Table(
        *[
            Column(_lang["Parameter"], justify="full", style="bold yellow"),
            Column(_lang["Description"], justify="right", style="bold cyan"),
        ],
        show_edge=False,
        show_header=False,
        row_styles=["none", "dim"],
        box=SIMPLE,
        pad_edge=False,
        title="[bold underline] {title}[dim]Author: RhythmLian\n".format(
            title=menu["title"]
        ),
    )
    for line in menu["lines"]:
        tb.add_row(
            (menu["prefix"] + " " if line[0].startswith("-") else "") + line[0], line[1]
        )
    QproDefaultConsole.print(tb, justify="center")
    QproDefaultConsole.print(
        "\n" + _lang["docs"], "https://qpro-doc.rhythmlian.cn/", justify="center"
    )


def get_config(without_output: bool = False):
    config_path = __latest_filename("project_configure.json")
    config = {}
    if config_path:
        import json

        with open(config_path, "r") as f:
            config = json.load(f)
    else:
        if not without_output:
            QproDefaultConsole.print(
                QproErrorString,
                _lang["NoSuchFile"].format('"project_configure.json"')
                + "\n"
                + _lang["RunCmd"].format('"Qpro init"'),
            )
        exit(0)
    return config


def get_server_targets():
    res = get_config()["server_targets"]
    for item in res:
        if not item["path"].endswith("/"):
            item["path"] += "/"
    return res


def _choose_server_target():
    server_targets = get_server_targets()
    choices = [
        f'{i["user"]}@{i["host"]}:{i["path"]} port: {i["port"]}'
        if i["user"]
        else f'{i["host"]}:{i["path"]} port: {i["port"]}'
        for i in server_targets
        if i["host"] and i["path"]
    ]
    try:
        index = choices.index(
            _ask(
                {
                    "type": "list",
                    "message": _lang["ChooseServerTarget"],
                    "choices": choices,
                }
            )
        )
        return server_targets[index]
    except:
        return None


def apply_fig_complete(name: str, team: str = "", token: str = ""):
    external_exec(
        f'npx @fig/publish-spec --spec-path complete/fig/*.ts --name {name}{" --team " + team if team else ""}{" --token " + token if token else ""}'
    )
