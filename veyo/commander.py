from __future__ import annotations

import argparse
import inspect
from inspect import isfunction
import os
import re
import sys
from typing import Any, Callable

from .console import ask, console, err_str, info_str
from .exec import remove
from .i18n import _lang

_ROOT_HELP = "__COMMANDER_ROOT_HELP_FUNCTION__"

zsh_comp_template = """#compdef __proj_name__

local cur prev
cur=${words[CURRENT]}
prev=${words[CURRENT-1]}

(( $+functions[___proj_name___args_comp] )) || 
___proj_name___args_comp() {
    local -a opt_args
    __sub_commands_args__
    _describe subcommand opt_args
}

(( $+functions[___proj_name___main] )) || 
___proj_name___main() {
    local -a args
    args=(
        __sub_commands__
    )

    _describe -t common-commands 'common commands' args && _ret=0
}

if (( ${#words} >= 3 )); then
    ___proj_name___args_comp
else
    ___proj_name___main
fi
"""

zsh_file_comp1 = """
    else
        _arguments -S -s '*:filename:_files'
        return
    fi
"""

zsh_file_comp2 = """
_arguments -S -s '*:filename:_files'
return
"""


_BUILTIN_TYPES: dict[str, type] = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
    "list": list,
}


def _resolve_annotation(annotation: Any, func: Callable[..., Any]) -> Any:
    if annotation is inspect.Parameter.empty or annotation is None:
        return None
    if isinstance(annotation, str):
        if annotation in _BUILTIN_TYPES:
            return _BUILTIN_TYPES[annotation]
        try:
            evaluated = eval(annotation, getattr(func, "__globals__", {}))
            if callable(evaluated):
                return evaluated
        except Exception:
            pass
        return str
    return annotation


def str2bool(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    if str(v).lower() in ("yes", "true", "t", "y", "1"):
        return True
    if str(v).lower() in ("no", "false", "f", "n", "0"):
        return False
    raise argparse.ArgumentTypeError("Boolean value expected.")


class Commander:
    """
    Lightweight decorator-driven CLI framework.
    Turns plain Python functions into subcommands with Rich help tables and Zsh completion.
    """

    def __init__(
        self,
        name: str = "app",
        seg_flag: bool = True,
        custom_complete: bool = False,
        non_complete: bool = False,
    ) -> None:
        """
        :param name: CLI application name
        :param seg_flag: Replace '_' with '-' in command and option names
        :param custom_complete: Do not register the built-in hidden `complete` subcommand
        :param non_complete: Exclude hidden commands from generated completion scripts
        """
        self.name = name
        self.seg_flag = seg_flag
        self.non_complete = non_complete
        self.command_table: dict[str, dict[str, Any]] = {}
        self.custom_complete_table: dict[str, dict[str, list[Any]]] = {}
        self.custom_help_table: dict[str, Callable[..., Any]] = {
            _ROOT_HELP: self.help
        }

        if not custom_complete:

            @self.command(hidden=True)
            def complete(is_script: bool = False) -> None:
                """
                Generate zsh completion script

                :param is_script: Also generate a sourceable rc file for script usage
                """
                return self.generate_complete(is_script=is_script)

    def _normalize_name(self, raw_name: str) -> str:
        cleaned = raw_name.strip("_")
        return cleaned.replace("_", "-") if self.seg_flag else cleaned

    def custom_complete(self, param: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """
        Register completion candidates for a subcommand parameter.

        :param param: Parameter name
        """
        norm_param = param.replace("_", "-") if self.seg_flag else param

        def wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
            if not isfunction(func):
                raise TypeError(f"{func} {_lang['NotFunction']}")
            func_name = self._normalize_name(func.__name__)
            if func_name not in self.custom_complete_table:
                self.custom_complete_table[func_name] = {}
            self.custom_complete_table[func_name][norm_param] = func()
            return func

        return wrapper

    def command(self, hidden: bool = False) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """
        Register a Python function as a CLI subcommand.

        :param hidden: Hide this command from standard help output
        """

        def wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
            if not isfunction(func):
                raise TypeError(f"{func} {_lang['NotFunction']}")
            param_doc = (
                {
                    k.strip(): v.strip()
                    for k, v in re.findall(r":param\s+(.*?):(.*?)(?:\n|$)", func.__doc__)
                }
                if func.__doc__
                else {}
            )
            func_analyser = inspect.signature(func)
            func_name = self._normalize_name(func.__name__)
            if func_name in self.command_table:
                raise ValueError(f"{func} {_lang['CommandAlreadyExists']}")

            description = (
                func.__doc__.strip().split(":param")[0].strip()
                if func.__doc__
                else func_name.replace("-", " ").replace("_", " ")
            )
            func_args_parser = argparse.ArgumentParser(
                prog=f"{self.name} {func_name}",
                description=description,
            )

            spec_args: list[dict[str, Any]] = []
            spec_options: list[dict[str, Any]] = []

            for arg in func_analyser.parameters.values():
                if arg.name.startswith("_"):
                    continue
                arg_name = arg.name.replace("_", "-") if self.seg_flag else arg.name
                _type = _resolve_annotation(arg.annotation, func)
                _default = arg.default if arg.default != arg.empty else None
                arg_desc = param_doc.get(arg.name, f"<{arg_name}>")

                if _default is None:
                    if _type is list:
                        func_args_parser.add_argument(
                            f"-{arg_name}",
                            type=str,
                            nargs="+",
                            required=True,
                            help=arg_desc,
                        )
                        spec_options.append(
                            {
                                "name": f"-{arg_name}",
                                "param": arg_name,
                                "description": arg_desc,
                            }
                        )
                    else:
                        func_args_parser.add_argument(
                            arg_name,
                            type=(str2bool if _type is bool else _type),
                            help=arg_desc,
                        )
                        spec_args.append(
                            {
                                "name": arg_name,
                                "param": arg_name,
                                "description": arg_desc,
                            }
                        )
                else:
                    if _type is list:
                        console.print(
                            err_str,
                            f"{func_name}:",
                            '"list"',
                            _lang["CantHaveDefaultValue"],
                        )
                        return func
                    _kw: dict[str, Any] = {
                        "required": False,
                        "default": _default,
                        "help": arg_desc,
                    }
                    if _type is bool:
                        _kw["action"] = "store_false" if _default is True else "store_true"
                    elif _type is not None:
                        _kw["type"] = _type
                    func_args_parser.add_argument(f"--{arg_name}", **_kw)
                    spec_options.append(
                        {
                            "name": f"--{arg_name}",
                            "param": arg_name,
                            "description": arg_desc,
                        }
                    )

            self.command_table[func_name] = {
                "func": func,
                "analyser": func_analyser,
                "parser": func_args_parser,
                "param_doc": param_doc,
                "description": description,
                "hidden": hidden,
                "spec": {
                    "name": func_name,
                    "description": description,
                    "args": spec_args,
                    "options": spec_options,
                },
            }
            return func

        return wrapper

    def _check_args(self, is_option: bool = True, shown_hidden: bool = False) -> bool:
        for info in self.command_table.values():
            if info["hidden"] and not shown_hidden:
                continue
            for arg in info["analyser"].parameters.values():
                if arg.name.startswith("_"):
                    continue
                has_default = arg.default != arg.empty and arg.default is not None
                if is_option and has_default:
                    return True
                if not is_option and not has_default:
                    return True
        return False

    def custom_help(self, root: bool = False) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """
        Register a custom help renderer for the root CLI or a specific subcommand.

        :param root: Whether this replaces the root help view
        """

        def wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
            if not isfunction(func):
                raise TypeError(f"{func} {_lang['NotFunction']}")
            if root:
                self.custom_help_table[_ROOT_HELP] = func
                return func
            func_name = self._normalize_name(func.__name__)
            self.custom_help_table[func_name] = func
            return func

        return wrapper

    def help(self, shown_hidden: bool = False) -> None:
        from rich.box import SIMPLE_HEAVY
        from rich.table import Table

        has_requir = self._check_args(False, shown_hidden)
        has_option = self._check_args(True, shown_hidden)
        table = Table(
            show_edge=False,
            row_styles=["none", "dim"],
            box=SIMPLE_HEAVY,
            title=f"[bold underline]{self.name}[/bold underline]\n",
        )
        table.add_column(_lang["SubCommand"], justify="center")
        table.add_column(_lang["Description"], justify="center")
        if has_requir:
            table.add_column(_lang["RequiredArgs"], justify="center")
        if has_option:
            table.add_column(_lang["OptionalArgs"], justify="center")

        for func_name, info in self.command_table.items():
            if info["hidden"] and not shown_hidden:
                continue
            cur_line = [f"[bold magenta]{func_name}[/bold magenta]"]
            req_args: list[str] = []
            opt_args: list[str] = []
            for arg in info["analyser"].parameters.values():
                if arg.name.startswith("_"):
                    continue
                arg_name = arg.name.replace("_", "-") if self.seg_flag else arg.name
                name_label = f"[underline]{arg_name}[/underline]"
                resolved_type = _resolve_annotation(arg.annotation, info["func"])
                _type = (
                    getattr(resolved_type, "__name__", str(resolved_type))
                    if resolved_type is not None
                    else "Any"
                )
                _default = arg.default if arg.default != arg.empty else None
                arg_str = f"{name_label}: [bold cyan]{_type}[/bold cyan]"
                if _default is not None:
                    if _type == "str":
                        arg_str += f" = [dim]'[/dim][yellow]{_default}[/yellow][dim]'[/dim]"
                    elif _type in ("int", "float"):
                        arg_str += f" = [bold blue]{_default}[/bold blue]"
                    elif _type == "bool":
                        arg_str += f" = [bold red]{_default}[/bold red]"
                    else:
                        arg_str += f" = {_default}"
                    opt_args.append(arg_str)
                else:
                    req_args.append(arg_str)
            cur_line.append(info["description"])
            if has_requir:
                cur_line.append(", ".join(req_args))
            if has_option:
                cur_line.append(", ".join(opt_args))
            table.add_row(*cur_line)
        console.print(table, justify="center")

    def __call__(self, argv: list[str] | None = None) -> Any:
        args_list = list(sys.argv[1:] if argv is None else argv)
        if not args_list or (
            args_list[0] in ("-h", "--help") and args_list[0] not in self.command_table
        ):
            return self.custom_help_table[_ROOT_HELP]()

        func_name = args_list[0]
        if func_name not in self.command_table:
            console.print(err_str, f'"{func_name}":', _lang["NoSuchCommand"])
            return self.custom_help_table[_ROOT_HELP](shown_hidden=True)

        func_info = self.command_table[func_name]
        if (
            len(args_list) == 2
            and args_list[1] in ("-h", "--help")
            and func_name in self.custom_help_table
        ):
            return self.custom_help_table[func_name]()

        parsed = func_info["parser"].parse_args(args_list[1:])
        try:
            call_kwargs = {
                k.replace("-", "_"): v for k, v in parsed._get_kwargs()
            }
            if "pre_call" in func_info:
                if func_info["pre_call"](**call_kwargs) is False:
                    return None
            return func_info["func"](**call_kwargs)
        except KeyboardInterrupt:
            return console.print(err_str, _lang["UserInterrupt"])
        except Exception:
            console.print_exception()
            sys.exit(1)

    def real_call(self, func_name: str, *args: Any, **kwargs: Any) -> Any:
        """
        Invoke a registered command function directly by name.
        """
        norm_name = self._normalize_name(func_name)
        if norm_name not in self.command_table:
            return console.print(err_str, f'"{norm_name}": {_lang["NoSuchCommand"]}')
        try:
            return self.command_table[norm_name]["func"](*args, **kwargs)
        except KeyboardInterrupt:
            return console.print(err_str, _lang["UserInterrupt"])
        except Exception:
            return console.print_exception()

    def bind_pre_call(self, func_name: str, pre_call: Callable[..., Any]) -> None:
        """
        Bind a pre-execution hook to a command. If `pre_call` returns False, execution is aborted.
        """
        norm_name = self._normalize_name(func_name)
        if norm_name not in self.command_table:
            console.print(err_str, f'"{norm_name}": {_lang["NoSuchCommand"]}')
            return
        self.command_table[norm_name]["pre_call"] = pre_call

    @staticmethod
    def _format_zsh_suggestion(item: Any) -> str:
        if isinstance(item, dict):
            name = str(item.get("name", ""))
            desc = str(item.get("description", name)).replace("'", "")
            return f"{name}:'{desc}'"
        val = str(item)
        return f"{val}:'{val}'"

    def generate_complete(self, is_script: bool = False) -> None:
        """
        Generate Zsh completion script under `complete/zsh/_{project_name}`.

        :param is_script: Also write `.{project_name}rc` in current directory
        """
        project_name = self.name.replace("_", "-") if self.seg_flag else self.name

        if os.path.exists("complete") and os.path.isdir("complete"):
            if ask(
                {
                    "type": "confirm",
                    "message": _lang["OverwriteCompleteDir"],
                    "default": False,
                }
            ):
                remove("complete")
            else:
                return

        os.makedirs(os.path.join("complete", "zsh"), exist_ok=True)

        cur_sub_cmds: list[str] = []
        sub_cmd_args: list[str] = []

        for cmd_name, info in self.command_table.items():
            if self.non_complete and info["hidden"]:
                continue
            spec = info["spec"]
            cmd_desc = str(spec["description"]).replace("'", "")
            cur_sub_cmds.append(f"{cmd_name}:'{cmd_desc}'")

            custom_map = self.custom_complete_table.get(cmd_name, {})
            sub_cmd_opts: list[str] = []

            for arg in spec["args"]:
                suggestions = custom_map.get(arg["param"])
                if suggestions:
                    for item in suggestions:
                        sub_cmd_opts.append(self._format_zsh_suggestion(item))
                elif arg["name"].startswith("-"):
                    desc = str(arg["description"]).replace("'", "")
                    sub_cmd_opts.append(f"{arg['name']}:'{desc}'")

            for opt in spec["options"]:
                suggestions = custom_map.get(opt["param"])
                if suggestions:
                    for item in suggestions:
                        sub_cmd_opts.append(self._format_zsh_suggestion(item))
                elif opt["name"].startswith("-"):
                    desc = str(opt["description"]).replace("'", "")
                    sub_cmd_opts.append(f"{opt['name']}:'{desc}'")

            if sub_cmd_opts:
                block = (
                    f"if [[ ${{prev}} == {cmd_name} ]]; then\n"
                    f"        opt_args=(\n"
                    f"            " + "\n            ".join(sub_cmd_opts) + "\n"
                    f"        )"
                )
                sub_cmd_args.append(block)

        template = zsh_comp_template.replace("__proj_name__", project_name)
        template = template.replace("__sub_commands__", "\n        ".join(cur_sub_cmds))
        template = template.replace(
            "__sub_commands_args__",
            "\n    el".join(sub_cmd_args) + zsh_file_comp1
            if sub_cmd_args
            else zsh_file_comp2,
        )

        with open(
            os.path.join("complete", "zsh", f"_{project_name}"), "w", encoding="utf-8"
        ) as f:
            f.write(template)

        if is_script:
            with open(f".{project_name}rc", "w", encoding="utf-8") as f:
                print("export FPATH=$FPATH:$(pwd)/complete/zsh", file=f)
                print("autoload -Uz compinit", file=f)
                print("zstyle ':completion:*' menu select", file=f)
                print("compinit", file=f)
            console.print(info_str, _lang["ScriptComplete"].format(project_name))

    def __add__(self, other: Commander) -> Commander:
        """Merge commands from another Commander instance into this one."""
        if not isinstance(other, Commander):
            raise TypeError(
                f"unsupported operand type(s) for +: '{type(self).__name__}' and '{type(other).__name__}'"
            )
        self.command_table.update(other.command_table)
        self.custom_complete_table.update(other.custom_complete_table)
        for k, v in other.custom_help_table.items():
            if k != _ROOT_HELP:
                self.custom_help_table[k] = v
        return self
