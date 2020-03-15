import os
import re
import sys
import colorama
from colorama import Fore, Style

COLORAMA_INIT_FLAG = True
if sys.platform.startswith('win'):
    is_win = True
    dir_char = '\\'
else:
    is_win = False
    dir_char = '/'
work_dir = os.getcwd()
work_project = work_dir.split(dir_char)[-1]
work_dir += dir_char

lang_template = {
    'cpp': """#include <iostream>
using namespace std;

int main(int argc, char **argv) {
    cout<<"hello world\\n";
    return 0;
}
""",
    'c': """#include <stdio.h>

int main(int argc, char **argv) {
    puts("hello world");
    return 0;
}
""",
    'java': """class CLASS_NAME {
    public static void main(String[] args) {
        System.out.println("hello world!");
    }
}
""",
    'python': """print 'hello world'""",
    'python3': """print('hello world')"""
}


def basic_string_replace(ss):
    global COLORAMA_INIT_FLAG
    if COLORAMA_INIT_FLAG:
        colorama.init()
        COLORAMA_INIT_FLAG = False
    ss = ss.split('\n')
    ret = ''
    for i in ss:
        if '[' in i:
            replace_list = re.findall('\[(.*?)\]', i)
            split_list = re.split('\[.*?\]', i)
            for p in range(len(split_list)):
                ret += Fore.CYAN + split_list[p] + Style.RESET_ALL
                if p < len(replace_list):
                    ret += Fore.RED + '[' + Fore.YELLOW + replace_list[p] + Fore.RED + ']' + Style.RESET_ALL
        else:
            ret += i
        ret += '\n'
    return ret


def remove(path):
    import shutil
    if os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)


def get_config():
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
    return config


def scp_init(server_target, ct=False):
    if server_target:
        server, target = get_server_target(server_target)
        user, ip = server.split('@')
        if ct:
            st = os.system('scp -r %s %s' % (work_project, user + '@\\[' + ip + '\\]:' + target))
        else:
            st = os.system('scp -r * %s' % user + '@\\[' + ip + '\\]:' + target)
        if st:
            exit("upload project failed!")


def create():
    try:
        project_name = sys.argv[sys.argv.index('-c') + 1]
        global work_project
        work_project = project_name
    except IndexError:
        exit('usage: Qpro -c project')
    else:
        if os.path.exists(project_name) and os.path.isdir(project_name):
            exit('"%s" is exist!' % (work_dir + project_name + dir_char))
        lang_tool_exe = {
            'c': ['gcc -std=c11', '', '', '.c'],
            'cpp': ['g++ -std=c++11', '', '', '.cpp'],
            'java': ['javac', '-d dist', 'java -classpath dist ', '.java'],
            'python3': ['', '', 'python3 ', '.py'],
            'python': ['', '', 'python ', '.py'],
            'empty': ['', '', '', '']
        }
        os.mkdir(project_name)
        langs = list(lang_tool_exe.keys())
        for i, lang in enumerate(langs):
            print('[%d] %-5s' % (i + 1, lang), end='\t' if (i + 1) % 3 else '\n')
        if len(langs) % 3:
            print()
        id_lang = 0
        while id_lang <= 0 or id_lang > len(langs):
            try:
                id_lang = int(input('choose one:'))
            except:
                id_lang = 0
        lang = lang_tool_exe[langs[id_lang - 1]]
        server_target = input('input [user@ip:dir_path] if you need scp:')
        if server_target and not server_target.endswith('/'):
            if not server_target.endswith(':'):
                server_target += '/'
            else:
                server_target += '~/'
        if not lang[-1]:
            source_file = ''
            execute = ''
        else:
            source_file = ('main' + lang[-1]) if lang[0] != 'javac' else project_name + lang[-1]
            if lang[0] != 'javac':
                execute = lang[2] + 'dist' + dir_char + project_name if lang[0] else lang[2] + source_file
            else:
                execute = lang[2] + project_name
            with open(project_name + dir_char + source_file, 'w') as f:
                if lang[-1] != '.other':
                    content = lang_template[langs[id_lang - 1]]
                    if lang[0] == 'javac':
                        content = content.replace('CLASS_NAME', project_name)
                    f.write(content)
            os.mkdir(project_name + dir_char + 'dist')
            os.mkdir(project_name + dir_char + 'template')
        info = [
            ['compile_tool', lang[0], lang[1]],
            ['compile_filename', source_file],
            ['executable_filename', execute],
            ['input_file', 'dist' + dir_char + 'input.txt' if lang[-1] else ''],
            ['template_root', 'template' + dir_char if lang[-1] else ''],
            ['server_target', server_target]
        ]
        with open(project_name + dir_char + 'project_configure.csv', 'w') as f:
            for row in info:
                f.write(','.join(row) + '\n')
        if lang[-1]:
            with open(project_name + dir_char + info[3][-1], 'w') as f:
                f.write('edit this file to make input')
            with open(project_name + dir_char + info[1][-1], 'r') as f:
                main_cont = f.read()
            with open(project_name + dir_char + 'template' + dir_char + 'main', 'w') as f:
                f.write(main_cont)
        scp_init(server_target, True)


def scp():
    try:
        path = sys.argv[sys.argv.index('-scp') + 1]
    except IndexError:
        exit('usage: Qpro -scp file')
    else:
        if not os.path.abspath(path).startswith(work_dir):
            exit("%s is not in this Qpro project!" % path)
        if not os.path.exists(path):
            exit('No such file named: ' + path)
        server, target = get_server_target()
        user, ip = server.split('@')
        if os.path.isdir(path):
            os.system('scp -r %s %s' % (path, user + '@\\[' + ip + '\\]:' + target + path))
        else:
            os.system('scp %s %s' % (path, user + '@\\[' + ip + '\\]:' + target + path))


def get():
    try:
        path = sys.argv[sys.argv.index('-get') + 1]
    except IndexError:
        exit('usage: Qpro -get file')
    else:
        if not os.path.abspath(path).startswith(work_dir):
            exit("%s is not in this Qpro project!" % path)
        server, target = get_server_target()
        user, ip = server.split('@')
        os.system('scp -r %s %s' % (user + '@\\[' + ip + '\\]:' + target + path, path))


def adjust():
    config = get_config()
    import tkinter as tk
    win = tk.Tk()
    win.title('Qpro项目调整器')
    key_to_name = {
        'compile_tool': '编译指令:',
        'compile_filename': '源程序:',
        'executable_filename': '运行指令:',
        'input_file': '输入文件:',
        'template_root': '模板目录:',
        'server_target': '远程映射:'
    }
    all_dt = {}
    for i, v in enumerate(config):
        tk.Label(win, text='%12s' % key_to_name[v]).grid(row=i, column=0)
        if v == 'compile_tool':
            stringvar1 = tk.Variable()
            stringvar1.set(config[v][0])
            stringvar2 = tk.Variable()
            stringvar2.set(config[v][1])
            tk.Entry(win, textvariable=stringvar1, width=20).grid(row=i, column=1)
            tk.Entry(win, textvariable=stringvar2, width=19).grid(row=i, column=2)
            all_dt[v] = [stringvar1, stringvar2]
        else:
            stringvar1 = tk.Variable()
            stringvar1.set(config[v])
            tk.Entry(win, textvariable=stringvar1, width=40).grid(row=i, column=1, columnspan=2)
            all_dt[v] = stringvar1

    def deal_config():
        for dt in all_dt:
            if dt == 'compile_tool':
                config[dt] = [all_dt[dt][0].get(), all_dt[dt][1].get()]
            elif dt == 'server_target':
                config[dt] = all_dt[dt].get()
                if config[dt]:
                    if ':' in config[dt] and not config[dt].endswith('/') and not config[dt].endswith(':'):
                        config[dt] += '/'
                    elif ':' not in config[dt]:
                        print('Not a legal server target!\n'
                              'You can run "Qpro -adjust" to adjust target\n'
                              'and run "Qpro -scp-init" to upload project.')
            else:
                config[dt] = all_dt[dt].get()
        if not config['template_root'].endswith(dir_char):
            config['template_root'] += dir_char
        win.destroy()
        with open('project_configure.csv', 'w') as file:
            for line in config:
                if line == 'compile_tool':
                    file.write('%s,%s\n' % (line, ','.join(config[line])))
                else:
                    file.write('%s,%s\n' % (line, config[line]))

    tk.Button(win, text='确认', command=deal_config, width=10).grid(row=6, column=0, columnspan=3)
    tk.mainloop()


def pro_init():
    id_lang = -1
    langs = []
    if not os.path.exists('CMakeLists.txt'):
        ask = input('Not an CLion Project!' + 'You need make configure manually [y/n]:').strip()
        if 'y' not in ask and 'Y' not in ask:
            exit(0)
        global work_project
        while not work_project:
            work_project = input('You need to set project name:').strip()
        lang_tool_exe = {
            'c': ['gcc -std=c11', '', '', '.c'],
            'cpp': ['g++ -std=c++11', '', '', '.cpp'],
            'java': ['javac', '-d dist', 'java -classpath dist ', '.java'],
            'python3': ['', '', 'python3 ', '.py'],
            'python': ['', '', 'python ', '.py'],
            'empty': ['', '', '', '']
        }
        langs = list(lang_tool_exe.keys())
        for i, lang in enumerate(langs):
            print('[%d] %-5s' % (i + 1, lang), end='\t' if (i + 1) % 3 else '\n')
        if len(langs) % 3:
            print()
        id_lang = 0
        while id_lang <= 0 or id_lang > len(langs):
            try:
                id_lang = int(input('choose one:'))
            except:
                id_lang = 0
        lang = lang_tool_exe[langs[id_lang - 1]]
        source_file = ''
        if langs[id_lang - 1] != 'empty':
            source_file = ('main' + lang[-1]) if lang[0] != 'javac' else work_project + lang[-1]
            while not os.path.exists(source_file):
                source_file = input('Not found "%s", set compile_filename:' % source_file).strip()
        server_target = input('input [user@ip:dir_path] if you need scp:').strip().replace('\\', '/')
        if ':' in server_target and not server_target.endswith('/'):
            if not server_target.endswith(':'):
                server_target += '/'
            else:
                server_target += '~/'
        if lang[0] != 'javac':
            execute = lang[2] + 'dist' + dir_char + work_project if lang[0] else lang[2] + source_file
        elif langs[id_lang - 1] != 'empty':
            work_project = source_file.split(dir_char)[-1].split('.')[0]
            execute = lang[2] + work_project
        else:
            execute = ''
        if (not os.path.exists('dist') or not os.path.isdir('dist')) and langs[id_lang - 1] != 'empty':
            os.mkdir('dist')
        info = [
            ['compile_tool', lang[0], lang[1]],
            ['compile_filename', source_file],
            ['executable_filename', execute],
            ['input_file', 'dist' + dir_char + 'input.txt' if langs[id_lang - 1] != 'empty' else ''],
            ['template_root', 'template' + dir_char if langs[id_lang - 1] != 'empty' else ''],
            ['server_target', server_target]
        ]
    else:
        with open("CMakeLists.txt", 'r') as f:
            content = f.read()
        project_name = re.findall('project\((.*?)\)', content)[0].split()[0]
        if '.cpp' in content or '.CPP' in content:
            is_cpp = True
        else:
            is_cpp = False
        print('Project name:%s(%s)' % (project_name, 'CPP' if is_cpp else 'C'))
        project_name = 'cmake-build-debug' + dir_char + project_name
        source_file = 'main.c' + ('pp' if is_cpp else '')
        pro_root = dir_char.join(project_name.split(dir_char)[:-1])
        default_input = pro_root + dir_char + 'input.txt'
        server_target = input('input [user@ip:dir_path] if you need scp:').strip().replace('\\', '/')
        if ':' in server_target and not server_target.endswith('/') and not server_target.endswith(':'):
            server_target += '/'
        elif server_target:
            print('Not a legal server target!\n'
                  'You can run "Qpro -adjust" to adjust target\n'
                  'and run "Qpro -scp-init" to upload project.')
        print('adding project_configure')
        info = [
            ['compile_tool', 'g++ -std=c++11' if is_cpp else 'gcc -std=c11', ''],
            ['compile_filename', source_file],
            ['executable_filename', project_name],
            ['input_file', default_input],
            ['template_root', 'template' + dir_char],
            ['server_target', server_target]
        ]
    with open('project_configure.csv', 'w') as f:
        for row in info:
            f.write(','.join(row) + '\n')
    if id_lang >= 0 and langs[id_lang - 1] == 'empty':
        scp_init(server_target)
        exit(0)
    with open(info[3][-1], 'w') as f:
        f.write('edit this file to make input')
    if not os.path.exists('template') or not os.path.isdir('template'):
        os.mkdir('template')
    try:
        with open(info[1][-1], 'r') as f:
            main_cont = f.read()
        with open('template' + dir_char + 'main', 'w') as f:
            f.write(main_cont)
    except Exception as e:
        print("make backup failed with error: %s, you need backup code by yourself!" % e)
    scp_init(server_target)


def get_server_target(st=None):
    if not st:
        ls = get_config()['server_target'].split(':')
    else:
        ls = st.split(':')
    if len(ls) > 2:
        server = ':'.join(ls[:8])
        target = ':'.join(ls[8:])
    else:
        server, target = ls
    return server, target


def ssh():
    server, target = get_server_target()
    os.system("ssh -t %s 'cd %s ; exec $SHELL -l'" % (server, target))


def delete_all():
    config = get_config()
    if ':' in config['server_target']:
        server, target = get_server_target()
        st = os.system("ssh %s 'rm -rf %s'" % (server, target))
        if st:
            return
    remove(os.getcwd())


def delete():
    try:
        path = sys.argv[sys.argv.index('-del') + 1]
    except IndexError:
        exit('usage: Qpro -del path')
    else:
        if not os.path.abspath(path).startswith(work_dir):
            exit("%s is not in this Qpro project!" % path)
        if not os.path.exists(path):
            exit('No such file named: ' + path)
        config = get_config()
        path = path.strip('.' + dir_char)
        path = path.strip(dir_char)
        if ':' in config['server_target']:
            server, target = get_server_target()
            st = os.system("ssh %s 'rm -rf %s'" % (server, target + path))
            if st:
                return
        remove(path)


def tele_ls():
    try:
        path = sys.argv[sys.argv.index('-ls') + 1]
    except IndexError:
        path = ''
    config = get_config()
    if path:
        path = path.strip('.' + dir_char)
        path = path.strip(dir_char)
    if ':' in config['server_target']:
        server, target = get_server_target()
        os.system("ssh %s 'ls %s'" % (server, target + path))


func = {
    '-c': create,
    '-scp': scp,
    '-get': get,
    '-adjust': adjust,
    '-ssh': ssh,
    '-del-all': delete_all,
    '-del': delete,
    '-ls': tele_ls
}


def main():
    if len(sys.argv) < 2 or '-h' == sys.argv[1]:
        print(basic_string_replace('usage:\n'
                                   '   * [Qpro -init    ]: let dir be a Qpro project!\n'
                                   '   * [Qpro -h       ]: help\n'
                                   '   * [Qpro -c name  ]: create a Qpro project\n'
                                   '   * [Qpro -update  ]: update Qpro\n'
                                   '   * [Qpro -adjust  ]: adjust configure\n'
                                   '   * [Qpro -ssh     ]: login server by ssh\n'
                                   '   * [Qpro -scp path]: upload path to default server target\n'
                                   '   * [Qpro -scp-init]: upload all of project to server target\n'
                                   '   * [Qpro -get path]: download file from server target\n'
                                   '   * [Qpro -del path]: delete path in project\n'
                                   '   * [Qpro -del-all ]: delete Qpro project\n'
                                   '   * [Qpro -ls path ]: list element in path\n'
                                   '   * [tmpm *        ]: manage your template\n'
                                   '   * [qrun *        ]: run your Qpro project\n'
                                   '   * [detector -(p/f)(p/f)]: run beat detector for two source files'))
    elif '-update' == sys.argv[1]:
        os.system('pip3 install Qpro --upgrade')
        exit(0)
    elif sys.argv[1] in func:
        func[sys.argv[1]]()
    elif sys.argv[1] == '-scp-init':
        scp_init(get_config()['server_target'])
    elif '-init' not in sys.argv:
        exit('wrong usage! Run "Qpro -h" for help!')
    elif not os.path.exists('project_configure.csv'):
        pro_init()
    else:
        exit("You have configured your project, see project_configure to adjust your configure!")


if __name__ == '__main__':
    main()
