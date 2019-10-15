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
                temp_name = sys.argv[indx+1]
            except IndexError:
                exit('usage: refresh -create template')
            ls = os.listdir(config['template_root'])
            if temp_name in ls:
                exit('已存在 %s 模板' % temp_name)
            else:
                with open(config['compile_filename'],'r') as f:
                    content = f.read()
                with open(config['template_root'] + temp_name, 'w') as f:
                    f.write(content)
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
                with open(config['template_root']+temp_name, 'r') as f:
                    content = f.read()
                with open(config['compile_filename'], 'w') as f:
                    f.write(content)
