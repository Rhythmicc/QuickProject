#!/usr/bin/env python3
import os
import sys
import pyperclip

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
except IOError:
    exit("No file named: project_configure.csv\n May you need run:\"Qpro -init\" first!")
argv = []
input_file = config['input_file']


def run(use_txt=False, executable_file=str(config['executable_filename'])):
    cmd = executable_file + ' '
    if argv:
        cmd += ' '.join(argv)
    cmd += (' < ' + input_file if use_txt else '')
    os.system(cmd)


def red_col(string):
    if is_win:
        return string
    return '\033[1;31m' + string + '\033[0m'


def blue_col(string):
    if is_win:
        return string
    return '\033[1;34m' + string + '\033[0m'


def main():
    to_build = '-b' in sys.argv or '-br' in sys.argv
    to_run = '-r' in sys.argv or '-b' not in sys.argv
    filename = config['compile_filename']
    flag = False
    if '-debug' in sys.argv:
        raise ImportError
    if '-h' in sys.argv:
        print(blue_col('usage: run.py:\n') +
              '  * ' + blue_col('build or run:\n') +
              '    # ' + red_col('[ -b ]') + ' : ' + blue_col('build\n') +
              '    # ' + red_col('[ -r ]') + ' : ' + blue_col('run\n') +
              '    # ' + red_col('[ -br]') + ' : ' + blue_col('build and run\n') +
              blue_col('    (it will run if neither of commands in "build or run")\n') +
              '  * ' + red_col('[ -i ]') + ' : ' + blue_col('use input.txt as input\n') +
              '  * ' + red_col('[ -if  *.* ]') + ' : ' + blue_col('set input file(*.*) as input\n') +
              '  * ' + red_col('[-if -paste]') + ' : ' + blue_col('use Clipboard content as input\n') +
              '  * ' + red_col('[ -f  *.cpp]') + ' : ' + blue_col('set build file as *.cpp\n') +
              '  * ' + red_col('[ -h ]') + ' : ' + blue_col('help\n') +
              '  * ' + red_col('[ *  ]') + ' : ' + blue_col('add parameters for program\n') +
              '  * ' + blue_col('Modify config to adjust default configuration'))
        exit(0)
    if '-f' in sys.argv:
        index = sys.argv.index('-f')
        if index == len(sys.argv) - 1:
            print(red_col('ERROR: No file with -f'))
        filename = sys.argv[index + 1]
        if not os.path.exists(filename):
            print(red_col('ERROR: No such file:%s' % filename))
            exit(-1)
        if not filename.endswith('.cpp') and not filename.endswith('.c'):
            print(red_col("ERROR: %s is not an C/CPP file" % filename))
            exit(-1)
        if filename.endswith('.c'):
            config['compile_tool'][0] = 'gcc -std=c11'
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
    o_file = config['executable_filename']
    if to_build:
        if flag:
            o_file = filename.split(dir_char)[-1].split('.')[0]
            o_file = os.path.abspath(o_file)
        os.system(config['compile_tool'][0] + ' ' + filename + ' -o ' + o_file + ' ' + config['compile_tool'][1])
    if to_run:
        add_flag = True
        for i in sys.argv[1:]:
            if not add_flag:
                add_flag = True
                continue
            if not i.startswith('-'):
                argv.append(i)
            elif i == '-if' or i == '-f':
                add_flag = False
        run('-i' in sys.argv or '-if' in sys.argv, o_file)
    if flag:
        os.remove(o_file)
