#!/usr/bin/env python3
import sys
import os

if sys.platform.startswith('win'):
    dir_char = '\\'
else:
    dir_char = '/'


def main():
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
    if len(sys.argv) == 1:
        with open(config['template_root'] + 'main', 'r') as f:
            content = f.read()
        with open(config['compile_filename'], 'w') as f:
            f.write(content)
    else:
        if '-c' in sys.argv:
            indx = sys.argv.index('-create')
            temp_name = 'main'
            try:
                temp_name = sys.argv[indx + 1]
            except IndexError:
                exit('usage: refresh -create template')
            ls = [i.split('.')[0] for i in os.listdir(config['template_root'])]
            if temp_name in ls:
                exit('已存在 %s 模板' % temp_name)
            else:
                with open(config['compile_filename'], 'r') as f:
                    content = f.read()
                with open(config['template_root'] + temp_name + '.md', 'w') as f:
                    f.write(
                        '# %s\n ```%s\n' % (temp_name, 'c++' if is_cpp else 'c'))
                    f.write(content)
                    f.write('\n```')
        else:
            temp_name = sys.argv[1]
            ls = os.listdir(config['template_root'])
            rls = []
            for i in ls:
                if i.startswith(temp_name):
                    rls.append(i)
            if len(rls) > 1:
                print('存在多个模板:')
                for i in rls:
                    print(i)
                exit(-1)
            else:
                if rls[0].split('.')[0] != temp_name:
                    if input('Mathc template: %s. Are you sure to join it?[y/n]:') == 'n':
                        exit(0)
                print('get %s' % config['template_root'] + rls[0])
                with open(config['template_root'] + rls[0], 'r') as f:
                    content = f.read()
                    import re
                    if is_cpp:
                        content = re.findall('```c\+\+(.*?)```', content, re.S)[0]
                    else:
                        content = re.findall('```c(.*?)```', content, re.S)[0]
                with open(config['compile_filename'], 'r') as f:
                    content = f.read().replace('/// __TEMPLATE__', content)
                with open(config['compile_filename'], 'w') as f:
                    f.write(content)


if __name__ == '__main__':
    main()
