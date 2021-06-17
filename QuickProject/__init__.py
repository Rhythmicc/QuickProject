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


def __latest_filename(name):
    import os
    from . import dir_char

    cur = os.getcwd()
    rec = cur
    while cur != dir_char:
        if os.path.exists(name):
            os.chdir(rec)
            return os.path.abspath(cur + dir_char + name)
        os.chdir('..')
        cur = os.getcwd()
    os.chdir(rec)
    return ''


rt_dir = os.path.dirname(__latest_filename('project_configure.csv')) + dir_char


def __sub_path(path, isExist=True):
    if not os.path.exists(path) and isExist:
        return ''
    abs_path = os.path.abspath(path)
    return abs_path.replace(rt_dir, '') if abs_path.startswith(rt_dir) else ''


class SshProtocol:
    @staticmethod
    def post_folder(user, domain, target, port, srcPath, dstPath):
        status = os.system('scp -P %s -r %s %s' % (port, srcPath, user + '@\\[' + domain + '\\]:' + target + dstPath))
        return status

    @staticmethod
    def post_file(user, domain, target, port, srcPath, dstPath):
        status = os.system('scp -P %s %s %s' % (port, srcPath, user + '@\\[' + domain + '\\]:' + target + dstPath))
        return status

    @staticmethod
    def post_all_in_folder(user, domain, target, port, dstPath):
        status = os.system('scp -P %s -r * %s' % (port, user + '@\\[' + domain + '\\]:' + target + dstPath))
        return status

    @staticmethod
    def get_file_or_folder(user, domain, target, port, srcPath, dstPath):
        return os.system('scp -P %s -r %s %s' % (port, user + '@\\[' + domain + '\\]:' + target + srcPath, dstPath))

    @staticmethod
    def ls(user, domain, target, port, dstPath):
        return os.system(f"ssh -P {port} {user + '@' + domain} 'ls {target + dstPath}'")

    @staticmethod
    def ssh(user, domain, target, port, dstPath):
        return os.system(f"ssh -P {port} -t {user + '@' + domain} 'cd {target + dstPath} ; exec $SHELL -l'")


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


def get_config():
    config_path = __latest_filename('project_configure.csv')
    config = {}
    if config_path:
        with open(config_path, 'r') as f:
            for row in f.read().strip().split('\n'):
                row = row.replace('\,', '--QPRO-IS-SPLIT--')
                row = [i.replace('--QPRO-IS-SPLIT--', ',') for i in row.split(',')]
                config[row[0]] = [i.strip() for i in row[1:]]
            for i in config:
                if i in ['server_target']:
                    continue
                config[i] = config[i][0]
    else:
        QproDefaultConsole.print(
            QproErrorString, "No file named: project_configure.csv\n May you need run:\"Qpro -init\" first!")
        exit(0)
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
