import os
import sys
from rich.console import Console


if sys.platform.startswith('win'):
    is_win = True
    dir_char = '\\'
else:
    is_win = False
    dir_char = '/'
QproDefaultConsole = Console()
QproErrorString = '[bold red][ERRO]'
QproInfoString = '[bold cyan][INFO]'
QproWarnString = '[bold yellow][WARN]'
name = 'QuickProject'


class SshProtocol:
    @staticmethod
    def post_folder(user, domain, target, port, path):
        status = os.system('scp -P %s -r %s %s' % (port, path, user + '@\\[' + domain + '\\]:' + target + path))
        return status

    @staticmethod
    def post_file(user, domain, target, port, path):
        status = os.system('scp -P %s %s %s' % (port, path, user + '@\\[' + domain + '\\]:' + target + path))
        return status

    @staticmethod
    def post_all_in_folder(user, domain, target, port):
        status = os.system('scp -P %s -r * %s' % (port, user + '@\\[' + domain + '\\]:' + target))
        return status

    @staticmethod
    def get_file_or_folder(user, domain, target, port, path):
        return os.system('scp -P %s -r %s %s' % (port, user + '@\\[' + domain + '\\]:' + target + path, path))

    @staticmethod
    def ls(user, domain, target, port, path):
        return os.system(f"ssh -P {port} {user + '@' + domain} 'ls {target + path}'")

    @staticmethod
    def ssh(user, domain, target, port):
        return os.system(f"ssh -P {port} -t {user + '@' + domain} 'cd {target} ; exec $SHELL -l'")


def menu_output(menu):
    from rich.table import Table, Column
    from rich.box import SIMPLE

    tb = Table(*[Column('Parameter', justify='full', style='bold yellow'),
                 Column('Description', justify='right', style='bold cyan')],
               show_edge=False, show_header=False, row_styles=['none', 'dim'], box=SIMPLE, pad_edge=False,
               title=f'[bold underline] {menu["title"]}[dim]Author: RhythmLian\n')
    for line in menu['lines']:
        tb.add_row((menu['prefix'] + ' ' if line[0].startswith('-') else '') + line[0], line[1])
    QproDefaultConsole.print(tb, justify='center')
    QproDefaultConsole.print('\nDOC: https://rhythmlian.cn/2020/02/14/QuickProject/', justify='center')


def get_config(exit_if_failed: bool = True):
    config = {}
    try:
        with open('project_configure.csv', 'r') as f:
            for row in f.read().strip().split('\n'):
                row = row.replace('\,', '--QPRO-IS-SPLIT--')
                row = [i.replace('--QPRO-IS-SPLIT--', ',') for i in row.split(',')]
                config[row[0]] = [i.strip() for i in row[1:]]
            for i in config:
                if i in ['server_target']:
                    continue
                config[i] = config[i][0]
    except IOError:
        if exit_if_failed:
            QproDefaultConsole.print(
                QproErrorString, "No file named: project_configure.csv\n May you need run:\"Qpro -init\" first!")
            exit(0)
        else:
            return False
    return config


def get_server_target(st=None):
    if not st:
        config = get_config()['server_target']
        ls, port = config[0].split(':'), config[1]
    else:
        ls, port = st[0].split(':'), st[1]
    if len(ls) > 2:
        server = ':'.join(ls[:8])
        target = ':'.join(ls[8:])
    else:
        server, target = ls
    return server, target, port
