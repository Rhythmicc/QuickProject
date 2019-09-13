#!/usr/bin/env python3
import sys

base_dir = sys.path[0]
if sys.platform.startswith('win'):
    dir_char = '\\'
else:
    dir_char = '/'
base_dir += dir_char

if __name__ == '__main__':
    with open(base_dir + 'template/main', 'r') as f:
        content = f.read()
    with open(base_dir + 'main.cpp', 'w') as f:
        f.write(content)
