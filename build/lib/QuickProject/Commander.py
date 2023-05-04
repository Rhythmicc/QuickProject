import re
import sys
import inspect
import argparse
from inspect import isfunction
from . import QproDefaultConsole, QproErrorString, _lang


_ROOT_HELP = "__COMMANDER_ROOT_HELP_FUNCTION__"


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


class Commander:
    def __init__(
        self,
        name: str,
        seg_flag: bool = True,
        custom_complete: bool = False,
        non_complete: bool = False,
    ):
        """
        QuickProject的Commander类，帮助快速构建一个命令工具

        :param seg_flag: 是否将函数名和参数名中的'_'替换为'-'
        :param custom_complete: 是否开启自定义补全
        :param non_complete: 不将隐藏函数加入到帮助菜单和补全插件中
        """
        self.name = name
        self.non_complete = non_complete
        self.command_table = {}
        self.fig_table = []
        self.custom_complete_table = {}
        self.custom_help_table = {}

        self.custom_help_table[_ROOT_HELP] = self.help
        self.seg_flag = seg_flag
        self.fig_prefix = None

        if not custom_complete:

            @self.command(hidden=True)
            def complete(team: str = "", token: str = "", is_script: bool = False):
                """
                获取补全列表

                :param team: 团队名
                :param token: 团队token
                :param is_script: 是否为脚本
                """
                return self.generate_complete(team, token, is_script)

    def custom_complete(self, param: str, description: str = None):
        """
        自定义补全
        Custom complete

        :param param: 参数名
        :param description: 参数描述
        :return:
        """

        def wrapper(func):
            if not isfunction(func):
                raise TypeError(f"{func} not a function")
            func_name = func.__name__.strip("_")
            if self.seg_flag:
                func_name = func_name.replace("_", "-")
            if func_name not in self.custom_complete_table:
                self.custom_complete_table[func_name] = {}
            self.custom_complete_table[func_name][param] = {
                "suggestions": func(),
                "description": description,
            }

        return wrapper

    def __op_cur_args(self, func_name, cur_args, name):
        if name in self.custom_complete_table.get(func_name, {}):
            cur_args["suggestions"] = self.custom_complete_table[func_name][name]
            if description := self.custom_complete_table[func_name][name].get("description", None):
                cur_args["description"] = description

    def command(self, hidden: bool = False):
        def wrapper(func):
            if not isfunction(func):
                raise TypeError(f"{func} " + _lang["NotFunction"])
            param_doc = (
                {
                    i[0].strip(): i[1].strip()
                    for i in re.findall(":param(.*?):(.*?)\n", func.__doc__, re.S)
                }
                if func.__doc__
                else {}
            )
            func_analyser = inspect.signature(func)
            func_args_parser = argparse.ArgumentParser()
            func_name = func.__name__.strip("_")
            description = (
                func.__doc__.strip().split(":param")[0].strip()
                if func.__doc__
                else func_name.replace("_", " ")
            )
            if self.seg_flag:
                func_name = func_name.replace("_", "-")
            func_fig = {
                "name": func_name,
                "description": description,
                "args": [],
                "options": [],
            }
            if func_name in self.command_table:
                raise Exception(f"{func} " + _lang["CommandAlreadyExists"])
            for arg in func_analyser.parameters.values():
                if arg.name.startswith("_"):  # 忽略私有参数
                    continue
                arg_name = arg.name if not self.seg_flag else arg.name.replace("_", "-")
                _type = None
                _default = None
                if arg.annotation != arg.empty:
                    _type = arg.annotation
                if arg.default != arg.empty:
                    _default = arg.default
                if _default is None:
                    if _type == list:
                        func_args_parser.add_argument(
                            f"-{arg_name}",
                            type=str,
                            nargs="+",
                        )
                        cur_args = {
                            "name": arg_name,
                            "description": param_doc.get(arg.name, f"<{arg_name}>"),
                            "isVariadic": True,
                            "isRequired": True,
                        }
                        self.__op_cur_args(func_name, cur_args, arg_name)
                        if "file" in arg_name.lower() or "path" in arg_name.lower():
                            cur_args["template"] = ["filepaths", "folders"]
                        func_fig["options"].append(
                            {
                                "name": f"-{arg_name}",
                                "description": param_doc.get(arg.name, f"<{arg_name}>"),
                                "args": cur_args,
                            }
                        )
                    else:
                        func_args_parser.add_argument(
                            arg_name, type=_type if _type != bool else str2bool
                        )
                        cur_args = {
                            "name": arg_name,
                            "description": param_doc.get(arg.name, f"<{arg_name}>"),
                        }
                        self.__op_cur_args(func_name, cur_args, arg_name)
                        if "file" in arg_name.lower() or "path" in arg_name.lower():
                            cur_args["template"] = ["filepaths", "folders"]
                        func_fig["args"].append(cur_args)
                else:
                    if _type == list:
                        QproDefaultConsole.print(
                            QproErrorString,
                            f"{func_name}:",
                            '"list"',
                            _lang["CantHaveDefaultValue"],
                        )
                        return
                    _kw = {"required": False, "type": _type, "default": _default}
                    if _type == bool:
                        _kw.pop("type")
                        _kw["action"] = "store_true"
                    func_args_parser.add_argument(f"--{arg_name}", **_kw)
                    cur_args = {
                        "name": arg_name,
                        "description": param_doc.get(arg.name, f"<{arg_name}>"),
                    }
                    self.__op_cur_args(func_name, cur_args, arg_name)
                    if (
                        "file" in arg_name.lower()
                        or "path" in arg_name.lower()
                        and _type != bool
                    ):
                        cur_args["template"] = ["filepaths", "folders"]
                    if _type != bool:
                        func_fig["options"].append(
                            {
                                "name": f"--{arg_name}",
                                "description": param_doc.get(arg.name, f"<{arg_name}>"),
                                "isOptional": True,
                                "args": cur_args,
                            }
                        )
                    else:
                        func_fig["options"].append(
                            {
                                "name": f"--{arg_name}",
                                "description": param_doc.get(arg.name, f"<{arg_name}>"),
                            }
                        )
            self.fig_table.append(func_fig)
            self.command_table[func_name] = {
                "func": func,
                "analyser": func_analyser,
                "parser": func_args_parser,
                "param_doc": param_doc,
                "description": description,
                "hidden": hidden,
            }

        return wrapper

    def _check_args_(self, is_option: bool = True, shown_hidden: bool = False):
        res = False
        if is_option:
            for function in self.command_table:
                if self.command_table[function]["hidden"] and not shown_hidden:
                    continue
                for arg in self.command_table[function]["analyser"].parameters.values():
                    _default = arg.default if arg.default != arg.empty else None
                    if _default is not None:
                        res = True
                        break
                if res:
                    break
        else:
            for function in self.command_table:
                if self.command_table[function]["hidden"] and not shown_hidden:
                    continue
                for arg in self.command_table[function]["analyser"].parameters.values():
                    _default = arg.default if arg.default != arg.empty else None
                    if _default is None:
                        res = True
                        break
                if res:
                    break
        return res

    def custom_help(self, root: bool = False):
        """
        自定义帮助信息

        :param root: 是否为根命令
        """

        def wrapper(func):
            if not isfunction(func):
                raise TypeError(f"{func} not a function")
            if root:
                self.custom_help_table[_ROOT_HELP] = func
                return
            func_name = func.__name__.strip("_")
            if self.seg_flag:
                func_name = func_name.replace("_", "-")
            if func_name not in self.custom_help_table:
                self.custom_help_table[func_name] = func

        return wrapper

    def help(self, shown_hidden: bool = False):
        from rich.table import Table
        from rich.box import SIMPLE_HEAVY

        has_requir = self._check_args_(False, shown_hidden)
        has_option = self._check_args_(True, shown_hidden)
        table = Table(
            show_edge=False,
            row_styles=["none", "dim"],
            box=SIMPLE_HEAVY,
            title=f"[bold underline]{_lang['MenuHelp']}[/bold underline]\n",
        )
        table.add_column(_lang["SubCommand"], justify="center")
        table.add_column(_lang["Description"], justify="center")
        if has_requir:
            table.add_column(_lang["RequiredArgs"], justify="center")
        if has_option:
            table.add_column(_lang["OptionnalArgs"], justify="center")
        for function in self.command_table:
            if self.command_table[function]["hidden"] and not shown_hidden:
                continue
            cur_line = ["[bold magenta]" + function + "[/bold magenta]"]
            arg1, arg2 = [], []
            for arg in self.command_table[function]["analyser"].parameters.values():
                if arg.name.startswith("_"):  # 忽略私有参数
                    continue
                arg_name = arg.name if not self.seg_flag else arg.name.replace("_", "-")
                name = "[underline]" + arg_name + "[/underline]"
                _type = (
                    arg.annotation.__name__ if arg.annotation != arg.empty else "Any"
                )
                _default = arg.default if arg.default != arg.empty else None
                arg_str = f"{name}: [bold cyan]{_type}[/bold cyan]"
                if _default is not None:
                    if _type == "str":
                        arg_str += (
                            f" = [dim]'[/dim][yellow]{_default}[/yellow][dim]'[/dim]"
                        )
                    elif _type == "int" or _type == "float":
                        arg_str += f" = [bold blue]{_default}[/bold blue]"
                    elif _type == "bool":
                        arg_str += f" = [bold red]{_default}[/bold red]"
                    else:
                        arg_str += f" = {_default}"
                    arg2.append(arg_str)
                else:
                    arg1.append(arg_str)
            cur_line.append(self.command_table[function]["description"])
            if has_requir:
                cur_line.append(", ".join(arg1))
            if has_option:
                cur_line.append(", ".join(arg2))
            table.add_row(*cur_line)
        QproDefaultConsole.print(table, justify="center")

    def __command_complete__(self, route_path: list):
        """
        用于命令补全

        :param route_path: 路径
        :return:
        """
        if not route_path:
            ls = [
                f"{i}:{self.command_table[i]['func'].__doc__.strip().split(':param')[0].strip().replace(' ', '_') if self.command_table[i]['func'].__doc__ else 'NONE'}"
                for i in self.command_table
            ]
            return "\n".join(ls)
        call_func = route_path[0]
        has_args = [i.strip().strip("--") for i in route_path[1:]]
        if call_func not in self.command_table:
            return _lang["NoSuchCommand"]
        call_analyser = self.command_table[call_func]["analyser"]
        param_doc = self.command_table[call_func]["param_doc"]
        res = []
        for arg in call_analyser.parameters.values():
            arg_name = arg.name if not self.seg_flag else arg.name.replace("_", "-")
            if arg_name in has_args:
                continue
            if arg.default != arg.empty:
                res.append(
                    f'--{arg_name}:{param_doc[arg.name].replace(" ", "_") if arg.name in param_doc else _lang["NoDescription"]}'
                )
        return "\n".join(res)

    def _fig_complete_(self):
        import json

        table = self.fig_table.copy()
        if self.non_complete:
            for item in table:
                _item = self.command_table.get(item["name"], None)
                if _item and _item["hidden"]:
                    table.remove(item)
        return json.dumps(table, ensure_ascii=False, indent=4)

    def __call__(self):
        if len(sys.argv) >= 2:
            if sys.argv[1] == "--qrun-commander-complete":
                if "qrun" in sys.argv:
                    sys.argv.remove("qrun")
                return print(self.__command_complete__(sys.argv[2:]))
            elif sys.argv[1] == "--qrun-fig-complete":
                return print(self._fig_complete_())
        try:
            func_name = sys.argv[1]
            sys.argv = sys.argv[:1] + sys.argv[2:]
            if func_name not in self.command_table:
                raise KeyError
        except IndexError:
            return self.custom_help_table[_ROOT_HELP]()
        except KeyError:
            QproDefaultConsole.print(
                QproErrorString, f'"{func_name}":', _lang["NoSuchCommand"]
            )
            return self.custom_help_table[_ROOT_HELP](shown_hidden=True)
        else:
            func_info = self.command_table[func_name]
            args = func_info["parser"].parse_args()
            try:
                if "pre_call" in func_info:
                    func_info["pre_call"](**{i[0]: i[1] for i in args._get_kwargs()})
                return func_info["func"](**{i[0]: i[1] for i in args._get_kwargs()})
            except KeyboardInterrupt:
                return QproDefaultConsole.print(QproErrorString, _lang["UserInterrupt"])
            except:
                QproDefaultConsole.print_exception()
                exit(1)

    def real_call(self, func_name: str, *args, **kwargs):
        """
        调用被装饰为命令的函数

        :param func_name: 注册的函数名
        :param args: 参数
        :param kwargs: 参数
        :return:
        """
        if self.seg_flag:
            func_name = func_name.replace("_", "-")
        if func_name not in self.command_table:
            return QproDefaultConsole.print(
                QproErrorString, f'"{func_name}":' + _lang["NoSuchCommand"]
            )
        try:
            return self.command_table[func_name]["func"](*args, **kwargs)
        except KeyboardInterrupt:
            return QproDefaultConsole.print(QproErrorString, _lang["UserInterrupt"])
        except Exception:
            return QproDefaultConsole.print_exception()

    def bind_pre_call(self, func_name, pre_call):
        """
        绑定前置函数
        :param func_name: 函数名
        :param pre_call: 前置函数
        :return:
        """
        if func_name not in self.command_table:
            return QproDefaultConsole.print(
                QproErrorString,
                f'"{func_name}":' + _lang["NoSuchCommand"],
            )
        self.command_table[func_name]["pre_call"] = pre_call

    def generate_complete(
        self, team: str = "", token: str = "", is_script: bool = False
    ):
        """
        生成自动补全文件

        :param team: 团队名
        :param token: 团队token
        :param is_script: 是否为脚本
        """
        import os
        from . import external_exec, _ask

        import json

        project_name = self.name
        project_subcommands = self.fig_table.copy()

        if self.non_complete:
            for item in project_subcommands:
                _item = self.command_table.get(item["name"], None)
                if _item and _item["hidden"]:
                    project_subcommands.remove(item)

        if os.path.exists("complete") and os.path.isdir("complete"):
            if _ask(
                {
                    "type": "confirm",
                    "message": _lang["OverwriteCompleteDir"],
                    "default": False,
                }
            ):
                from .Qpro import remove

                remove("complete")
            else:
                return

        os.mkdir("complete")
        os.mkdir(os.path.join("complete", "fig"))
        os.mkdir(os.path.join("complete", "zsh"))

        with open(os.path.join("complete", "fig", f"{project_name}.ts"), "w") as f:
            from .QproFigTable import default_custom_command_template

            if self.fig_prefix:
                f.write(self.fig_prefix + "\n")

            f.write(
                default_custom_command_template.replace(
                    "__CUSTOM_COMMAND_SPEC__",
                    json.dumps(
                        {
                            "name": project_name,
                            "description": project_name,
                            "subcommands": project_subcommands,
                        },
                        ensure_ascii=False,
                        indent=4,
                    ),
                )
            )
        cur_sub_cmds = []
        sub_cmd_args = []
        for sub_cmd in project_subcommands:
            cur_sub_cmds.append(f"{sub_cmd['name']}:'{sub_cmd['description']}'")
            if "args" in sub_cmd and sub_cmd["args"]:
                cur_args = """if [[ ${prev} == __sub_cmd__ ]]; then
    	opt_args=(
            __sub_cmd_opts__
        )"""
                sub_cmd_opts = []
                for arg in sub_cmd["args"]:
                    if "suggestions" in arg:
                        for i in arg["suggestions"]:
                            sub_cmd_opts.append(
                                f"{i['name']}:'{i.get('description', i['name'])}'"
                            )
                    elif arg["name"].startswith("-"):
                        sub_cmd_opts.append(f"{arg['name']}:'{arg['description']}'")
                for opt in sub_cmd["options"]:
                    if "suggestions" in opt:
                        for i in opt["suggestions"]:
                            sub_cmd_opts.append(
                                f"{i['name']}:'{i.get('description', i['name'])}'"
                            )
                    elif opt["name"].startswith("-"):
                        sub_cmd_opts.append(f"{opt['name']}:'{opt['description']}'")
                cur_args = cur_args.replace("__sub_cmd__", sub_cmd["name"])
                cur_args = cur_args.replace(
                    "__sub_cmd_opts__", "\n            ".join(sub_cmd_opts)
                )
                sub_cmd_args.append(cur_args)

        with open(os.path.join("complete", "zsh", f"_{project_name}"), "w") as f:
            from .QproZshComp import zsh_comp_template, zsh_file_comp1, zsh_file_comp2

            template = zsh_comp_template
            template = template.replace("__proj_name__", project_name)
            template = template.replace(
                "__sub_commands__", "\n        ".join(cur_sub_cmds)
            )
            template = template.replace(
                "__sub_commands_args__",
                "\n    el".join(sub_cmd_args) + zsh_file_comp1
                if sub_cmd_args
                else zsh_file_comp2,
            )
            f.write(template)

        if _ask(
            {
                "type": "confirm",
                "message": _lang["InstallToFig"],
                "default": False,
            }
        ):
            external_exec(
                f'npx @fig/publish-spec --spec-path complete/fig/*.ts --name {project_name}{" --team " + team if team else ""}{" --token " + token if token else ""}{" --is-script" if is_script else ""}'
            )

        if is_script:
            with open(f".{project_name}rc", "w") as f:
                print("function {}() ".format(self.name), file=f, end="{\n")
                print("    qrun $@", file=f)
                print("}", file=f)
                print("export FPATH=$FPATH:$(pwd)/complete/zsh", file=f)
                print("autoload -Uz compinit", file=f)
                print("zstyle ':completion:*' menu select", file=f)
                print("compinit", file=f)
            from . import QproInfoString

            QproDefaultConsole.print(
                QproInfoString,
                _lang["ScriptComplete"].format(self.name),
            )

    def __add__(self, other):
        """
        合并命令

        :param other: 另一个命令
        :return:
        """
        if not isinstance(other, Commander):
            raise TypeError(
                f"unsupported operand type(s) for +: '{type(self).__name__}' and '{type(other).__name__}'"
            )
        self.command_table.update(other.command_table)
        self.fig_table.extend(other.fig_table)
        self.custom_complete_table.update(other.custom_complete_table)

        return self

    def set_fig_prefix(self, prefix):
        """
        【高级接口】设置fig前缀代码

        :param prefix: 前缀
        """
        self.fig_prefix = prefix

    def set_fig_command(self, name, args: dict = None, options: dict = None):
        """
        【高级接口】设置fig命令参数

        :param name: 命令名
        :param args: 参数
        :param options: 选项
        """
        if name not in self.command_table:
            raise ValueError(f"command {name} not found")
        for item in self.fig_table:
            if item["name"] == name:
                if args:
                    item["args"] = args
                if options:
                    item["options"] = options
                if not args and not options:
                    if "args" in item:
                        item.pop("args")
                    if "options" in item:
                        item.pop("options")
                return
