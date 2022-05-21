from . import *
from . import _ask
from QuickProject import __sub_path, _choose_server_target
from rich.prompt import Prompt


def __format_json(info, path: str):
    """
    回写配置表

    :param info: 列表格式或字典格式
    :param path: 路径
    :return:
    """
    import json
    with open(path, 'w') as f:
        if isinstance(info, list):
            config = {}
            for line in info:
                config[line[0]] = line[1] if line[0] != 'server_targets' else line[1:]
            json.dump(config, f, indent=1)
        elif isinstance(info, dict):
            json.dump(info, f, indent=1)


def __findAndReplace(dirPath, fo, to):
    """
    替换模板项目中的指定字段

    :param dirPath: 项目路径
    :param fo: 识别
    :param to: 替换
    :return:
    """
    for rt, son_dir, son_files in os.walk(dirPath):
        for file in son_files:
            with open(rt + dir_char + file, 'r') as f:
                ct = f.read()
            with open(rt + dir_char + file, 'w') as f:
                f.write(ct.replace(fo, to))


def remove(path):
    """
    删除文件或目录

    :param path: 路径
    :return:
    """
    import shutil
    if os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)


def scp_init(server_targets: list):
    if not server_targets:
        return
    for server_target in server_targets:
        user, host, port, target = server_target['user'], server_target['host'], server_target['port'], server_target['path']
        st = SshProtocol.post_all_in_folder(user, host, target, port, '')
        if st:
            QproDefaultConsole.print(QproErrorString, "upload project failed!" if user_lang != 'zh' else '上传项目失败!')


def _create_empty_project(project_name):
    if os.path.exists(project_name):
        return QproDefaultConsole.print(
            QproErrorString,
            f'{project_name} already exists!' if user_lang != 'zh' else f'{project_name} 已存在'
        )
    os.mkdir(project_name)
    __format_json([
        ['compile_tool', ''],
        ['compile_filename', ''],
        ['executable_filename', ''],
        ['input_file', ''],
        ['template_root', ''],
        ['server_target', '', '']
    ], project_name + dir_char + configure_name)
    os.chdir(project_name)
    return


def _search_supported_languages(is_CN):
    kw = _ask({
        'type': 'input',
        'message': 'Input a keyword' if user_lang != 'zh' else '输入一个关键词',
        'name': 'language'
    })

    import json
    import requests

    try:
        res = json.loads(requests.get(f'https://qpro.rhythmlian.cn/?keyword={kw}&is_CN={str(is_CN).lower()}').text)
        if not res['status']:
            QproDefaultConsole.print(QproErrorString, res['message'])
            return None
        data = {i[0]: i[1:] for i in res['data']}
        return data[
            _ask({
                'type': 'list',
                'message': 'Choose Supported Language' if user_lang != 'zh' else '选择支持的语言',
                'name': 'url',
                'choices': list(data.keys())
            })
        ]
    except Exception as e:
        QproDefaultConsole.print(QproErrorString, repr(e))
    return None


def _external_create(project_name: str, key: str = ''):
    from git import Repo

    if key:
        if key in ['Empty', '空白项目']:
            return _create_empty_project(project_name)

        try:
            from QuickStart_Rhy.API.alapi import ip_info
            with QproDefaultConsole.status(
                    ('Check IP to switch mirrors' if user_lang != 'zh' else '检查IP以选择合适的镜像').format(key, project_name)):
                is_CN = ip_info('')['ad_info']['nation'].startswith('中国')
        except:
            is_CN = False

        templateProjectUrls = _search_supported_languages(is_CN)
        if not templateProjectUrls:
            exit(0)
        with QproDefaultConsole.status(
                ('Cloning Qpro {} Template to {}' if user_lang != 'zh' else '正在克隆Qpro {} 模板为 {}').format(key,
                                                                                                         project_name)):
            Repo.clone_from(templateProjectUrls[0], project_name)
    else:
        templateProjectUrls = _ask({
            'type': 'input',
            'message': 'GIT ' + ('URL' if user_lang != 'zh' else '链接') + ':',
            'name': 'url'
        })
        with QproDefaultConsole.status(
                ('Cloning External Template to {}' if user_lang != 'zh' else '正在克隆Qpro 外部模板为 {}').format(project_name)):
            Repo.clone_from(templateProjectUrls, project_name)
    os.chdir(project_name)
    try:
        remove('.git')
    except Exception as e:
        QproDefaultConsole.print(QproErrorString, repr(e))
    if key:
        __findAndReplace(os.getcwd(), templateProjectUrls[1], project_name)


def __get_server_target_from_string():
    """
    从字符串中获取服务器目标
    """
    server_target = _ask({
        'type': 'input',
        'name': 'server_target',
        'message': 'Input user@ip:dir_path if you need scp' if user_lang != 'zh' else '输入 用户@IP:路径 如果你打算使用SSH'
    }).strip().replace(dir_char, '/')

    if server_target and not server_target.endswith('/'):
        if not server_target.endswith(':'):
            server_target += '/'
        else:
            server_target += '~/'
    user, host, path, port = '', '', '', 22
    if server_target:
        user, target = server_target.split('@')
        target = target.split(':')
        host = ':'.join(target[:-1])
        path = target[-1] + ('' if target[-1].endswith('/') else '/')
        port = _ask({
            'type': 'input',
            'name': 'port',
            'message': 'input port' if user_lang != 'zh' else '输入端口号',
            'default': '22'
        })
    return {
        'user': user,
        'host': host,
        'port': port,
        'path': path
    }


def create():
    try:
        project_name = sys.argv[2]
    except IndexError:
        return QproDefaultConsole.print(QproWarnString,
                                        'usage: Qpro create <project>' if user_lang != 'zh' else '使用: Qpro create <项目>')
    else:
        if os.path.exists(project_name) and os.path.isdir(project_name):
            return QproDefaultConsole.print(QproErrorString, '"%s" is exist!' % (os.path.abspath(project_name)))

        lang = _ask({
            'type': 'list',
            'name': 'lang_name',
            'message': 'Choose Lang | 选择语言:',
            'choices': [
                'Empty' if user_lang != 'zh' else '空白项目',
                'Template' if user_lang != 'zh' else '内置模板',
                'External' if user_lang != 'zh' else '外部项目'
            ]
        })

        if lang in ['external', '外部项目']:
            _external_create(project_name)
        else:
            _external_create(project_name, lang)

        config = get_config()
        config['server_targets'] = [__get_server_target_from_string()]
        __format_json(config, configure_name)

        if _ask({
            'type': 'confirm',
            'message': 'Open it with VS Code?' if user_lang != 'zh' else '是否现在使用VS Code打开?',
            'name': 'open',
            'default': True
        }):
            if sys.platform == 'darwin':
                os.system(f'open -a "Visual Studio Code" .')
            else:
                os.system('code .')


def scp(smv_flag: bool = False):
    kw = 'scp' if not smv_flag else 'smv'
    try:
        path = sys.argv[2]
        sub_path = __sub_path(path)
    except IndexError:
        return QproDefaultConsole.print(
            QproWarnString, f'usage: Qpro {kw} <path>' if user_lang != 'zh' else f'使用: Qpro {kw} <路径>'
        )
    else:
        if not sub_path:
            return \
                QproDefaultConsole.print(
                    QproErrorString,
                    (f"{path} is not in this Qpro project!" if os.path.exists(path) else f'No such file named: {path}')
                    if user_lang != 'zh' else
                    (f"{path} 不在当前 Qpro 项目中!" if os.path.exists(path) else f'该路径不存在: {path}')
                )
        server_targets = get_server_targets()
        status = 0
        for server_target in server_targets:
            if os.path.isdir(path):
                status |= SshProtocol.post_folder(server_target['user'], server_target['host'], server_target['path'], server_target['port'], path, sub_path)
            else:
                status |= SshProtocol.post_file(server_target['user'], server_target['host'], server_target['path'], server_target['port'], path, sub_path)
        if smv_flag and not status:
            remove(path)


def smv():
    if _ask({
        'type': 'confirm',
        'message': 'Confirm delete after transform | 确认传输后删除',
        'default': True,
        'name': 'confirm'
    }):
        scp(True)


def get():
    try:
        path = sys.argv[2]
        sub_path = __sub_path(path, isExist=False)
    except IndexError:
        return QproDefaultConsole.print(
            QproWarnString, 'usage: Qpro get <path>' if user_lang != 'zh' else '使用: Qpro get <路径>'
        )
    else:
        if not sub_path:
            return QproDefaultConsole.print(QproErrorString,
                                            f"{path} is not in this Qpro project!" if user_lang != 'zh' else f'{path} 不在当前 Qpro 项目中!')
        server_target = get_server_targets()[0]
        SshProtocol.get_file_or_folder(server_target['user'], server_target['host'], server_target['port'], server_target['path'], sub_path, path)


def pro_init():
    work_project = ''
    while not work_project:
        work_project = Prompt.ask('You need to set project name' if user_lang != 'zh' else '请设置项目名').strip()
    lang_tool_exe = {
        'c': ['gcc -std=c11 --source_file-- -o --execute--', '', '.c'],
        'cpp': ['g++ -std=c++11 --source_file-- -o --execute--', '', '.cpp'],
        'java': ['javac -d dist --source_file--', 'java -classpath dist ', '.java'],
        'python3': ['', 'python3 ', '.py'],
        'python': ['', 'python ', '.py'],
        'empty | other': ['', '', '']
    }

    lang_name = _ask({
        'type': 'list',
        'name': 'lang_name',
        'message': 'Choose Lang | 选择语言:',
        'choices': lang_tool_exe.keys()
    })

    lang = lang_tool_exe[lang_name]
    source_file = ''
    if lang_name != 'empty | other':
        source_file = ('main' + lang[-1]) if lang[0] != 'javac' else work_project + lang[-1]
        while not os.path.exists(source_file):
            source_file = Prompt.ask((
                                         'Not found "%s", set compile_filename'
                                         if user_lang != 'zh' else
                                         '没有找到 "%s", 请设置源文件'
                                     ) % source_file).strip()
    if lang[0] != 'javac':
        execute = lang[1] + 'dist' + dir_char + work_project if lang[0] else lang[1] + source_file
    elif lang_name != 'empty | other':
        work_project = source_file.split(dir_char)[-1].split('.')[0]
        execute = lang[1] + work_project
    else:
        execute = ''
    if (not os.path.exists('dist') or not os.path.isdir('dist')) and lang_name != 'empty | other':
        os.mkdir('dist')
    info = [
        ['compile_tool', lang[0].replace('--source_file--', source_file).replace('--execute--', execute)],
        ['compile_filename', source_file],
        ['executable_filename', execute],
        ['input_file', 'dist' + dir_char + 'input.txt' if lang_name != 'empty' else ''],
        ['template_root', 'template' + dir_char if lang_name != 'empty' else ''],
        ['server_targets', __get_server_target_from_string()],
    ]
    __format_json(info, configure_name)
    if lang_name and lang_name == 'empty | other':
        if _ask({
            'type': 'confirm',
            'message': 'Confirm to sync project | 确认同步项目',
            'default': True,
            'name': 'confirm'
        }):
            scp_init(info[-1][1:])
        return
    with open(info[3][-1], 'w') as f:
        f.write('edit this file to make input' if user_lang != 'zh' else '编辑此文件作为程序输入')
    if not os.path.exists('template') or not os.path.isdir('template'):
        os.mkdir('template')
    try:
        with open(info[1][-1], 'r') as f:
            main_cont = f.read()
        with open('template' + dir_char + 'main', 'w') as f:
            f.write(main_cont)
    except Exception as e:
        QproDefaultConsole.print(
            QproErrorString, "make backup failed with error: %s, you need backup code by yourself!" % e)
    if _ask({
        'type': 'confirm',
        'message': 'Confirm to sync project | 确认同步项目',
        'default': True,
        'name': 'confirm'
    }):
        scp_init(info[-1][1:])


def ssh():
    server_target = _choose_server_target()
    if not server_target:
        return
    SshProtocol.ssh(server_target['user'], server_target['host'], server_target['path'], server_target['port'], __sub_path('.'))


def delete_all():
    server_targets = get_server_targets()
    st = 0
    for server_target in server_targets:
        _st = SshProtocol.command(server_target['user'], server_target['host'], server_target['path'], server_target['port'], 'rm -rf .')
        st |= 1 if _st else 0
        QproDefaultConsole.print(QproErrorString, f'{server_target}: delete all failed with error: {st}')
    if not st:
        remove(os.getcwd())


def delete():
    try:
        path = os.path.abspath(sys.argv[2])
        sub_path = __sub_path(path)
    except IndexError:
        return QproDefaultConsole.print(
            QproWarnString, 'usage: Qpro del <path>' if user_lang != 'zh' else '使用: Qpro del <路径>'
        )
    else:
        if not sub_path:
            return \
                QproDefaultConsole.print(
                    QproErrorString,
                    (f"{path} is not in this Qpro project!" if os.path.exists(path) else f'No such file named: {path}')
                    if user_lang != 'zh' else
                    (f"{path} 不在当前 Qpro 项目中!" if os.path.exists(path) else f'该路径不存在: {path}')
                )
        server_targets = get_server_targets()
        st = 0
        for server_target in server_targets:
            _st = SshProtocol.command(server_target['user'], server_target['host'], server_target['path'],
                                      server_target['port'], f'rm -rf {sub_path}')
            st |= 1 if _st else 0
            if _st:
                QproDefaultConsole.print(QproErrorString, f'{server_target}: delete {sub_path} failed with error: {_st}')
        if not st or _ask({
            'type': 'confirm',
            'name': 'confirm',
            'message': f'{path} is not in this Qpro project! Do you want to delete it?' if user_lang != 'zh' else f'{path} 不在当前 Qpro 项目中! 是否删除?',
        }):
            remove(sub_path)


def tele_ls():
    try:
        path = sys.argv[2]
        sub_path = __sub_path(path, False)
    except IndexError:
        sub_path = __sub_path('./', False)
    server_target = _choose_server_target()
    if server_target:
        from . import SshProtocol
        res = SshProtocol.command(server_target['user'], server_target['host'], server_target['path'], server_target['port'], f'ls -lah {sub_path}').strip().split('\n')[3:]
        res = [i.strip().split() for i in res]

        from rich.table import Table
        from rich.box import SIMPLE_HEAVY
        from rich.color import Color
        from rich.text import Text
        from rich.style import Style

        table = Table(title=f'{sub_path}', box=SIMPLE_HEAVY, show_header=True, header_style='bold magenta')
        table.add_column('permission' if user_lang != 'zh' else '权限码', justify='center')
        table.add_column('size' if user_lang != 'zh' else '尺寸', justify='center')
        table.add_column('owner' if user_lang != 'zh' else '拥有者', justify='center')
        table.add_column('time' if user_lang != 'zh' else '修改时间', justify='center')
        table.add_column('name' if user_lang != 'zh' else '文件名', justify='right')
        for i in res:
            is_dir = True if i[0][0] == 'd' else False
            color = Color.from_rgb(112, 87, 250) if is_dir else None
            p_color = Color.from_rgb(171, 157, 242)
            permission = ''.join(['1' if j != '-' else '0' for j in i[0][1:]])
            permission = '%d%d%d' % (int(permission[:3], 2), int(permission[3: 6], 2), int(permission[6:], 2))
            table.add_row(*[Text(permission, style=Style(color=p_color)), f'[green]{i[4]}', '[bold yellow]' + i[2], '[blue]' +  ' '.join(i[5:8]), Text(" ".join(i[8:]), style=Style(color=color, bold=is_dir))])
        QproDefaultConsole.print(table, justify='center')


def template_format():
    config = {}
    with open('project_configure.csv', 'r') as f:
        for row in f.read().strip().split('\n'):
            row = row.replace('\,', '--QPRO-IS-SPLIT--')
            row = [i.replace('--QPRO-IS-SPLIT--', ',') for i in row.split(',')]
            config[row[0]] = [i.strip() for i in row[1:]]
        for i in config:
            if i in ['server_target']:
                continue
            config[i] = config[i][0]
    __format_json(config, 'project_configure.json')
    remove('project_configure.csv')


def enable_complete():
    config = get_config()
    config['enable_complete'] = True
    __format_json(config, project_configure_path)


def __get_Qpro_fig_Dir():
    QproGlobalDir = os.environ.get('QproGlobalDir', None)
    if not QproGlobalDir:
        QproDefaultConsole.print(QproErrorString,
                                 'QproGlobalDir is not set!' if user_lang != 'zh' else 'QproGlobalDir 未设置!')
        return None
    QproGlobalDir = QproGlobalDir.replace('~', user_root)
    if not os.path.exists(QproGlobalDir):
        QproDefaultConsole.print(QproErrorString,
                                 'QproGlobalDir is not exists!' if user_lang != 'zh' else 'QproGlobalDir 不存在!')
        return None
    if not os.path.exists(os.path.join(QproGlobalDir, 'bin')):
        os.mkdir(os.path.join(QproGlobalDir, 'bin'))
    if not os.path.exists(os.path.join(QproGlobalDir, 'fig')):
        os.mkdir(os.path.join(QproGlobalDir, 'fig'))
    return QproGlobalDir


def register_global_command():
    if not os.path.exists(configure_name):
        return QproDefaultConsole.print(QproErrorString, f'{configure_name} is not exists!' if user_lang != 'zh' else f'{configure_name} 不存在!')
    if is_win:
        return QproDefaultConsole.print(QproWarnString, 'Not Support Windows!' if user_lang != 'zh' else '不支持 Windows!')
    QproGlobalDir = __get_Qpro_fig_Dir()
    if not QproGlobalDir:
        return
    import json

    disable_global_command = '--disable_global_command' in sys.argv
    project_name = os.getcwd().split(dir_char)[-1]
    fig_dir = os.path.join(QproGlobalDir, 'fig')
    if os.path.exists(os.path.join(fig_dir, f'{project_name}.json')):
        QproDefaultConsole.print(QproWarnString,
                                 'This project has been registered!' if user_lang != 'zh' else '该项目已注册!')
        if _ask({
            'type': 'confirm',
            'name': 'confirm',
            'message': 'Do you want to override it?' if user_lang != 'zh' else '是否覆盖?',
            'default': False
        }):
            os.remove(os.path.join(fig_dir, f'{project_name}.json'))
        else:
            return
    import subprocess

    with open(os.path.join(fig_dir, f'{project_name}.json'), 'w') as f:
        project_subcommands = json.loads(subprocess.check_output(['qrun', '--qrun-fig-complete']).decode('utf-8'))
        if not project_subcommands:
            return QproDefaultConsole.print(QproErrorString, 'Not a Commander APP' if user_lang != 'zh' else '不是Commander应用')
        for item in project_subcommands:
            if 'args' in item:
                if 'options' not in item:
                    item['options'] = []
                for arg in item['args']:
                    if arg['name'].startswith('-') and not arg['name'].startswith('--'):
                        if 'file' in arg['name'] or 'path' in arg['name']:
                            arg['args']['template'] = ['filepaths', 'folders']
                        item['options'].append(arg)
                        item['args'].remove(arg)
                        continue
                    if 'file' in arg['name'] or 'path' in arg['name']:
                        arg['template'] = ['filepaths', 'folders']

        json.dump({
            'fig': {
                'name': project_name,
                'description': project_name,
                'subcommands': project_subcommands
            },
            'path': os.getcwd()
        }, f, ensure_ascii=False, indent=1)
    if disable_global_command:
        return
    with open(os.path.join(QproGlobalDir, 'bin', f'{project_name}'), 'w') as f:
        with open(get_config()['compile_filename'], 'r') as ff:
            ct = ff.read()
        if not ct.startswith('#!/usr/bin/env python3'):
            ct = '#!/usr/bin/env python3\n' + ct
        f.write(ct)
    os.chmod(os.path.join(QproGlobalDir, 'bin', f'{project_name}'), 0o755)


def gen_fig_script():
    if is_win:
        return QproDefaultConsole.print(QproWarnString, 'Not Support Windows!' if user_lang != 'zh' else '不支持 Windows!')
    QproGlobalDir = __get_Qpro_fig_Dir()
    if not QproGlobalDir:
        return
    import json
    from .QproFigTable import default_custom_command_template
    fig_Qpro_template = requirePackage('.QproFigTable', f'default_Qpro_{user_lang if user_lang == "zh" else "en"}_content_template')
    fig_qrun_template = requirePackage('.QproFigTable', f'default_qrun_{user_lang if user_lang == "zh" else "en"}_content_template')
    fig_detector_template = requirePackage('.QproFigTable', f'default_detector_{user_lang if user_lang == "zh" else "en"}_content_template')
    fig_tmpm_template = requirePackage('.QproFigTable', f'default_tmpm_{user_lang if user_lang == "zh" else "en"}_content_template')

    with open('src/Qpro.ts', 'w') as f:
        subcommands = os.listdir(os.path.join(QproGlobalDir, 'fig'))
        res = []
        for cmd in subcommands:
            with open(os.path.join(QproGlobalDir, 'fig', cmd), 'r') as cmdf:
                proj_name = cmd.split(".")[0]
                fig = json.load(cmdf)['fig']
                res.append(fig)
                if not os.path.exists(os.path.join(QproGlobalDir, 'bin', f'{proj_name}')):
                    continue
                with open(f'src/{proj_name}.ts', 'w') as custom_f:
                    custom_f.write(default_custom_command_template.replace('__CUSTOM_COMMAND_SPEC__', json.dumps(fig, ensure_ascii=False, indent=1)))
        f.write(fig_Qpro_template.replace('--Qpro-bin-subcommands-gen--', json.dumps(res, ensure_ascii=False, indent=1)))
    with open('src/qrun.ts', 'w') as f:
        f.write(fig_qrun_template)
    with open('src/detector.ts', 'w') as f:
        f.write(fig_detector_template)
    with open('src/tmpm.ts', 'w') as f:
        f.write(fig_tmpm_template)
    os.system('npm run copy-to-global')


def bin_exec():
    if is_win:
        return QproDefaultConsole.print(QproWarnString, 'Not Support Windows!' if user_lang != 'zh' else '不支持 Windows!')
    import json
    proj_name = sys.argv[2]
    proj_args = sys.argv[3:]
    QproGlobalDir = __get_Qpro_fig_Dir()
    if not QproGlobalDir:
        return
    if f'{proj_name}.json' not in os.listdir(os.path.join(QproGlobalDir, 'fig')):
        return QproDefaultConsole.print(QproErrorString, f'{proj_name} is not registered' if user_lang == 'zh' else f'{proj_name} 未注册')
    with open(os.path.join(QproGlobalDir, 'fig', f'{proj_name}.json'), 'r') as f:
        path = json.load(f)['path']
    os.chdir(path)
    os.system(f'qrun ' + ' '.join(proj_args))


def gen_zsh_comp():
    if is_win:
        return QproDefaultConsole.print(QproWarnString, 'Not Support Windows!' if user_lang != 'zh' else '不支持 Windows!')
    QproGlobalDir = __get_Qpro_fig_Dir()
    if not QproGlobalDir:
        return

    import json
    from .QproZshComp import zsh_comp_template

    subcommands = os.listdir(os.path.join(QproGlobalDir, 'fig'))
    file_comp1 = """
    else
        _arguments -S -s '*:filename:_files'
        return
    fi
    """
    file_comp2 = """
    _arguments -S -s '*:filename:_files'
    return
    """
    for cmd in subcommands:
        proj_name = cmd.split(".")[0]
        if not os.path.exists(os.path.join(QproGlobalDir, 'bin', f'{proj_name}')):
            continue
        with open(os.path.join(QproGlobalDir, 'fig', cmd), 'r') as cmdf:
            fig = json.load(cmdf)['fig']
        cur_sub_cmds = []
        sub_cmd_args = []
        for sub_cmd in fig['subcommands']:
            cur_sub_cmds.append(f"{sub_cmd['name']}:'{sub_cmd['description']}'")
            if 'args' in sub_cmd and sub_cmd['args']:
                cur_args = """if [[ ${prev} == __sub_cmd__ ]]; then
        opt_args=(
            __sub_cmd_opts__
        )"""
                sub_cmd_opts = []
                for arg in sub_cmd['args']:
                    if arg['name'].startswith('-'):
                        sub_cmd_opts.append(f"{arg['name']}:'{arg['description']}'")
                for opt in sub_cmd['options']:
                    if opt['name'].startswith('-'):
                        sub_cmd_opts.append(f"{opt['name']}:'{opt['description']}'")
                cur_args = cur_args.replace('__sub_cmd__', sub_cmd['name'])
                cur_args = cur_args.replace('__sub_cmd_opts__', '\n            '.join(sub_cmd_opts))
                sub_cmd_args.append(cur_args)

        with open('_' + fig['name'], 'w') as f:
            template = zsh_comp_template
            template = template.replace('__proj_name__', fig['name'])
            template = template.replace('__sub_commands__', '\n        '.join(cur_sub_cmds))
            template = template.replace('__sub_commands_args__', '\n    el'.join(sub_cmd_args) + file_comp1 if sub_cmd_args else file_comp2)
            f.write(template)


func = {
    'create': create,
    'scp': scp,
    'smv': smv,
    'get': get,
    'ssh': ssh,
    'del-all': delete_all,
    'del': delete,
    'ls': tele_ls,
    'csv': template_format,
    'bin': bin_exec,
    'enable-complete': enable_complete,
    'register-global': register_global_command,
    'gen-fig-script': gen_fig_script,
    'gen-zsh-comp': gen_zsh_comp,
}


def main():
    if len(sys.argv) < 2 or '-h' == sys.argv[1]:
        menu_output({'title': 'Qpro usage\n' if user_lang != 'zh' else 'Qpro 菜单\n',
                     'lines': [
                         ('init', 'let current dir be a Qpro project!' if user_lang != 'zh' else '使当前目录成为Qpro项目'),
                         ('-h', 'help' if user_lang != 'zh' else '帮助'),
                         ('create [bold magenta]<name>', 'create a Qpro project' if user_lang != 'zh' else '创建Qpro项目'),
                         ('update', 'update Qpro' if user_lang != 'zh' else '更新Qpro'),
                         ('ssh', 'login server by ssh' if user_lang != 'zh' else '通过SSH登录远程映射'),
                         (
                             'scp [bold magenta]<path>',
                             'upload path to default server target' if user_lang != 'zh' else '上传路径到默认的远程映射对应位置'
                         ),
                         (
                             'smv [bold magenta]<path>',
                             'delete after scp' if user_lang != 'zh' else '上传完成后删除文件或目录'
                         ),
                         (
                             'scp-init',
                             'upload all of project to server target' if user_lang != 'zh' else '上传当前全部内容到远程映射'
                         ),
                         (
                             'get [bold magenta]<path>',
                             'download file from server target' if user_lang != 'zh' else '从远程映射下载'
                         ),
                         (
                             'del [bold magenta]<path>',
                             'delete path in project' if user_lang != 'zh' else '同时删除本地及远程映射文件或目录'
                         ),
                         ('del-all', 'delete Qpro project' if user_lang != 'zh' else '销毁当前Qpro项目(本地+远程)'),
                         ('ls  [bold magenta]<path>', 'list element in path' if user_lang != 'zh' else '展示路径中的子项'),
                         ('enable-complete', 'enable complete' if user_lang != 'zh' else '启用Commander类的自动补全'),
                         ('register-global', 'register global command' if user_lang != 'zh' else '注册全局命令'),
                         ('gen-fig-script', 'generate fig autocomplete scripts' if user_lang != 'zh' else '生成Fig自动补全脚本'),
                         ('gen-zsh-comp', 'generate zsh autocomplete scripts' if user_lang != 'zh' else '生成zsh自动补全脚本'),
                         ('tmpm *', 'manage your template' if user_lang != 'zh' else '模板管理器'),
                         ('qrun *', 'run your Qpro project' if user_lang != 'zh' else '运行器'),
                         (
                             'detector -<p/f><p/f>',
                             'run beat detector for two source files' if user_lang != 'zh' else '对拍器'
                         )],
                     'prefix': 'Qpro'})
    elif 'update' == sys.argv[1]:
        os.system('pip3 install Qpro --upgrade')
    elif sys.argv[1] in func:
        try:
            func[sys.argv[1]]()
        except SystemExit:
            return
        except Exception:
            QproDefaultConsole.print_exception()
    elif sys.argv[1] == 'scp-init':
        scp_init(get_server_targets())
    elif 'init' != sys.argv[1]:
        QproDefaultConsole.print(
            QproErrorString, 'wrong usage! Run "Qpro -h" for help!' if user_lang != 'zh' else '请运行 "Qpro -h" 查看帮助!'
        )
    elif not os.path.exists(configure_name):
        pro_init()
    else:
        QproDefaultConsole.print(
            f"You have configured your project, see {project_configure_path} to adjust your configure!"
            if user_lang != 'zh' else
            f"你已经配置过这个项目啦, 查看配置表({project_configure_path})来调整它吧!"
        )


if __name__ == '__main__':
    main()
