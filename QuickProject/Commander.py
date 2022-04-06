import re
import sys
import inspect
import argparse
from inspect import isfunction
from . import QproDefaultConsole, QproErrorString, user_lang


class Commander:
    def __init__(self):
        self.command_table = {}
        self.fig_table = [{'name': '--help', 'description': '获取帮助'}]

    def command(self):
        def wrapper(func):
            if not isfunction(func):
                raise TypeError(f'{func} not a function')
            param_doc = {i[0].strip(): i[1].strip() for i in re.findall(':param(.*?):(.*?)\n', func.__doc__, re.S)}
            func_analyser = inspect.signature(func)
            func_args_parser = argparse.ArgumentParser()
            func_name = func.__name__.strip('_')

            func_fig = {'name': func_name, 'description': func.__doc__.strip().split(':param')[0].strip(), 'args': []}
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
                    if _type == list:
                        func_args_parser.add_argument(f'-{arg.name}', type=str, nargs='+')
                        func_fig['args'].append({
                            'name': f'-{arg.name}',
                            'description': param_doc.get(arg.name, f'<{arg.name}>'),
                            'args': {
                                'name': arg.name,
                                'description': param_doc.get(arg.name, f'<{arg.name}>'),
                                'isVariadic': True
                            }
                        })
                    else:
                        func_args_parser.add_argument(arg.name, type=_type)
                        func_fig['args'].append({
                            'name': arg.name,
                            'description': param_doc.get(arg.name, f'<{arg.name}>'),
                        })
                else:
                    func_args_parser.add_argument(f'--{arg.name}', required=False, type=_type, default=_default)
                    func_fig['args'].append({
                        'name': f'--{arg.name}',
                        'description': param_doc.get(arg.name, f'<{arg.name}>'),
                        'isOptional': True,
                        'args': {
                            'name': arg.name,
                            'description': param_doc.get(arg.name, f'<{arg.name}>'),
                        }
                    })
            self.fig_table.append(func_fig)
            self.command_table[func_name] = {'func': func, 'analyser': func_analyser, 'parser': func_args_parser, 'param_doc': param_doc}
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

    def __command_complete__(self, route_path: list):
        """

        :param route_path:
        :return:
        """
        if not route_path and len(self.command_table) > 1:
            ls = [
                f"{i}:{self.command_table[i]['func'].__doc__.strip().split(':param')[0].strip() if self.command_table[i]['func'].__doc__ else 'NONE'}"
                for i in self.command_table
            ]
            return '\n'.join(
                (ls if len(ls) > 1 else []) + ["--help:应用帮助" if user_lang == 'zh' else '--help:Application help']
            )
        if len(self.command_table) > 1:
            call_func = route_path[0]
            has_args = [i.strip().strip('--') for i in route_path[1:]]
        else:
            call_func = list(self.command_table.keys())[0]
            has_args = [i.strip().strip('--') for i in route_path]
        if call_func not in self.command_table:
            return '错误:无该命令' if user_lang != 'zh' else 'ERROR:No such command'
        call_analyser = self.command_table[call_func]['analyser']
        param_doc = self.command_table[call_func]['param_doc']
        res = []
        for arg in call_analyser.parameters.values():
            if arg.name in has_args:
                continue
            if arg.default != arg.empty:
                res.append(f'--{arg.name}:{param_doc[arg.name].replace(" ", "_") if arg.name in param_doc else "No Description" if user_lang != "zh" else "无参数描述"}')
        return '\n'.join(res + ["--help:应用帮助" if user_lang == 'zh' else '--help:Application help'])

    def _fig_complete_(self):
        import json
        return json.dumps(self.fig_table)

    def __call__(self):
        if len(sys.argv) >= 2:
            if sys.argv[1] == '--qrun-commander-complete':
                if 'qrun' in sys.argv:
                    sys.argv.remove('qrun')
                return print(self.__command_complete__(sys.argv[2:]))
            elif sys.argv[1] == '--qrun-fig-complete':
                return print(self._fig_complete_())
            if sys.argv[1] == '--help':
                return self.help()
        if len(self.command_table) <= 1:
            func_info = self.command_table[list(self.command_table.keys())[0]]
            args = func_info['parser'].parse_args()
            try:
                return func_info['func'](**{i[0]: i[1] for i in args._get_kwargs()})
            except:
                return QproDefaultConsole.print_exception()
        else:
            try:
                func_name = sys.argv[1]
                sys.argv = sys.argv[:1] + sys.argv[2:]
            except IndexError:
                return QproDefaultConsole.print(
                    QproErrorString, '至少输入一个子命令!' if user_lang == 'zh' else 'Input at least one sub command!'
                )
            else:
                func_info = self.command_table[func_name]
                args = func_info['parser'].parse_args()
                try:
                    return func_info['func'](**{i[0]: i[1] for i in args._get_kwargs()})
                except:
                    return QproDefaultConsole.print_exception()

    def real_call(self, func_name: str, *args, **kwargs):
        """
        调用被装饰为命令的函数

        :param func_name: 注册的函数名
        :param args: 参数
        :param kwargs: 参数
        :return:
        """
        if func_name not in self.command_table:
            return QproDefaultConsole.print(
                QproErrorString,  f'{func_name} 未被注册!' if user_lang == 'zh' else f'{func_name} not registered!'
            )
        return self.command_table[func_name]['func'](*args, **kwargs)
