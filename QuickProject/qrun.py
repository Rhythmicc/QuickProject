import os
import sys
import pyperclip
from QuickProject import menu_output, get_config, dir_char, QproDefaultConsole, QproErrorString

config = get_config()
argv = []
retain_arg = ['-br', '-b', '-r', '-h', '-i']
has_recog = {i: False for i in retain_arg}


def run(use_txt=False, executable_file=str(config['executable_filename'])):
    if os.path.exists(executable_file):
        cmd = executable_file.replace(' ', '\ ') + ' '
    else:
        cmd = executable_file + ' '
    if argv:
        cmd += ' '.join(argv)
    if cmd.strip():
        cmd += (' < "' + config['input_file'] + '"' if use_txt else '')
        os.system(cmd)


def main():
    to_build = '-b' in sys.argv or '-br' in sys.argv
    to_run = '-r' in sys.argv or '-b' not in sys.argv
    filename = config['compile_filename']
    flag = False
    if '-debug' in sys.argv:
        raise ImportError
    if '-h' in sys.argv:
        return menu_output({'title': 'qrun usage\n',
                            'lines': [
                                ('-b', 'build'),
                                ('qrun [bold green][-r]', 'run'),
                                ('-br', 'build and run'),
                                ('-h', 'help'),
                                ('-i', 'use input.txt as input'),
                                ('-if [bold magenta]<file>', 'set file as input'),
                                ('-if [bold magenta]-paste', 'use Clipboard content as input'),
                                ('-f  [bold magenta]<file>', 'set file as build file'),
                                ('*', 'add parameters for program')],
                            'prefix': 'qrun '})
    if '-f' in sys.argv:
        index = sys.argv.index('-f')
        if index == len(sys.argv) - 1:
            return QproDefaultConsole.print(QproErrorString, 'No file with -f')
        filename = sys.argv[index + 1]
        if not os.path.exists(filename):
            return QproDefaultConsole.print(QproErrorString, f'No such file: {filename}')
        flag = True
    if '-if' in sys.argv:
        index = sys.argv.index('-if')
        if index == len(sys.argv) - 1:
            QproDefaultConsole.print(QproErrorString, 'No file with -if')
        tmp_file = sys.argv[index + 1]
        if tmp_file == '-paste':
            with open('cmake-build-debug' + dir_char + 'input.txt', 'w') as file:
                file.write(pyperclip.paste())
        else:
            __input_file__ = tmp_file
            if not os.path.exists(__input_file__):
                return QproDefaultConsole.print(QproErrorString, f'No such file: {__input_file__}')
            config['input_file'] = __input_file__
    o_file = config['executable_filename']
    record_file_name = os.path.basename(filename).split('.')[0]
    if config['compile_tool'] and to_build:
        os.system(config['compile_tool'].replace(config['compile_filename'], filename))
    if to_run:
        add_flag = True
        for i in sys.argv[1:]:
            if not add_flag:
                add_flag = True
                continue
            if i in retain_arg:
                if has_recog[i]:
                    argv.append(i)
                else:
                    has_recog[i] = True
            elif i in ['-if', '-f']:
                add_flag = False
            else:
                argv.append(i)
        run('-i' in sys.argv or '-if' in sys.argv, o_file)
    if config['compile_tool'] and flag:
        if config['compile_tool'].split()[0] == 'javac':
            os.remove('dist' + dir_char + record_file_name + '.class')
        else:
            os.remove(o_file)


if __name__ == '__main__':
    main()
