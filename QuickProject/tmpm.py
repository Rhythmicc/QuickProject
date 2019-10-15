#!/usr/bin/env python3
import sys
import os

if sys.platform.startswith('win'):
    dir_char = '\\'
else:
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
is_cpp = config['compile_filename'].endswith('cpp')
algorithm_name = 'main'
temp_name = 'main'


def match_algorithm():
    with open(config['compile_filename'], 'r') as file:
        import re
        try:
            content = re.findall('/// __START__(.*?)/// __END__', file.read(), re.S)[0]
        except IndexError:
            exit('No template index found! Insert "/// __START__" and "/// __END__" to your code!')
    return content.strip()


def create():
    global temp_name, algorithm_name
    indx = sys.argv.index('-c')
    try:
        temp_name = sys.argv[indx + 1] + '.md'
        algorithm_name = sys.argv[indx + 2]
    except IndexError:
        exit('usage: tmpm -c template algorithm')
    if os.path.exists(config['template_root'] + temp_name):
        if input('Template %s is already exist, would you cover it?[y/n]:' % temp_name) == 'n':
            exit(0)
    content = match_algorithm()
    with open(config['template_root'] + temp_name, 'w') as file:
        file.write('\n## %s\n\n```%s\n' % (algorithm_name, 'c++' if is_cpp else 'c'))
        file.write(content)
        file.write('\n```\n')


def append():
    global temp_name, algorithm_name
    indx = sys.argv.index('-a')
    try:
        temp_name = sys.argv[indx + 1] + '.md'
        algorithm_name = sys.argv[indx+2]
    except IndexError:
        exit('usage: tmpm -a template algorithm')
    if os.path.exists(config['template_root'] + temp_name):
        content = match_algorithm()
        with open(config['template_root'] + temp_name, 'a') as file:
            file.write('\n## %s\n\n```%s\n' % (algorithm_name, 'c++' if is_cpp else 'c'))
            file.write(content)
            file.write('\n```\n')
    else:
        sys.argv[indx] = '-c'
        create()


def join():
    global temp_name
    try:
        temp_name = sys.argv[1] + '.md'
    except IndexError:
        exit('usage: tmpm template')
    if os.path.exists(config['template_root'] + temp_name):
        with open(config['template_root'] + temp_name, 'r') as file:
            import re
            content = re.findall('##(.*?)\n.*?```.*?\n(.*?)```', file.read(), re.S)
            for i, v in enumerate(content):
                print('[%d] %s' % (i + 1, v[0].strip()), end=' ' if i + 1 % 10 else '\n')
            indx = int(input('%s选择:' % ('\n' if len(content) % 10 else ''))) - 1
            content = content[indx]
        with open(config['compile_filename'], 'r') as file:
            content = file.read().replace('/// __TEMPLATE__', content[1].strip())
        with open(config['compile_filename'], 'w') as file:
            file.write(content)
    else:
        exit('No template named: %s' % temp_name)


def h():
    print('usage:\n'
          '\t * [tmpm]: init "compile_filename" to template/main\n'
          '\t * [tmpm -h]: for help\n'
          '\t * [tmpm -a template algorithm]: add algorithm to template\n'
          '\t * [tmpm -c template algorithm]: create template and write algorithm\n'
          '\t * [tmpm template]: insert algorithm in template')


def main():
    if len(sys.argv) == 1:
        path = config['template_root']
        path += 'main'
        with open(path, 'r') as file:
            content = file.read()
        with open(config['compile_filename'], 'w') as file:
            file.write(content)
    else:
        if '-h' in sys.argv:
            h()
        elif '-c' in sys.argv:
            create()
        elif '-a' in sys.argv:
            append()
        else:
            join()


if __name__ == '__main__':
    main()
