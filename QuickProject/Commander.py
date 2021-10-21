import sys
import inspect
import argparse
from inspect import isfunction
from . import QproDefaultConsole, QproErrorString


class Commander:
    def __init__(self):
        self.command_table = {}

    def command(self):
        def wrapper(func):
            if not isfunction(func):
                raise TypeError(f'{func} not a function')
            func_analyser = inspect.signature(func)
            func_args_parser = argparse.ArgumentParser()
            func_name = func.__name__.strip('_')
            if func_name in self.command_table:
                raise Exception(f'{func} already in command table')
            for arg in func_analyser.parameters.values():
                _type = None
                _default = None
                if arg.annotation != arg.empty:
                    _type = arg.annotation
                if arg.default != arg.empty:
                    _default = arg.default
                if not _default:
                    func_args_parser.add_argument(arg.name, type=_type)
                else:
                    func_args_parser.add_argument(f'--{arg.name}', required=False, type=_type, default=_default)
            self.command_table[func_name] = {'func': func, 'analyser': func_analyser, 'parser': func_args_parser}
        return wrapper

    def help(self):
        from rich.table import Table
        from rich.box import SIMPLE_HEAVY
        table = Table(show_edge=False, row_styles=['none', 'dim'], box=SIMPLE_HEAVY, title=f'[bold underline]HELP[/bold underline]\n')
        table.add_column('子命令\nSub Command', justify='center')
        table.add_column('必填参数\nRequired Args', justify='center')
        table.add_column('可选参数\nOptionnal Args', justify='center')
        for function in self.command_table:
            cur_line = ['[bold magenta]' + (function if len(self.command_table) > 1 else '*') + '[/bold magenta]']
            arg1, arg2 = [], []
            for arg in self.command_table[function]['analyser'].parameters.values():
                name = '[underline]' + arg.name + '[/underline]'
                _type = arg.annotation.__name__ if arg.annotation != arg.empty else 'Any'
                _default = arg.default if arg.default != arg.empty else None
                arg_str = f'{name}: [bold cyan]{_type}[/bold cyan]'
                if _default:
                    if _type == 'str':
                        arg_str += f" = [dim]'[/dim][yellow]{_default}[/yellow][dim]'[/dim]"
                    elif _type == 'int' or _type == 'float':
                        arg_str += f' = [bold blue]{_default}[/bold blue]'
                    else:
                        arg_str += f' = {_default}'
                    arg2.append(arg_str)
                else:
                    arg1.append(arg_str)
            cur_line += [', '.join(arg1), ', '.join(arg2)]
            table.add_row(*cur_line)
        QproDefaultConsole.print(table, justify='center')

    def __command_complete__(self):
        ls = [i for i in self.command_table]
        return ' '.join((ls if len(ls) > 1 else []) + ['--help'])

    def __call__(self):
        if len(sys.argv) < 2:
            return
        if sys.argv[1] == '--qrun-commander-complete':
            return print(self.__command_complete__())
        if sys.argv[1] == '--help':
            return self.help()
        if len(self.command_table) <= 1:
            func_info = self.command_table[list(self.command_table.keys())[0]]
            args = func_info['parser'].parse_args()
            func_info['func'](**{i[0]: i[1] for i in args._get_kwargs()})
        else:
            try:
                func_name = sys.argv[1]
                sys.argv = sys.argv[:1] + sys.argv[2:]
            except IndexError:
                QproDefaultConsole.print(QproErrorString, '至少输入一个子命令!')
            else:
                func_info = self.command_table[func_name]
                args = func_info['parser'].parse_args()
                func_info['func'](**{i[0]: i[1] for i in args._get_kwargs()})
