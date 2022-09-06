import re
import sys
import inspect
import argparse
from inspect import isfunction
from . import QproDefaultConsole, QproErrorString, user_lang


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


class Commander:
    def __init__(self, seg_flag: bool = False):
        """
        QuickProject的Commander类，帮助快速构建一个命令工具

        :param seg_flag: 是否将函数名中的'_'替换为'-'
        """
        self.command_table = {}
        self.fig_table = [{'name': '--help', 'description': '获取帮助'}]
        self.custom_complete_table = {}
        self.seg_flag = seg_flag

    def custom_complete(self, param: str):
        """
        自定义补全

        :param param: 参数名
        :return:
        """
        def wrapper(func):
            if not isfunction(func):
                raise TypeError(f'{func} not a function')
            func_name = func.__name__.strip('_')
            if self.seg_flag:
                func_name = func_name.replace('_', '-')
            if func_name not in self.custom_complete_table:
                self.custom_complete_table[func_name] = {}
            self.custom_complete_table[func_name][param] = func()
        return wrapper

    def __op_cur_args(self, func_name, cur_args, name):
        if name in self.custom_complete_table.get(func_name, {}):
            cur_args['suggestions'] = self.custom_complete_table[func_name][name]

    def command(self):
        def wrapper(func):
            if not isfunction(func):
                raise TypeError(f'{func} not a function')
            param_doc = {i[0].strip(): i[1].strip() for i in re.findall(':param(.*?):(.*?)\n', func.__doc__, re.S)} if func.__doc__ else {}
            func_analyser = inspect.signature(func)
            func_args_parser = argparse.ArgumentParser()
            func_name = func.__name__.strip('_')
            description = func.__doc__.strip().split(':param')[0].strip() if func.__doc__ else func_name.replace('_', ' ')
            if self.seg_flag:
                func_name = func_name.replace('_', '-')
            func_fig = {'name': func_name, 'description': description, 'args': []}
            if func_name in self.command_table:
                raise Exception(f'{func} already in command table')
            for arg in func_analyser.parameters.values():
                _type = None
                _default = None
                if arg.annotation != arg.empty:
                    _type = arg.annotation
                if arg.default != arg.empty:
                    _default = arg.default
                if _default is None:
                    if _type == list:
                        func_args_parser.add_argument(f'-{arg.name}', type=str, nargs='+')
                        cur_args = {
                            'name': arg.name,
                            'description': param_doc.get(arg.name, f'<{arg.name}>'),
                            'isVariadic': True
                        }
                        self.__op_cur_args(func_name, cur_args, arg.name)
                        if 'file' in arg.name.lower() or 'path' in arg.name.lower():
                            cur_args['template'] = ['filepaths', 'folders']
                        func_fig['args'].append({
                            'name': f'-{arg.name}',
                            'description': param_doc.get(arg.name, f'<{arg.name}>'),
                            'args': cur_args
                        })
                    else:
                        func_args_parser.add_argument(arg.name, type=_type if _type != bool else str2bool)
                        cur_args = {
                            'name': arg.name,
                            'description': param_doc.get(arg.name, f'<{arg.name}>'),
                        }
                        self.__op_cur_args(func_name, cur_args, arg.name)
                        if 'file' in arg.name.lower() or 'path' in arg.name.lower():
                            cur_args['template'] = ['filepaths', 'folders']
                        func_fig['args'].append(cur_args)
                else:
                    if _type == list:
                        QproDefaultConsole.print(QproErrorString, f'{func_name}:', '"list" 类型不可以有默认值' if user_lang == 'zh' else '"list" type can not have default value')
                        return
                    _kw = {'required': False, 'type': _type, 'default': _default}
                    if _type == bool:
                        _kw.pop('type')
                        _kw['action'] = 'store_true'
                    func_args_parser.add_argument(f'--{arg.name}', **_kw)
                    cur_args = {
                        'name': arg.name,
                        'description': param_doc.get(arg.name, f'<{arg.name}>'),
                    }
                    self.__op_cur_args(func_name, cur_args, arg.name)
                    if 'file' in arg.name.lower() or 'path' in arg.name.lower():
                        cur_args['template'] = ['filepaths', 'folders']
                    func_fig['args'].append({
                        'name': f'--{arg.name}',
                        'description': param_doc.get(arg.name, f'<{arg.name}>'),
                        'isOptional': True,
                        'args': cur_args
                    })
            self.fig_table.append(func_fig)
            self.command_table[func_name] = {'func': func, 'analyser': func_analyser, 'parser': func_args_parser, 'param_doc': param_doc, 'description': description}
        return wrapper

    def _check_args_(self, is_option: bool = True):
        res = False
        if is_option:
            for function in self.command_table:
                for arg in self.command_table[function]['analyser'].parameters.values():
                    _default = arg.default if arg.default != arg.empty else None
                    if _default is not None:
                        res = True
                        break
                if res:
                    break
        else:
            for function in self.command_table:
                for arg in self.command_table[function]['analyser'].parameters.values():
                    _default = arg.default if arg.default != arg.empty else None
                    if _default is None:
                        res = True
                        break
                if res:
                    break
        return res

    def help(self):
        from rich.table import Table
        from rich.box import SIMPLE_HEAVY

        has_requir = self._check_args_(False)
        has_option = self._check_args_(True)
        table = Table(show_edge=False, row_styles=['none', 'dim'], box=SIMPLE_HEAVY, title=f'[bold underline]帮助 HELP[/bold underline]\n')
        table.add_column('子命令\nSub Command', justify='center')
        table.add_column('描述\nDescription', justify='center')
        if has_requir:
            table.add_column('必填参数\nRequired Args', justify='center')
        if has_option:
            table.add_column('可选参数\nOptionnal Args', justify='center')
        for function in self.command_table:
            cur_line = ['[bold magenta]' + function + '[/bold magenta]']
            arg1, arg2 = [], []
            for arg in self.command_table[function]['analyser'].parameters.values():
                name = '[underline]' + arg.name + '[/underline]'
                _type = arg.annotation.__name__ if arg.annotation != arg.empty else 'Any'
                _default = arg.default if arg.default != arg.empty else None
                arg_str = f'{name}: [bold cyan]{_type}[/bold cyan]'
                if _default is not None:
                    if _type == 'str':
                        arg_str += f" = [dim]'[/dim][yellow]{_default}[/yellow][dim]'[/dim]"
                    elif _type == 'int' or _type == 'float':
                        arg_str += f' = [bold blue]{_default}[/bold blue]'
                    elif _type == 'bool':
                        arg_str += f' = [bold red]{_default}[/bold red]'
                    else:
                        arg_str += f' = {_default}'
                    arg2.append(arg_str)
                else:
                    arg1.append(arg_str)
            cur_line.append(self.command_table[function]['description'])
            if has_requir:
                cur_line.append(', '.join(arg1))
            if has_option:
                cur_line.append(', '.join(arg2))
            table.add_row(*cur_line)
        QproDefaultConsole.print(table, justify='center')

    def __command_complete__(self, route_path: list):
        """

        :param route_path:
        :return:
        """
        if not route_path:
            ls = [
                f"{i}:{self.command_table[i]['func'].__doc__.strip().split(':param')[0].strip().replace(' ', '_') if self.command_table[i]['func'].__doc__ else 'NONE'}"
                for i in self.command_table
            ]
            return '\n'.join(
                ls + ["--help:应用帮助" if user_lang == 'zh' else '--help:Application help']
            )
        call_func = route_path[0]
        has_args = [i.strip().strip('--') for i in route_path[1:]]
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
        return json.dumps(self.fig_table, ensure_ascii=False)

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
        try:
            func_name = sys.argv[1]
            sys.argv = sys.argv[:1] + sys.argv[2:]
            if func_name not in self.command_table:
                return QproDefaultConsole.print(QproErrorString, f'"{func_name}"' + (':无该命令' if user_lang != 'zh' else ':No such command'))
        except IndexError:
            return QproDefaultConsole.print(
                QproErrorString, '至少输入一个子命令!' if user_lang == 'zh' else 'Input at least one sub command!'
            )
        else:
            func_info = self.command_table[func_name]
            args = func_info['parser'].parse_args()
            try:
                if 'pre_call' in func_info:
                    func_info['pre_call'](**{i[0]: i[1] for i in args._get_kwargs()})
                return func_info['func'](**{i[0]: i[1] for i in args._get_kwargs()})
            except KeyboardInterrupt:
                return QproDefaultConsole.print(QproErrorString, '用户中断')
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
        if self.seg_flag:
            func_name = func_name.replace('_', '-')
        if func_name not in self.command_table:
            return QproDefaultConsole.print(
                QproErrorString,  f'{func_name} 未被注册!' if user_lang == 'zh' else f'{func_name} not registered!'
            )
        try:
            return self.command_table[func_name]['func'](*args, **kwargs)
        except KeyboardInterrupt:
            return QproDefaultConsole.print(QproErrorString, '用户中断')
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
                QproErrorString,  f'{func_name} 未被注册!' if user_lang == 'zh' else f'{func_name} not registered!'
            )
        self.command_table[func_name]['pre_call'] = pre_call
