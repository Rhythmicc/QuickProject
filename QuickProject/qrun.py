import os
import sys
import pyperclip
from QuickProject import menu_output, get_config, dir_char, QproDefaultConsole, QproErrorString, rt_dir

config = get_config()
retain_arg = ['-br', '-b', '-r', '-h', '-i']
has_recog = {i: False for i in retain_arg}


def parseArgs():
    add_flag = True
    isPath = False
    programArgs, retainArgs = [], []
    for i in sys.argv[1:]:
        if not add_flag:
            add_flag = True
            if isPath:
                programArgs.append(os.path.abspath(i))
            else:
                retainArgs.append(i)
            continue
        if i in retain_arg:
            if has_recog[i]:
                programArgs.append(i)
            else:
                retainArgs.append(i)
                has_recog[i] = True
        elif i in ['-if', '-f', '--path']:
            add_flag = False
            isPath = i == '--path'
        else:
            programArgs.append(i)
    return programArgs, retainArgs


argv, qrun_argv = parseArgs()


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
    to_build = '-b' in qrun_argv or '-br' in qrun_argv
    to_run = '-r' in qrun_argv or '-b' not in qrun_argv
    filename = rt_dir + config['compile_filename']
    flag = False
    if has_recog['-h']:
        menu_output({'title': 'qrun usage\n',
                     'lines': [
                            ('-b', 'build'),
                            ('qrun [bold green][-r]', 'run'),
                            ('-br', 'build and run'),
                            ('-h', 'help'),
                            ('-i', 'use input.txt as input'),
                            ('-if [bold magenta]<file>', 'set file as input'),
                            ('-if [bold magenta]-paste', 'use Clipboard content as input'),
                            ('-f  [bold magenta]<file>', 'set file as build file'),
                            ('*', 'add parameters for program'),
                            ('--path *.*', 'add *.* as program path parameter')],
                     'prefix': 'qrun '})
        if '-h' not in argv:
            return
    if '-f' in qrun_argv:
        index = qrun_argv.index('-f')
        if index == len(qrun_argv) - 1:
            return QproDefaultConsole.print(QproErrorString, 'No file with -f')
        filename = qrun_argv[index + 1] if qrun_argv[index + 1] != '__ignore__' else config['compile_filename']
        if not os.path.exists(filename):
            return QproDefaultConsole.print(QproErrorString, f'No such file: "{filename}"')
        filename = os.path.abspath(filename)
        flag = filename != config['compile_filename']
    if '-if' in qrun_argv:
        index = qrun_argv.index('-if')
        if index == len(qrun_argv) - 1:
            QproDefaultConsole.print(QproErrorString, 'No file with -if')
        tmp_file = qrun_argv[index + 1]
        if tmp_file == '-paste':
            with open(rt_dir + config['input_file'], 'w') as file:
                file.write(pyperclip.paste())
        elif tmp_file == '__ignore__':
            pass
        else:
            __input_file__ = tmp_file
            if not os.path.exists(__input_file__):
                return QproDefaultConsole.print(QproErrorString, f'No such file: "{__input_file__}"')
            config['input_file'] = os.path.abspath(__input_file__)
    o_file = config['executable_filename']
    record_file_name = os.path.basename(filename).split('.')[0]

    os.chdir(rt_dir)

    if config['compile_tool'] and to_build:
        os.system(config['compile_tool'].replace(config['compile_filename'], filename))
    if to_run:
        run('-i' in qrun_argv or '-if' in qrun_argv, o_file)
    if config['compile_tool'] and flag:
        if config['compile_tool'].split()[0] == 'javac':
            os.remove('dist' + dir_char + record_file_name + '.class')
        else:
            os.remove(o_file)


if __name__ == '__main__':
    main()
