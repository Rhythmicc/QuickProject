import os
import re
import sys
import csv

if sys.platform.startswith('win'):
    is_win = True
    dir_char = '\\'
else:
    is_win = False
    dir_char = '/'


def main():
    if '-h' in sys.argv or '-init' not in sys.argv:
        print('usage:\n'
              '\t * [Qpro -init ]: add configure so that command \"Qpro*\" can work\n'
              '\t * [Qpro -h    ]: help\n'
              '\t * [QproRefresh]: refresh your project\n'
              '\t * [QproRun *  ]: run your C/CPP project\n'
              '\t * [detector   ]: run beat detector for two source files')
        exit(0 if '-h' in sys.argv else 'wrong usage')
    if not os.path.exists('project_configure.csv'):
        if not os.path.exists('CMakeLists.txt'):
            print("Not an CLion Project! You need make configure manually [y/n]:", end='')
            ask = input()
            if 'y' not in ask or 'Y' not in ask:
                exit(0)
            is_cpp = True if input('Is a cpp project? [y/n]:') == 'y' else False
            project_name = input('Set executable filepath:')
            default_input = input('Set default input file path:')
            source_file = 'main.c' + ('pp' if is_cpp else '')
            while not os.path.exists(source_file):
                source_file = input('Not found "%s", set compile_filename:' % source_file)
        else:
            with open("CMakeLists.txt", 'r') as f:
                content = f.read()
            project_name = re.findall('project\((.*?)\)', content)[0].split()[0]
            if '.cpp' in content or '.CPP' in content:
                is_cpp = True
            else:
                is_cpp = False
            print('Project name:%s(%s)' % (project_name, 'CPP' if is_cpp else 'C'))
            project_name = 'cmake-build-debug' + dir_char + project_name
            default_input = 'cmake-build-debug' + dir_char + 'input.txt'
            source_file = 'main.c' + ('pp' if is_cpp else '')
        print('adding project_configure')
        info = [
            ['compile_tool', 'g++ -std=c++11' if is_cpp else 'gcc -std=c11', ''],
            ['compile_filename', source_file],
            ['executable_filename', project_name],
            ['input_file', default_input],
            ['template_file', 'template' + dir_char + 'main']
        ]
        with open('project_configure.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerows(info)
        pro_root = dir_char.join(project_name.split(dir_char)[:-1])
        with open(pro_root + dir_char + 'input.txt', 'w') as f:
            f.write('edit this file to make input')
        if not os.path.exists('template'):
            os.mkdir('template')
        with open(source_file, 'r') as f:
            main_cont = f.read()
        with open('template' + dir_char + 'main', 'w') as f:
            f.write(main_cont)
    else:
        exit("You have configured your project, see project_configure to adjust your configure!")
