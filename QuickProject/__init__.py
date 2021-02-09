import os
import re
import colorama
from colorama import Fore, Style

colorama.init()
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
    def ssh(user, domain, target, port):
        return os.system("ssh -p %s -t %s 'cd %s ; exec $SHELL -l'" % (port, user + '@' + domain, target))


def basic_string_replace(ss):
    ss = ss.split('\n')
    ret = ''
    for i in ss:
        if '[' in i:
            replace_list = re.findall('\[(.*?)]', i)
            split_list = re.split('\[.*?]', i)
            for p in range(len(split_list)):
                ret += Fore.CYAN + split_list[p] + Style.RESET_ALL
                if p < len(replace_list):
                    ret += Fore.RED + '[' + Fore.YELLOW + replace_list[p] + Fore.RED + ']' + Style.RESET_ALL
        else:
            ret += i
        ret += '\n'
    return ret


def get_config(exit_if_failed: bool = True):
    config = {}
    try:
        with open('project_configure.csv', 'r') as f:
            for row in f.readlines():
                row = row.replace('\,', '--QPRO-IS-SPLIT--')
                row = [i.replace('--QPRO-IS-SPLIT--', ',') for i in row.split(',')]
                config[row[0]] = [i.strip() for i in row[1:]]
            for i in config:
                if i in ['server_target']:
                    continue
                config[i] = config[i][0]
    except IOError:
        if exit_if_failed:
            exit("No file named: project_configure.csv\n May you need run:\"Qpro -init\" first!")
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
