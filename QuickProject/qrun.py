import pyperclip
from . import *

config = get_config(without_output='--qrun-commander-complete' in sys.argv or '--qrun-fig-complete' in sys.argv)
retain_arg = ['-br', '-b', '-r', '-h', '-i']
has_recog = {i: False for i in retain_arg}


def parseArgs():
    add_flag = True
    isPath = False
    programArgs, retainArgs = [], []
    conflictArgs = set()
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
                conflictArgs.add(i)
                programArgs.append(i)
            else:
                retainArgs.append(i)
                has_recog[i] = True
        elif i in ['-if', '-f', '--path']:
            add_flag = False
            isPath = i == '--path'
        else:
            programArgs.append(i)
    for i in conflictArgs:
        has_recog[i] = False
    return programArgs, retainArgs


argv, qrun_argv = parseArgs()


def run(use_txt=False, executable_file=str(config['executable_filename'])):
    if os.path.exists(executable_file):
        cmd = executable_file.replace(' ', '\ ') + ' '
    else:
        cmd = executable_file + ' '
    if '--qrun-commander-complete' in argv:
        if 'enable_complete' in config and config['enable_complete']:
            os.system(cmd + ' '.join(argv))
        else:
            print()
        return
    if '--qrun-fig-complete' in argv:
        if 'enable_complete' in config and config['enable_complete']:
            os.system(cmd + ' --qrun-fig-complete')
        else:
            print()
        return
    if argv:
        cmd += ' '.join(argv)
    if '--qrun-commander-complete' in argv and not config['enable_complete']:
        return print()
    if cmd.strip():
        cmd += (' < "' + config['input_file'] + '"' if use_txt else '')
        os.system(cmd)


def main():
    to_build = '-b' in qrun_argv or '-br' in qrun_argv
    to_run = '-r' in qrun_argv or '-b' not in qrun_argv
    filename = rt_dir + config['compile_filename'] if config['compile_filename'] else ''
    flag = False
    if has_recog['-h']:
        menu_output({'title': 'qrun usage\n',
                     'lines': [
                            ('-b', 'build' if user_lang != 'zh' else '编译'),
                            ('qrun [bold green][-r]', 'run' if user_lang != 'zh' else '运行'),
                            ('-br', 'build and run' if user_lang != 'zh' else '编译且运行'),
                            ('-h', 'help' if user_lang != 'zh' else '帮助'),
                            ('-i', 'use input.txt as input' if user_lang != 'zh' else '使用默认输入文件作为输入'),
                            ('-if [bold magenta]<file>', 'set file as input' if user_lang != 'zh' else '输入重定向'),
                            ('-if [bold magenta]-paste', 'use Clipboard content as input' if user_lang != 'zh' else '输入重定向到粘贴板'),
                            ('-f  [bold magenta]<file>', 'set file as build file' if user_lang != 'zh' else '指定源文件'),
                            ('*', 'add parameters for program' if user_lang != 'zh' else '程序的任何其他参数')],
                     'prefix': 'qrun '})
        if '-h' not in argv:
            return
    if '-f' in qrun_argv:
        index = qrun_argv.index('-f')
        if index == len(qrun_argv) - 1:
            return QproDefaultConsole.print(QproErrorString, 'No file with -f' if user_lang != 'zh' else '-f后没有指定文件')
        filename = qrun_argv[index + 1] if qrun_argv[index + 1] != '__ignore__' else config['compile_filename']
        if not os.path.exists(filename):
            return QproDefaultConsole.print(
                QproErrorString, (
                    'No such file: "{filename}"' if user_lang != 'zh' else '没有这个文件: "{filename}"'
                ).format(filename=filename)
            )
        filename = os.path.abspath(filename)
        flag = filename != config['compile_filename']
    if '-if' in qrun_argv:
        index = qrun_argv.index('-if')
        if index == len(qrun_argv) - 1:
            QproDefaultConsole.print(QproErrorString, 'No file with -if' if user_lang != 'zh' else '-if后没有指定文件')
        tmp_file = qrun_argv[index + 1]
        if tmp_file == '-paste':
            with open(rt_dir + config['input_file'], 'w') as file:
                file.write(pyperclip.paste())
        elif tmp_file == '__ignore__':
            pass
        else:
            __input_file__ = tmp_file
            if not os.path.exists(__input_file__):
                return QproDefaultConsole.print(
                    QproErrorString, (
                        'No such file: "{input_file}"' if user_lang != 'zh' else '没有这个文件: "{input_file}"'
                    ).format(input_file=__input_file__)
                )
            config['input_file'] = os.path.abspath(__input_file__)
    o_file = config['executable_filename']
    record_file_name = os.path.basename(filename).split('.')[0]

    os.chdir(rt_dir)

    if config['compile_tool'] and to_build:
        cmd = config['compile_tool']
        if filename and config['compile_filename']:
            cmd = cmd.replace(config['compile_filename'], filename)
        os.system(cmd)
    if to_run:
        run('-i' in qrun_argv or '-if' in qrun_argv, o_file)
    if config['compile_tool'] and flag:
        if config['compile_tool'].split()[0] == 'javac':
            os.remove('dist' + dir_char + record_file_name + '.class')
        else:
            os.remove(o_file)


if __name__ == '__main__':
    main()
