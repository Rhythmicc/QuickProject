import os
import re
import sys

base_dir = sys.path[0]
if sys.platform.startswith('win'):
    dir_char = '\\'
else:
    dir_char = '/'
base_dir += dir_char


def main():
    if not os.path.exists('CMakeLists.txt'):
        exit("Not an CLion Project!")
    with open("CMakeLists.txt", 'r') as f:
        content = f.read()
    project_name = re.findall('project\((.*?)\)', content)[0]
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
        if os.path.exists(base_dir + script):
            with open(base_dir + script, 'r') as f:
                content = f.read()
            if script == 'run':
                content = content.replace('__COMPILE_TOOL__', 'g++ -std=c++11' if is_cpp else 'gcc -std=c11')
                content = content.replace('__COMPILE_FILENAME__', 'main.cpp' if is_cpp else 'main.c')
                content = content.replace('__PROJECT_NAME__', project_name)
                with open('cmake-build-debug' + dir_char + 'input.txt', 'w') as f:
                    f.write('edit this file to make input')
                with open('run.py', 'w') as f:
                    f.write(content)
            elif script == 'refresh':
                os.mkdir('template')
                with open('main.cpp' if is_cpp else 'main.c', 'r')as f:
                    main_cont = f.read()
                with open('template' + dir_char + 'main', 'w') as f:
                    f.write(main_cont)
                with open('refresh.py', 'w') as f:
                    f.write(content)
            else:
                with open(script + '.py', 'w') as f:
                    f.write(content)
