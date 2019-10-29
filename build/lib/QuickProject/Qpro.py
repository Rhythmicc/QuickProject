import os
import re
import sys

if sys.platform.startswith('win'):
    is_win = True
    dir_char = '\\'
else:
    is_win = False
    dir_char = '/'
work_dir = os.getcwd() + dir_char

cpp_template = """
#include <iostream>
using namespace std;

int main(int argc, char **argv) {

    return 0;    
}
"""

c_template = """
#include <stdio.h>

int main(int argc, char **argv) {

    return 0;    
}
"""


def main():
    if '-h' in sys.argv:
        print('usage:\n'
              '\t * [Qpro -init   ]: let dir be a Qpro project!\n'
              '\t * [Qpro -h      ]: help\n'
              '\t * [Qpro -update ]: update Qpro\n'
              '\t * [Qpro -c name ]: create a Qpro project\n'
              '\t * [tmpm *       ]: manage your template\n'
              '\t * [run *        ]: run your Qpro project\n'
              '\t * [detector -[p/f][p/f] ]: run beat detector for two source files')
        exit(0)
    elif '-update' in sys.argv:
        os.system('pip3 install Qpro --upgrade')
        exit(0)
    elif '-c' in sys.argv:
        try:
            project_name = sys.argv[sys.argv.index('-c')+1]
        except IndexError:
            exit('usage: Qpro -c project')
        else:
            os.mkdir(project_name)
            is_cpp = True if input('Is a cpp project? [y/n]:') == 'y' else False
            source_file = 'main.cpp' if is_cpp else 'main.c'
            with open(project_name+dir_char+source_file, 'w') as f:
                f.write(cpp_template if is_cpp else c_template)
            os.mkdir(project_name+dir_char+'dist')
            os.mkdir(project_name+dir_char+'template')
            info = [
                ['compile_tool', 'g++ -std=c++11' if is_cpp else 'gcc -std=c11', ''],
                ['compile_filename', source_file],
                ['executable_filename', 'dist'+dir_char+project_name],
                ['input_file', 'dist'+dir_char+'input.txt'],
                ['template_root', 'template' + dir_char]
            ]
            with open(project_name+dir_char+'project_configure.csv', 'w') as f:
                for row in info:
                    f.write(','.join(row) + '\n')
            with open(project_name+dir_char+info[3][-1], 'w') as f:
                f.write('edit this file to make input')
            with open(project_name+dir_char+info[1][-1], 'r') as f:
                main_cont = f.read()
            with open(project_name+dir_char+'template' + dir_char + 'main', 'w') as f:
                f.write(main_cont)
    elif '-init' not in sys.argv:
        exit('wrong usage! Run "Qpro -h" for help!')
    elif not os.path.exists('project_configure.csv'):
        if not os.path.exists('CMakeLists.txt'):
            ask = input('Not an CLion Project!' + 'You need make configure manually [y/n]:')
            if 'y' not in ask and 'Y' not in ask:
                exit(0)
            is_cpp = True if input('Is a cpp project? [y/n]:') == 'y' else False
            project_name = os.path.abspath(input('Set executable file path:')).replace(work_dir, '')
            if dir_char not in project_name:
                project_name = '.' + dir_char + project_name
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
            source_file = 'main.c' + ('pp' if is_cpp else '')
        pro_root = dir_char.join(project_name.split(dir_char)[:-1])
        default_input = pro_root + dir_char + 'input.txt'
        print('adding project_configure')
        info = [
            ['compile_tool', 'g++ -std=c++11' if is_cpp else 'gcc -std=c11', ''],
            ['compile_filename', source_file],
            ['executable_filename', project_name],
            ['input_file', default_input],
            ['template_root', 'template' + dir_char]
        ]
        with open('project_configure.csv', 'w') as f:
            for row in info:
                f.write(','.join(row) + '\n')
        with open(info[3][-1], 'w') as f:
            f.write('edit this file to make input')
        if not os.path.exists('template') or not os.path.isdir('template'):
            os.mkdir('template')
        with open(info[1][-1], 'r') as f:
            main_cont = f.read()
        with open('template' + dir_char + 'main', 'w') as f:
            f.write(main_cont)
    else:
        exit("You have configured your project, see project_configure to adjust your configure!")
