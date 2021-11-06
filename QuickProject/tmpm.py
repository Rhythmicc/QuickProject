import sys
import os
from QuickProject import *

config = get_config()
is_cpp = config['compile_filename'].endswith('cpp')
algorithm_name = 'main'
temp_name = 'main'


def match_algorithm():
    with open(config['compile_filename'], 'r') as file:
        import re
        try:
            content = re.findall('__TMPM_START__(.*?)__TMPM_END__', file.read(), re.S)[0].strip()
        except IndexError:
            return QproDefaultConsole.print(
                QproErrorString,
                'No template index found! Insert "__TMPM_START__" and "__TMPM_END__" to your code!'
                if user_lang != 'zh' else
                '没有找到模板桩! 请插入"__TMPM_START__" 和 "__TMPM_END__"到默认源文件中!'
            )
    content = content.replace('__TMPM__', '')
    return content


def write_algorithm(temp, algorithm, content, mode):
    with open(config['template_root'] + temp, mode) as file:
        file.write('\n## %s\n\n```%s\n' % (algorithm, 'c++' if is_cpp else 'c'))
        file.write(content)
        file.write('\n```\n')


def create():
    global temp_name, algorithm_name
    indx = sys.argv.index('-c')
    try:
        temp_name = sys.argv[indx + 1]
        algorithm_name = sys.argv[indx + 2]
    except IndexError:
        if temp_name != 'main':
            with open(config['compile_filename'], 'r') as file:
                ct = file.read()
            with open(config['template_root'] + temp_name, 'w') as file:
                file.write(ct)
            return
        else:
            return QproDefaultConsole.print(
                QproWarnString,
                'usage: tmpm -c <template> [algorithm]'
                if user_lang != 'zh' else
                '使用: tmpm -c <模板> [算法]'
            )
    temp_name += '.md'
    if os.path.exists(config['template_root'] + temp_name):
        from rich.prompt import Prompt
        if Prompt.ask((
            'Template {temp_name} is already exist, would you cover it?[y/n]'
            if user_lang != 'zh' else
            '模板 {temp_name} 已经存在, 是否覆盖它?[y/n]'
        ).format(temp_name=temp_name), default='n') == 'n':
            exit(0)
    content = match_algorithm()
    write_algorithm(temp_name, algorithm_name, content, 'w')


def append():
    global temp_name, algorithm_name
    indx = sys.argv.index('-a')
    try:
        temp_name = sys.argv[indx + 1] + '.md'
        algorithm_name = sys.argv[indx + 2]
    except IndexError:
        return QproDefaultConsole.print(
            QproWarnString,
            'usage: tmpm -a <template> [algorithm]'
            if user_lang != 'zh' else
            '使用: tmpm -a <模板> [算法]'
        )
    if os.path.exists(config['template_root'] + temp_name):
        content = match_algorithm()
        write_algorithm(temp_name, algorithm_name, content, 'a')
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
            from rich.prompt import Prompt

            content = re.findall('##(.*?)\n.*?```.*?\n(.*?)```', file.read(), re.S)
            for i, v in enumerate(content):
                QproDefaultConsole.print('[%d] %s' % (i + 1, v[0].strip()), end=' ' if i + 1 % 10 else '\n')
            indx = int(Prompt.ask(('%sChoose' if user_lang != 'zh' else '%s选择') % ('\n' if len(content) % 10 else ''))) - 1
            content = content[indx]
        with open(config['compile_filename'], 'r') as file:
            content = file.read().replace('__TMPM__', content[1].strip())
        with open(config['compile_filename'], 'w') as file:
            file.write(content)
    else:
        return QproDefaultConsole.print(
            QproErrorString, (
                'No template named: {temp_name}'
                if user_lang != 'zh' else
                '没有模板: {temp_name}'
            ).format(temp_name=temp_name)
        )


def h():
    menu_output({'title': 'tmpm usage\n' if user_lang != 'zh' else '模板管理器菜单\n',
                 'lines': [
                     ('-h', 'for help' if user_lang != 'zh' else '帮助'),
                     ('-i', 'init content as template/main' if user_lang != 'zh' else '恢复源文件内容为template/main'),
                     ('-r', 'select copy and init' if user_lang != 'zh' else '选择备份然后恢复'),
                     (
                         '-r [bold magenta]<backup>',
                         'revert "compile_filename" from template/<backup>'
                         if user_lang != 'zh' else '恢复源文件内容为template/<backup>'
                     ),
                     (
                         '-c [bold magenta]<backup>',
                         'create or cover a <backup> of "compile_filename"' if user_lang != 'zh' else '创建或覆盖备份'
                     ),
                     (
                         '-c [bold magenta]<template> [bold magenta]<algorithm>',
                         'create template and write algorithm' if user_lang != 'zh' else '创建模板然后写入算法'
                     ),
                     (
                         '-a [bold magenta]<template> [bold magenta]<algorithm>',
                         'add algorithm to template' if user_lang != 'zh' else '添加算法到模板'
                     ),
                     (
                         'tmpm    [bold magenta]<template>',
                         'insert algorithm in <template>' if user_lang != 'zh' else '在模板桩插入模板库中的算法'
                     )],
                 'prefix': 'tmpm'})


def init(file_name: str = 'main'):
    with open(str(config['template_root']) + file_name, 'r') as file:
        content = file.read()
    with open(config['compile_filename'], 'w') as file:
        file.write(content)


def revert():
    indx = sys.argv.index('-r')
    try:
        file_name = sys.argv[indx + 1]
    except IndexError:
        from rich.prompt import Prompt

        ls = os.listdir(config['template_root'])
        rls = []
        cnt = 1
        stdSuffix = config['compile_filename'].strip().split('.')[-1]
        for i in ls:
            iSuffix = i.split('.')[-1]
            if iSuffix != stdSuffix and '.' in i:
                continue
            QproDefaultConsole.print('[%d] %s' % (cnt, i), end='\t' if cnt % 8 else '\n')
            rls.append(i)
            cnt += 1
        if cnt % 8:
            QproDefaultConsole.print()
        try:
            indx = int(Prompt.ask('选择' if user_lang == 'zh' else 'Choose'))
            if indx < 0 or indx > len(rls):
                raise IndexError
        except:
            return QproDefaultConsole.print(QproErrorString, 'Choose out of index' if user_lang == 'zh' else '选择')
        file_name = rls[indx - 1]
        return init(file_name)
    if os.path.exists(config['template_root'] + file_name):
        init(file_name)
    else:
        return QproDefaultConsole.print(QproErrorString, 'No such backup' if user_lang != 'zh' else '没有这个备份')


def complete():
    if rt_dir == os.path.abspath('.') + dir_char and not os.path.exists(project_configure_path):
        return print()
    print(' '.join(os.listdir(rt_dir + config['template_root'])))


def main():
    os.chdir(rt_dir)

    if len(sys.argv) == 1:
        h()
    elif '-h' in sys.argv:
        h()
    elif '-c' in sys.argv:
        create()
    elif '-a' in sys.argv:
        append()
    elif '-r' in sys.argv:
        revert()
    elif '-i' in sys.argv:
        init()
    elif '-complete' in sys.argv:
        complete()
    else:
        join()


if __name__ == '__main__':
    main()
