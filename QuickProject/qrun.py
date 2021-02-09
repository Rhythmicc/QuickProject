import os
import sys
import pyperclip
import colorama
from colorama import Fore, Style
from QuickProject import basic_string_replace, get_config

colorama.init()
if sys.platform.startswith('win'):
    is_win = True
    dir_char = '\\'
else:
    is_win = False
    dir_char = '/'

config = get_config()
argv = []
retain_arg = ['-br', '-b', '-r', '-h', '-i']
has_recog = {i: False for i in retain_arg}


def run(use_txt=False, executable_file=str(config['executable_filename'])):
    if os.path.exists(executable_file):
        cmd = executable_file.replace(' ', '\ ') + ' '
    else:
        cmd = executable_file + ' '
    if argv:
        cmd += ' '.join(argv)
    if cmd.strip():
        cmd += (' < "' + config['input_file'] + '"' if use_txt else '')
        os.system(cmd)


def red_col(string):
    return Fore.RED + string + Style.RESET_ALL


def main():
    to_build = '-b' in sys.argv or '-br' in sys.argv
    to_run = '-r' in sys.argv or '-b' not in sys.argv
    filename = config['compile_filename']
    flag = False
    if '-debug' in sys.argv:
        raise ImportError
    if '-h' in sys.argv:
        print(basic_string_replace('(qrun.py) usage:\n'
                                   '  * build or run:\n'
                                   '    # [ -b ]: build\n'
                                   '    # [ -r ]: run\n'
                                   '    # [ -br]: build and run\n'
                                   '    (it will run if neither of commands in "build or run")\n'
                                   '  * [ -i ]: use input.txt as input\n'
                                   '  * [ -if  *.*  ]: set input file(*.*) as input\n'
                                   '  * [ -if -paste]: use Clipboard content as input\n'
                                   '  * [ -f  *.cpp ]: set build file as *.cpp\n'
                                   '  * [ -h ]: help\n'
                                   '  * [ *  ]: add parameters for program\n'
                                   '  * Modify config to adjust default configuration'))
        exit(0)
    if '-f' in sys.argv:
        index = sys.argv.index('-f')
        if index == len(sys.argv) - 1:
            print(red_col('ERROR: No file with -f'))
        filename = sys.argv[index + 1]
        if not os.path.exists(filename):
            print(red_col('ERROR: No such file:%s' % filename))
            exit(-1)
        flag = True
    if '-if' in sys.argv:
        index = sys.argv.index('-if')
        if index == len(sys.argv) - 1:
            print(red_col('ERROR: No file with -if'))
        tmp_file = sys.argv[index + 1]
        if tmp_file == '-paste':
            with open('cmake-build-debug' + dir_char + 'input.txt', 'w') as file:
                file.write(pyperclip.paste())
        else:
            __input_file__ = tmp_file
            if not os.path.exists(__input_file__):
                print(red_col('ERROR: No such file:%s' % __input_file__))
                exit(-1)
            config['input_file'] = __input_file__
    o_file = config['executable_filename']
    record_file_name = os.path.basename(filename).split('.')[0]
    if config['compile_tool'] and to_build:
        os.system(config['compile_tool'].replace(config['compile_filename'], filename))
    if to_run:
        add_flag = True
        for i in sys.argv[1:]:
            if not add_flag:
                add_flag = True
                continue
            if i in retain_arg:
                if has_recog[i]:
                    argv.append(i)
                else:
                    has_recog[i] = True
            elif i == '-if' or i == '-f':
                add_flag = False
            else:
                argv.append(i)
        run('-i' in sys.argv or '-if' in sys.argv, o_file)
    if config['compile_tool'] and flag:
        if config['compile_tool'].split()[0] == 'javac':
            os.remove('dist' + dir_char + record_file_name + '.class')
        else:
            os.remove(o_file)


if __name__ == '__main__':
    main()
