import os.path

from rich.prompt import Prompt

from QuickProject import __sub_path, _choose_server_target
from . import *
from . import _ask, _lang


def __format_json(info, path: str):
    """
    回写配置表

    :param info: 列表格式或字典格式
    :param path: 路径
    :return:
    """
    import json

    with open(path, "w") as f:
        if isinstance(info, list):
            config = {}
            for line in info:
                config[line[0]] = line[1] if line[0] != "server_targets" else line[1:]
            json.dump(config, f, indent=1)
        elif isinstance(info, dict):
            json.dump(info, f, indent=1)


def __findAndReplace(dirPath, fo, to):
    """
    替换模板项目中的指定字段

    :param dirPath: 项目路径
    :param fo: 识别
    :param to: 替换
    :return:
    """
    for rt, son_dir, son_files in os.walk(dirPath):
        for _dir in son_dir:
            if _dir.startswith(fo):
                os.rename(rt + dir_char + _dir, rt + dir_char + _dir.replace(fo, to))

    for rt, son_dir, son_files in os.walk(dirPath):
        for file in son_files:
            try:
                with open(rt + dir_char + file, "r") as f:
                    ct = f.read()
                with open(rt + dir_char + file, "w") as f:
                    f.write(ct.replace(fo, to))
                if file.startswith(fo):
                    os.rename(
                        rt + dir_char + file, rt + dir_char + file.replace(fo, to)
                    )
            except UnicodeDecodeError:
                QproDefaultConsole.print(
                    QproErrorString, f"UnicodeDecodeError: {rt + dir_char + file}"
                )


def remove(path):
    """
    删除文件或目录

    :param path: 路径
    :return:
    """
    import shutil

    if os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)


def scp_init(server_targets: list):
    if not server_targets:
        return
    for server_target in server_targets:
        user, host, port, target = (
            server_target["user"],
            server_target["host"],
            server_target["port"],
            server_target["path"],
        )
        st = SshProtocol.post_all_in_folder(user, host, target, port, "")
        if st:
            QproDefaultConsole.print(QproErrorString, _lang["scp_init_failed"])


def _create_empty_project(project_name):
    if os.path.exists(project_name):
        return QproDefaultConsole.print(QproErrorString, _lang["existsError"])
    os.mkdir(project_name)
    __format_json(
        [
            ["build", ""],
            ["entry_point", ""],
            ["executable", ""],
            ["input_file", ""],
            ["template_root", ""],
            ["server_target", "", ""],
        ],
        project_name + dir_char + configure_name,
    )
    os.chdir(project_name)
    return


def _search_supported_languages(is_CN=using_gitee):
    kw = _ask(
        {
            "type": "input",
            "message": _lang["askKeyword"],
        }
    )

    import json
    import requests

    try:
        res = json.loads(
            requests.get(
                f"https://qpro-lang.rhythmlian.cn/?keyword={kw}&is_CN={str(is_CN).lower()}"
            ).text
        )
        if not res["status"]:
            QproDefaultConsole.print(QproErrorString, res["message"])
            return None
        data = {i[0]: i[1:] for i in res["data"]}
        return data[
            _ask(
                {
                    "type": "list",
                    "message": _lang["ChooseSupportedTemplate"],
                    "choices": list(data.keys()),
                }
            )
        ]
    except Exception as e:
        QproDefaultConsole.print(QproErrorString, repr(e))
    return None


def _external_create(project_name: str, key: str = ""):
    from git import Repo

    if key:
        if key in ["Empty", "空白项目"]:
            return _create_empty_project(project_name)

        templateProjectUrls = _search_supported_languages()
        if not templateProjectUrls:
            exit(0)
        with QproDefaultConsole.status(
            (
                "Cloning Qpro {} Template to {}"
                if user_lang != "zh"
                else "正在克隆Qpro {} 模板为 {}"
            ).format(key, project_name)
        ):
            Repo.clone_from(templateProjectUrls[0], project_name)
    else:
        templateProjectUrls = _ask(
            {
                "type": "input",
                "message": "GIT " + ("URL" if user_lang != "zh" else "链接") + ":",
            }
        )
        with QproDefaultConsole.status(
            (
                "Cloning External Template to {}"
                if user_lang != "zh"
                else "正在克隆Qpro 外部模板为 {}"
            ).format(project_name)
        ):
            Repo.clone_from(templateProjectUrls, project_name)
    os.chdir(project_name)
    try:
        remove(".git")
    except Exception as e:
        QproDefaultConsole.print(QproErrorString, repr(e))
    if key:
        __findAndReplace(
            os.getcwd(), templateProjectUrls[1], project_name.replace("-", "_")
        )


def __get_server_target_from_string():
    """
    从字符串中获取服务器目标
    """
    server_target = (
        _ask(
            {
                "type": "input",
                "message": "Input user@ip:dir_path if you need scp"
                if user_lang != "zh"
                else "输入 用户@IP:路径 如果你打算使用SSH",
            }
        )
        .strip()
        .replace(dir_char, "/")
    )

    if server_target and not server_target.endswith("/"):
        if not server_target.endswith(":"):
            server_target += "/"
        else:
            server_target += "~/"
    user, host, path, port = "", "", "", 22
    if server_target:
        user, target = server_target.split("@")
        target = target.split(":")
        host = ":".join(target[:-1])
        path = target[-1] + ("" if target[-1].endswith("/") else "/")
        port = _ask(
            {
                "type": "input",
                "message": "input port" if user_lang != "zh" else "输入端口号",
                "default": "22",
            }
        )
    return {"user": user, "host": host, "port": port, "path": path}


def create():
    try:
        project_name = sys.argv[2]
    except IndexError:
        return QproDefaultConsole.print(
            QproWarnString,
            "usage: Qpro create <project>"
            if user_lang != "zh"
            else "使用: Qpro create <项目>",
        )
    else:
        if os.path.exists(project_name) and os.path.isdir(project_name):
            return QproDefaultConsole.print(
                QproErrorString, '"%s" is exist!' % (os.path.abspath(project_name))
            )

        lang = _ask(
            {
                "type": "list",
                "message": "选择模板:" if user_lang == "zh" else "Choose Template:",
                "choices": [
                    _lang["EmptyProject"],
                    _lang["InnerTemplate"],
                    _lang["ExternalProject"],
                ],
            }
        )

        if lang == _lang["ExternalProject"]:
            _external_create(project_name)
        else:
            _external_create(project_name, lang)

        config = get_config()
        config["server_targets"] = [__get_server_target_from_string()]
        __format_json(config, configure_name)

        if _ask(
            {"type": "confirm", "message": _lang["OpenWithVscode"], "default": True}
        ):
            if sys.platform == "darwin":
                os.system(f'open -a "Visual Studio Code" .')
            else:
                os.system("code .")


def scp(smv_flag: bool = False):
    kw = "scp" if not smv_flag else "smv"
    try:
        path = sys.argv[2]
        sub_path = __sub_path(path)
    except IndexError:
        return QproDefaultConsole.print(
            QproWarnString, f'{_lang["Usage"]}: Qpro {kw} <{_lang["Path"]}>'
        )
    else:
        if not sub_path:
            return QproDefaultConsole.print(
                QproErrorString,
                _lang["NotInProject"].format(path)
                if os.path.exists(path)
                else _lang["NoSuchFile"].format(path),
            )
        server_targets = get_server_targets()
        status = 0
        for server_target in server_targets:
            if os.path.isdir(path):
                status |= SshProtocol.post_folder(
                    server_target["user"],
                    server_target["host"],
                    server_target["path"],
                    server_target["port"],
                    path,
                    sub_path,
                )
            else:
                status |= SshProtocol.post_file(
                    server_target["user"],
                    server_target["host"],
                    server_target["path"],
                    server_target["port"],
                    path,
                    sub_path,
                )
        if smv_flag and not status:
            remove(path)


def smv():
    if _ask(
        {
            "type": "confirm",
            "message": _lang["ConfirmDeleteAfterTransform"],
            "default": True,
        }
    ):
        scp(True)


def get():
    try:
        path = sys.argv[2]
        sub_path = __sub_path(path, isExist=False)
    except IndexError:
        return QproDefaultConsole.print(
            QproWarnString, f'{_lang["Usage"]}: Qpro get <{_lang["Path"]}>'
        )
    else:
        if not sub_path:
            return QproDefaultConsole.print(
                QproErrorString, _lang["NotInProject"].format(path)
            )
        server_target = get_server_targets()[0]
        SshProtocol.get_file_or_folder(
            server_target["user"],
            server_target["host"],
            server_target["path"],
            server_target["port"],
            sub_path,
            path,
        )


def pro_init():
    work_project = ""
    while not work_project:
        work_project = Prompt.ask(_lang["askProjectName"]).strip()
    lang_tool_exe = {
        "c": ["gcc -std=c11 --source_file-- -o --execute--", "", ".c"],
        "cpp": ["g++ -std=c++11 --source_file-- -o --execute--", "", ".cpp"],
        "java": ["javac -d dist --source_file--", "java -classpath dist ", ".java"],
        "python3": ["", "python3 ", ".py"],
        "python": ["", "python ", ".py"],
        "custom": ["", "", ""],
    }

    lang_name = _ask(
        {
            "type": "list",
            "message": "Choose Language:" if user_lang != "zh" else "选择语言:",
            "choices": lang_tool_exe.keys(),
        }
    )

    lang = lang_tool_exe[lang_name]
    source_file = ""
    if lang_name != "custom":
        source_file = (
            ("main" + lang[-1]) if lang[0] != "javac" else work_project + lang[-1]
        )
        while not os.path.exists(source_file):
            source_file = Prompt.ask(_lang["SetEntryPoint"].format(source_file)).strip()
    if lang[0] != "javac":
        execute = (
            lang[1] + "dist" + dir_char + work_project
            if lang[0]
            else lang[1] + source_file
        )
    elif lang_name != "custom":
        work_project = source_file.split(dir_char)[-1].split(".")[0]
        execute = lang[1] + work_project
    else:
        execute = ""
    if (
        not os.path.exists("dist") or not os.path.isdir("dist")
    ) and lang_name != "custom":
        os.mkdir("dist")
    info = [
        [
            "build",
            lang[0]
            .replace("--source_file--", source_file)
            .replace("--execute--", execute),
        ],
        ["entry_point", source_file],
        ["executable", execute],
        ["input_file", "dist" + dir_char + "input.txt" if lang_name != "empty" else ""],
        ["template_root", "template" + dir_char if lang_name != "empty" else ""],
        ["server_targets", __get_server_target_from_string()],
    ]
    __format_json(info, configure_name)
    if lang_name and lang_name == "custom":
        if _ask(
            {
                "type": "confirm",
                "message": _lang["ConfirmSyncProject"],
                "default": True,
            }
        ):
            scp_init(info[-1][1:])
        return
    with open(info[3][-1], "w") as f:
        f.write(_lang["EditThisFile"])
    if not os.path.exists("template") or not os.path.isdir("template"):
        os.mkdir("template")
    try:
        with open(info[1][-1], "r") as f:
            main_cont = f.read()
        with open("template" + dir_char + "main", "w") as f:
            f.write(main_cont)
    except Exception as e:
        QproDefaultConsole.print(
            QproErrorString,
            "make backup failed with error: %s, you need backup code by yourself!" % e,
        )
    if _ask(
        {
            "type": "confirm",
            "message": _lang["ConfirmSyncProject"],
            "default": True,
        }
    ):
        scp_init(info[-1][1:])


def ssh():
    server_target = _choose_server_target()
    if not server_target:
        return
    SshProtocol.ssh(
        server_target["user"],
        server_target["host"],
        server_target["path"],
        server_target["port"],
        __sub_path("."),
    )


def delete_all():
    server_targets = get_server_targets()
    st = 0
    for server_target in server_targets:
        _st = SshProtocol.command(
            server_target["user"],
            server_target["host"],
            server_target["path"],
            server_target["port"],
            "rm -rf .",
        )
        st |= 1 if _st else 0
        QproDefaultConsole.print(
            QproErrorString, f"{server_target}: delete all failed with error: {st}"
        )
    if not st:
        remove(os.getcwd())


def delete():
    try:
        path = os.path.abspath(sys.argv[2])
        sub_path = __sub_path(path)
    except IndexError:
        return QproDefaultConsole.print(
            QproWarnString,
            f"{_lang['Usage']}: Qpro del <{_lang['Path']}>",
        )
    else:
        if not sub_path:
            return QproDefaultConsole.print(
                QproErrorString,
                _lang["NotInProject"].format(path)
                if os.path.exists(path)
                else _lang["NoSuchFile"].format(path),
            )
        server_targets = get_server_targets()
        st = 0
        for server_target in server_targets:
            _st = SshProtocol.command(
                server_target["user"],
                server_target["host"],
                server_target["path"],
                server_target["port"],
                f"rm -rf {sub_path}",
            )
            st |= 1 if _st else 0
            if _st:
                QproDefaultConsole.print(
                    QproErrorString,
                    f"{server_target}: delete {sub_path} failed with error: {_st}",
                )
        if not st or _ask(
            {
                "type": "confirm",
                "message": _lang["ConfirmDeleteNotInProject"].format(path),
            }
        ):
            remove(sub_path)


def tele_ls():
    try:
        path = sys.argv[2]
        sub_path = __sub_path(path, False)
    except IndexError:
        sub_path = __sub_path("./", False)
    server_target = _choose_server_target()
    if server_target:
        from . import SshProtocol

        res = (
            SshProtocol.command(
                server_target["user"],
                server_target["host"],
                server_target["path"],
                server_target["port"],
                f"ls -lah {sub_path}",
            )
            .strip()
            .split("\n")[3:]
        )
        res = [i.strip().split() for i in res]

        from rich.table import Table
        from rich.box import SIMPLE_HEAVY
        from rich.color import Color
        from rich.text import Text
        from rich.style import Style

        table = Table(
            title=f"{sub_path}",
            box=SIMPLE_HEAVY,
            show_header=True,
            header_style="bold magenta",
        )
        table.add_column(_lang["PermissionCode"], justify="center")
        table.add_column(_lang["Size"], justify="center")
        table.add_column(_lang["Owner"], justify="center")
        table.add_column(_lang["ChangeTime"], justify="center")
        table.add_column(_lang["Filename"], justify="right")
        for i in res:
            is_dir = True if i[0][0] == "d" else False
            color = Color.from_rgb(112, 87, 250) if is_dir else None
            p_color = Color.from_rgb(171, 157, 242)
            permission = "".join(["1" if j != "-" else "0" for j in i[0][1:]])
            permission = "%d%d%d" % (
                int(permission[:3], 2),
                int(permission[3:6], 2),
                int(permission[6:], 2),
            )
            table.add_row(
                *[
                    Text(permission, style=Style(color=p_color)),
                    f"[green]{i[4]}",
                    "[bold yellow]" + i[2],
                    "[blue]" + " ".join(i[5:8]),
                    Text(" ".join(i[8:]), style=Style(color=color, bold=is_dir)),
                ]
            )
        QproDefaultConsole.print(table, justify="center")


def enable_complete():
    config = get_config()
    config["enable_complete"] = True
    __format_json(config, project_configure_path)


def __get_Qpro_fig_Dir():
    QproGlobalDir = os.environ.get("QproGlobalDir", None)
    if not QproGlobalDir:
        QproDefaultConsole.print(
            QproErrorString,
            _lang["NotSet"].format("QproGlobalDir"),
        )
        return None
    QproGlobalDir = QproGlobalDir.replace("~", user_root)
    if not os.path.exists(QproGlobalDir):
        QproDefaultConsole.print(
            QproErrorString,
            _lang["notExistsError"].format("QproGlobalDir"),
        )
        return None
    if not os.path.exists(os.path.join(QproGlobalDir, "bin")):
        os.mkdir(os.path.join(QproGlobalDir, "bin"))
    if not os.path.exists(os.path.join(QproGlobalDir, "fig")):
        os.mkdir(os.path.join(QproGlobalDir, "fig"))
    if not os.path.exists(os.path.join(QproGlobalDir, "QproGlobalCommands")):
        os.mkdir(os.path.join(QproGlobalDir, "QproGlobalCommands"))
    return QproGlobalDir


def register_global_command():
    if not os.path.exists(configure_name):
        return QproDefaultConsole.print(
            QproErrorString,
            _lang["notExistsError"].format(configure_name),
        )
    if is_win:
        return QproDefaultConsole.print(QproWarnString, _lang["NotSupportWindows"])
    QproGlobalDir = __get_Qpro_fig_Dir()
    if not QproGlobalDir:
        return
    import json
    import shutil

    project_name = os.getcwd().split(dir_char)[-1]
    package_name = project_name.replace("-", "_")
    fig_dir = os.path.join(QproGlobalDir, "fig")
    commands_dir = os.path.join(QproGlobalDir, "QproGlobalCommands")
    if os.path.exists(os.path.join(fig_dir, f"{project_name}.json")):
        QproDefaultConsole.print(QproWarnString, _lang["HasBeenRegistered"])
        if _ask(
            {
                "type": "confirm",
                "message": _lang["Overwrite"],
                "default": False,
            }
        ):
            os.remove(os.path.join(fig_dir, f"{project_name}.json"))
            if os.path.exists(os.path.join(commands_dir, f"{package_name}")):
                shutil.rmtree(os.path.join(commands_dir, f"{package_name}"))
        else:
            return
    import subprocess

    with open(os.path.join(fig_dir, f"{project_name}.json"), "w") as f:
        project_subcommands = json.loads(
            subprocess.check_output(["qrun", "--qrun-fig-complete"]).decode("utf-8")
        )
        if not project_subcommands:
            return QproDefaultConsole.print(QproErrorString, _lang["NotACommanderAPP"])
        json.dump(
            {
                "fig": {
                    "name": project_name,
                    "description": project_name,
                    "subcommands": project_subcommands,
                },
                "path": os.getcwd(),
            },
            f,
            ensure_ascii=False,
            indent=1,
        )

    shutil.copytree(
        rt_dir + dir_char + package_name, os.path.join(commands_dir, package_name)
    )
    entry_point = get_config()["entry_point"].split(dir_char)[-1].split(".")[0]
    with open(os.path.join(commands_dir, package_name, f"{entry_point}.py"), "r") as f:
        ct = f.read()
        if "def main():" not in ct:
            ct = ct.replace("if __name__ == '__main__':", "def main():").replace(
                'if __name__ == "__main__":', "def main():"
            )
    with open(os.path.join(commands_dir, package_name, f"{entry_point}.py"), "w") as f:
        f.write(ct)
    with open(os.path.join(QproGlobalDir, "bin", f"{project_name}"), "w") as f:
        ct = f"""#!/usr/bin/env python3
import sys
sys.path.append('{QproGlobalDir}')

from QproGlobalCommands.{package_name} import {entry_point}
{entry_point}.main()
        """
        f.write(ct)
    config = get_config()
    flag = True
    for item in config["server_targets"]:
        if item["host"] == "localhost":
            item["path"] = os.path.join(QproGlobalDir, "QproGlobalCommands")
            item["port"] = 22
            flag = False
            break
    if flag:
        config["server_targets"].append(
            {
                "user": "",
                "host": "localhost",
                "path": os.path.join(QproGlobalDir, "QproGlobalCommands"),
                "port": 22,
            }
        )
    __format_json(config, project_configure_path)
    os.chmod(os.path.join(QproGlobalDir, "bin", f"{project_name}"), 0o755)
    QproDefaultConsole.print(
        QproInfoString, _lang["RegisterSuccess"].format(f'"{project_name}"')
    )


def unregister():
    QproGlobalDir = __get_Qpro_fig_Dir()
    if not QproGlobalDir:
        return

    import shutil

    config = get_config()
    project_name = os.getcwd().split(dir_char)[-1]
    fig_dir = os.path.join(QproGlobalDir, "fig")
    bin_dir = os.path.join(QproGlobalDir, "bin")

    for item in config["server_targets"]:
        if item["host"] == "localhost":
            shutil.rmtree(os.path.join(item["path"], project_name))
            break
    if os.path.exists(os.path.join(fig_dir, f"{project_name}.json")):
        os.remove(os.path.join(fig_dir, f"{project_name}.json"))
    if os.path.exists(os.path.join(bin_dir, f"{project_name}")):
        os.remove(os.path.join(bin_dir, f"{project_name}"))


def fmt():
    import json

    def adjust(filepath: str):
        if filepath.endswith(".csv"):
            with open(filepath, "r") as f:
                data = f.read().splitlines()
                data = {
                    i[0]: i[1:] if len(i[1:]) > 1 else i[1]
                    for i in [i.split(",") for i in data]
                }
        else:
            with open(filepath, "r") as f:
                data = json.load(f)
        if "server_target" in data:
            server_target = data.pop("server_target")
            if server_target[0]:
                ls = server_target[0].split("@")
                if len(ls) == 2:
                    user, target = ls
                else:
                    user, target = "", ls[0]
                target = target.split(":")
                host = ":".join(target[:-1])
                path = target[-1]
                data["server_targets"] = [
                    {"user": user, "host": host, "path": path, "port": server_target[1]}
                ]
            else:
                data["server_targets"] = [
                    {"user": "", "host": "", "path": "", "port": "22"}
                ]
        new_json = {}
        if "compile_tool" in data:
            new_json["build"] = data.pop("compile_tool")
        if "compile_filename" in data:
            new_json["entry_point"] = data.pop("compile_filename")
        if "executable_filename" in data:
            new_json["executable"] = data.pop("executable_filename")
        new_json.update(data)

        with open(
            os.path.join(os.path.dirname(filepath), "project_configure.json"), "w"
        ) as f:
            json.dump(new_json, f, indent=4, ensure_ascii=False)

    # walk dir
    for root, _, files in os.walk(os.getcwd()):
        for file in files:
            filepath = os.path.join(root, file)
            if file == "project_configure.csv" or file == "project_configure.json":
                try:
                    adjust(filepath)
                except Exception as e:
                    QproDefaultConsole.print(QproErrorString, repr(e))
                    QproDefaultConsole.print(QproErrorString, filepath)


func = {
    "create": create,
    "scp": scp,
    "smv": smv,
    "get": get,
    "ssh": ssh,
    "del-all": delete_all,
    "del": delete,
    "ls": tele_ls,
    "enable-complete": enable_complete,
    "register": register_global_command,
    "unregister": unregister,
    "fmt": fmt,
}


def main():
    if len(sys.argv) < 2 or "-h" == sys.argv[1]:
        menu_output(
            {
                "title": "Qpro usage\n" if user_lang != "zh" else "Qpro 菜单\n",
                "lines": [
                    ("init", _lang["MenuInit"]),
                    ("-h", _lang["MenuHelp"]),
                    ("create [bold magenta]<name>", _lang["MenuCreate"]),
                    ("update", _lang["MenuUpdate"]),
                    ("ssh", _lang["MenuSSH"]),
                    ("scp [bold magenta]<path>", _lang["MenuSCP"]),
                    ("smv [bold magenta]<path>", _lang["MenuSMV"]),
                    ("scp-init", _lang["MenuSCPInit"]),
                    ("get [bold magenta]<path>", _lang["MenuGet"]),
                    ("del [bold magenta]<path>", _lang["MenuDel"]),
                    ("del-all", _lang["MenuDelAll"]),
                    ("ls  [bold magenta]<path>", _lang["MenuLs"]),
                    ("enable-complete", _lang["MenuComplete"]),
                    ("register", _lang["MenuRegister"]),
                    ("unregister", _lang["MenuUnregister"]),
                    ("fmt", _lang["MenuFmt"]),
                    ("qrun *", _lang["MenuQrun"]),
                ],
                "prefix": "Qpro",
            }
        )
    elif "update" == sys.argv[1]:
        os.system(f"{user_pip} install Qpro --upgrade")
    elif sys.argv[1] in func:
        try:
            func[sys.argv[1]]()
        except SystemExit:
            return
        except Exception:
            QproDefaultConsole.print_exception()
    elif sys.argv[1] == "scp-init":
        scp_init(get_server_targets())
    elif "init" != sys.argv[1]:
        QproDefaultConsole.print(QproErrorString, _lang["WrongUsage"])
    elif not os.path.exists(configure_name):
        pro_init()
    else:
        QproDefaultConsole.print(
            _lang["HaveConfigured"].format(f'"{project_configure_path}"')
        )


if __name__ == "__main__":
    main()
