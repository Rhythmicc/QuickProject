import os
import sys
import pyperclip
from colorama import Fore, Style
from QuickProject.Qpro import basic_string_replace

if sys.platform.startswith('win'):
    is_win = True
    dir_char = '\\'
else:
    is_win = False
    dir_char = '/'

config = {}
try:
    with open('project_configure.csv', 'r') as f:
        for row in f.readlines():
            row = row.split(',')
            config[row[0]] = [i.strip() for i in row[1:]]
        for i in config:
            if i != 'compile_tool':
                config[i] = config[i][0]
        if config['template_root'] and not config['template_root'].endswith(dir_char):
            config['template_root'] += dir_char
except IOError:
    exit("No file named: project_configure.csv\n May you need run:\"Qpro -init\" first!")
argv = []
retain_arg = ['-br', '-b', '-r', '-h', '-i']
has_recog = {i: False for i in retain_arg}


def run(use_txt=False, executable_file=str(config['executable_filename'])):
    cmd = executable_file + ' '
    if argv:
        cmd += ' '.join(argv)
    if cmd.strip():
        cmd += (' < ' + config['input_file'] if use_txt else '')
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
        print(basic_string_replace('(run.py) usage:\n'
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
    record_file_name = ''
    if config['compile_tool'][0] and to_build:
        clang = ['clang', 'gcc', 'g++']
        use_lang = config['compile_tool'][0].split()[0]
        if use_lang in clang or 'gcc' in use_lang:
            if flag:
                o_file = filename.split(dir_char)[-1].split('.')[0]
                o_file = os.path.abspath(o_file)
            os.system(config['compile_tool'][0] + ' ' + filename + ' -o ' + o_file + ' ' + config['compile_tool'][1])
        else:  # java
            if flag:
                o_file = filename.split(dir_char)[-1].split('.')[0]
                record_file_name = o_file
                o_file = ' '.join(config['executable_filename'].split()[:-1]) + ' ' + o_file
            os.system(config['compile_tool'][0] + ' ' + filename + ' ' + config['compile_tool'][1])
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
    if config['compile_tool'][0] and flag:
        if config['compile_tool'][0].split()[0] == 'javac':
            os.remove('dist' + dir_char + record_file_name + '.class')
        else:
            os.remove(o_file)


if __name__ == '__main__':
    main()
