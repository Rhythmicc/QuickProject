import os
import sys
from rich.console import Console
try:
    import QuickStart_Rhy
    user_lang = QuickStart_Rhy.user_lang
    qs_flag = True
except:
    user_lang = 'en'
    qs_flag = False


if sys.platform.startswith('win'):
    is_win = True
    dir_char = '\\'
else:
    is_win = False
    dir_char = '/'
QproDefaultConsole = Console()
QproErrorString = '[bold red][ERRO]' if user_lang != 'zh' else '[bold red][错误]'
QproInfoString = '[bold cyan][INFO]' if user_lang != 'zh' else '[bold cyan][提示]'
QproWarnString = '[bold yellow][WARN]' if user_lang != 'zh' else '[bold yellow][警告]'
name = 'QuickProject'


def __latest_filename(filename):
    import os

    cur = os.getcwd()
    rec = cur
    while cur != dir_char:
        if os.path.exists(filename):
            os.chdir(rec)
            return os.path.abspath(cur + dir_char + filename)
        os.chdir('..')
        last = cur
        cur = os.getcwd()
        if cur == last:
            break
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
        if user:
            status = os.system('scp -P %s -r %s %s' % (port, srcPath, user + '@\\[' + domain + '\\]:' + target + dstPath))
        else:
            status = os.system('scp -P %s -r %s %s' % (port, srcPath, '\\[' + domain + '\\]:' + target + dstPath))
        return status

    @staticmethod
    def post_file(user, domain, target, port, srcPath, dstPath):
        if user:
            status = os.system('scp -P %s %s %s' % (port, srcPath, user + '@\\[' + domain + '\\]:' + target + dstPath))
        else:
            status = os.system('scp -P %s %s %s' % (port, srcPath, '\\[' + domain + '\\]:' + target + dstPath))
        return status

    @staticmethod
    def post_all_in_folder(user, domain, target, port, dstPath):
        if user:
            status = os.system('scp -P %s -r * %s' % (port, user + '@\\[' + domain + '\\]:' + target + dstPath))
        else:
            status = os.system('scp -P %s -r * %s' % (port, '\\[' + domain + '\\]:' + target + dstPath))
        return status

    @staticmethod
    def get_file_or_folder(user, domain, target, port, srcPath, dstPath):
        if user:
            return os.system('scp -P %s -r %s %s' % (port, user + '@\\[' + domain + '\\]:' + target + srcPath, dstPath))
        else:
            return os.system('scp -P %s -r %s %s' % (port, '\\[' + domain + '\\]:' + target + srcPath, dstPath))

    @staticmethod
    def ls(user, domain, target, port, dstPath):
        if user:
            return os.system(
                "ssh -P {port} {user}@{domain} 'ls {aim}'".format(
                    port=port, user=user, domain=domain, aim=target + dstPath
                ))
        else:
            return os.system(
                "ssh -P {port} {domain} 'ls {aim}'".format(
                    port=port, domain=domain, aim=target + dstPath
                )
            )

    @staticmethod
    def ssh(user, domain, target, port, dstPath):
        if user:
            return os.system(
                "ssh -P {port} -t {user}@{domain} 'cd {aim} ; exec $SHELL -l'".format(
                    port=port, user=user, domain=domain, aim=target + dstPath
                )
            )
        else:
            return os.system(
                "ssh -P {port} -t {domain} 'cd {aim} ; exec $SHELL -l'".format(
                    port=port, domain=domain, aim=target + dstPath
                )
            )


def menu_output(menu):
    from rich.table import Table, Column
    from rich.box import SIMPLE

    tb = Table(*[Column('Parameter', justify='full', style='bold yellow'),
                 Column('Description', justify='right', style='bold cyan')],
               show_edge=False, show_header=False, row_styles=['none', 'dim'], box=SIMPLE, pad_edge=False,
               title='[bold underline] {title}[dim]Author: RhythmLian\n'.format(title=menu['title']))
    for line in menu['lines']:
        tb.add_row((menu['prefix'] + ' ' if line[0].startswith('-') else '') + line[0], line[1])
    QproDefaultConsole.print(tb, justify='center')
    QproDefaultConsole.print(
        '\nDOC:' if user_lang != 'zh' else '\n文档:', 'https://rhythmlian.cn/2020/02/14/QuickProject/', justify='center'
    )


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
            QproErrorString,
            "No file named: project_configure.csv\n May you need run:\"Qpro -init\" first!"
            if user_lang != 'zh' else
            "没有文件: project_configure.csv\n可能你需要先运行: \"Qpro -init\"!"
        )
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
