#!/usr/bin/env python3
import sys
import csv

if sys.platform.startswith('win'):
    dir_char = '\\'
else:
    dir_char = '/'


def main():
    config = {}
    try:
        with open('project_configure.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                config[row[0]] = row[1:]
            for i in config:
                if i != 'compile_tool':
                    config[i] = config[i][0]
    except IOError:
        exit("No file named: project_configure.csv\n May you need run:\"Qpro -init\" first!")
    with open(config['template_file'], 'r') as f:
        content = f.read()
    with open(config['compile_filename'], 'w') as f:
        f.write(content)
