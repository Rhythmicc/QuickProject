import os
import re
import sys

if sys.platform.startswith('win'):
    is_win = True
    dir_char = '\\'
else:
    is_win = False
    dir_char = '/'


run = """#!/usr/bin/env python3
import os
import sys
import pyperclip

base_dir = sys.path[0]
if sys.platform.startswith('win'):
    is_win = True
    dir_char = '\\\\'
else:
    is_win = False
    dir_char = '/'
base_dir += dir_char

config = {
    'compile_tool': ['__COMPILE_TOOL__', ''],
    'compile_filename': base_dir + '__COMPILE_FILENAME__',
    'executable_filename': base_dir + 'cmake-build-debug' + dir_char + '__PROJECT_NAME__',
    'input_file': base_dir + 'cmake-build-debug' + dir_char + 'input.txt'
}


def run(use_txt=False, executable_file=config['executable_filename']):
    cmd = executable_file + ' '
    if argv:
        cmd += ' '.join(argv)
    cmd += (' < ' + input_file if use_txt else '')
    os.system(cmd)


def red_col(string):
    if is_win:
        return string
    return '\\033[1;31m' + string + '\\033[0m'


def blue_col(string):
    if is_win:
        return string
    return '\\033[1;34m' + string + '\\033[0m'


if __name__ == '__main__':
    cmd_ls = ['-b', '-r', '-br', '-h', '-f', '-if', '-paste']
    to_build = '-b' in sys.argv or '-br' in sys.argv
    to_run = '-r' in sys.argv or '-b' not in sys.argv
    filename = config['compile_filename']
    flag = False
    input_file = config['input_file']
    if '-h' in sys.argv:
        print(blue_col('usage: run.py:\\n') +
              '  * ' + blue_col('build or run:\\n') +
              '    # ' + red_col('[ -b ]') + ' : ' + blue_col('build\\n') +
              '    # ' + red_col('[ -r ]') + ' : ' + blue_col('run\\n') +
              '    # ' + red_col('[ -br]') + ' : ' + blue_col('build and run\\n') +
              blue_col('    (it will run if neither of commands in "build or run")\\n') +
              '  * ' + red_col('[ -i ]') + ' : ' + blue_col('use input.txt as input\\n') +
              '  * ' + red_col('[ -if  *.* ]') + ' : ' + blue_col('set input file(*.*) as input\\n') +
              '  * ' + red_col('[-if -paste]') + ' : ' + blue_col('use Clipboard content as input\\n') +
              '  * ' + red_col('[ -f  *.cpp]') + ' : ' + blue_col('set build file as *.cpp\\n') +
              '  * ' + red_col('[ -h ]') + ' : ' + blue_col('help\\n') +
              '  * ' + red_col('[ *  ]') + ' : ' + blue_col('add parameters for program\\n') +
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
            with open(base_dir+'cmake-build-debug' + dir_char + 'input.txt','w') as f:
                f.write(pyperclip.paste())
        else:
            input_file = tmp_file
            if not os.path.exists(input_file):
                print(red_col('ERROR: No such file:%s' % input_file))
                exit(-1)
    o_file = config['executable_filename']
    if to_build:
        if flag:
            o_file = base_dir + filename.split(dir_char)[-1].split('.')[0]
        os.system(config['compile_tool'][0] + ' ' + filename + ' -o ' + o_file + ' ' + config['compile_tool'][1])
    if to_run:
        argv = []
        add_flag = True
        for i in enumerate(sys.argv, 1):
            if i[1] not in cmd_ls and add_flag:
                argv.append(i[1])
            if not add_flag:
                add_flag = True
            if i[1] == '-f' or i[1] == '-if':
                add_flag = False
        run('-i' in sys.argv or '-if' in sys.argv, o_file)
    if flag:
        os.remove(o_file)
"""


refresh = """#!/usr/bin/env python3
import sys

base_dir = sys.path[0]
if sys.platform.startswith('win'):
    dir_char = '\\\\'
else:
    dir_char = '/'
base_dir += dir_char

if __name__ == '__main__':
    with open(base_dir + 'template/main', 'r') as f:
        content = f.read()
    with open(base_dir + 'main.cpp', 'w') as f:
        f.write(content)

"""


TextCmp = """#!/usr/bin/env python3
import difflib
import os
import webbrowser as wb
import sys
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox


base_dir = sys.path[0]
if sys.platform.startswith('win'):
    dir_char = '\\\\'
else:
    dir_char = '/'
base_dir += dir_char


def read_file(filename):
    try:
        with open(filename, 'r') as f:
            return f.readlines()
    except IOError:
        messagebox.showerror("ERROR:", "没有找到文件:%s" % filename)
        return


def compare_file(f1, f2, out_file):
    file1_content = read_file(f1.strip())
    file2_content = read_file(f2.strip())
    d = difflib.HtmlDiff()
    result = d.make_file(file1_content, file2_content)
    with open(out_file, 'w') as f:
        f.writelines(result)


def get_path1():
    global file1
    file1 = filedialog.askopenfilename()
    path1.set(file1)


def get_path2():
    global file2
    file2 = filedialog.askopenfilename()
    path2.set(file2)


def get_path3():
    global file3
    file3 = filedialog.askopenfilename()
    path3.set(file3)
    ll.configure(fg='black')


def cmp():
    if not file1 or not file2:
        messagebox.showerror("文件数不足", "请选择两个文件进行对比")
        return
    if file3 == '使用默认输入文件':
        os.system('./run.py -br -i -f %s > %scontent1' % (file1, base_dir))
        os.system('./run.py -br -i -f %s > %scontent2' % (file2, base_dir))
    else:
        os.system('./run.py -br -if %s -f %s > %scontent1' % (file3, file1, base_dir))
        os.system('./run.py -br -if %s -f %s > %scontent2' % (file3, file2, base_dir))
    compare_file(base_dir + 'content1', base_dir + 'content2', './res.html')
    wb.open('file://%sres.html' % base_dir)
    os.remove(base_dir + 'content1')
    os.remove(base_dir + 'content2')


if __name__ == '__main__':
    win = tk.Tk()
    win.title('对拍器')
    file1, path1 = '', tk.StringVar()
    file2, path2 = '', tk.StringVar()
    file3, path3 = '使用默认输入文件', tk.StringVar()
    path3.set(file3)
    width = 30
    tk.Label(win, text='%12s' % "文件1路径:").grid(row=0, column=0)
    tk.Label(win, textvariable=path1, width=width).grid(row=0, column=1)
    tk.Button(win, text="路径选择", command=get_path1).grid(row=0, column=2)
    tk.Label(win, text='%12s' % "文件2路径:").grid(row=1, column=0)
    tk.Label(win, textvariable=path2, width=width).grid(row=1, column=1)
    tk.Button(win, text="路径选择", command=get_path2).grid(row=1, column=2)
    tk.Label(win, text='%12s' % "输入文件:").grid(row=2, column=0)
    ll = tk.Label(win, textvariable=path3, width=width, fg='red')
    ll.grid(row=2, column=1)
    tk.Button(win, text="路径选择", command=get_path3).grid(row=2, column=2)
    tk.Button(win, text="对比", command=cmp).grid(row=3, column=1)
    tk.mainloop()

"""


def main():
    global run
    if not os.path.exists('CMakeLists.txt'):
        exit("Not an CLion Project!")
    with open("CMakeLists.txt", 'r') as f:
        content = f.read()
    project_name = re.findall('project\((.*?)\)', content)[0].split()[0]
    if '.cpp' in content or '.CPP' in content:
        is_cpp = True
    else:
        is_cpp = False
    print('Project name:%s(%s)' % (project_name, 'CPP' if is_cpp else 'C'))
    if '-add' not in sys.argv:
        print('usage:\n'
              '\t * [-add script]: add script.py to your project')
        exit('wrong usage')
    index = sys.argv.index('-add')
    scripts = sys.argv[index + 1:]
    for script in scripts:
        if script == 'run':
            print('creating run.py')
            run = run.replace('__COMPILE_TOOL__', 'g++ -std=c++11' if is_cpp else 'gcc -std=c11')
            run = run.replace('__COMPILE_FILENAME__', 'main.cpp' if is_cpp else 'main.c')
            run = run.replace('__PROJECT_NAME__', project_name)
            with open('cmake-build-debug' + dir_char + 'input.txt', 'w') as f:
                f.write('edit this file to make input')
            with open('run.py', 'w') as f:
                f.write(run)
            if not is_win:
                os.system('chmod a+x run.py')
        elif script == 'refresh':
            print("creating refresh.py")
            if not os.path.exists('template'):
                os.mkdir('template')
            with open('main.cpp' if is_cpp else 'main.c', 'r')as f:
                main_cont = f.read()
            with open('template' + dir_char + 'main', 'w') as f:
                f.write(main_cont)
            with open('refresh.py', 'w') as f:
                f.write(refresh)
            if not is_win:
                os.system('chmod a+x refresh.py')
        elif script == 'TextCmp':
            print('creating TextCmp.py')
            with open('TextCmp.py', 'w') as f:
                f.write(TextCmp)
            if not is_win:
                os.system('chmod a+x TextCmp.py')
