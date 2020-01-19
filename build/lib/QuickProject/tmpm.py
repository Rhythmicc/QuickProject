import sys
import os
from QuickProject.Qpro import basic_string_replace

if sys.platform.startswith('win'):
    dir_char = '\\'
else:
    dir_char = '/'
config = {}
try:
    with open('project_configure.csv', 'r') as f:
        for row in f.readlines():
            row = row.split(',')
            config[row[0]] = [i.strip() for i in row[1:]]
        for i in config:
            if i != 'compile_tool':
                config[i] = config[i][0]
        if not config['template_root']:
            exit('You need set template folder first!')
        if not config['template_root'].endswith(dir_char):
            config['template_root'] += dir_char
except IOError:
    exit("No file named: project_configure.csv\n May you need run:\"Qpro -init\" first!")
is_cpp = config['compile_filename'].endswith('cpp')
algorithm_name = 'main'
temp_name = 'main'


def match_algorithm():
    with open(config['compile_filename'], 'r') as file:
        import re
        try:
            content = re.findall('/// __START__(.*?)/// __END__', file.read(), re.S)[0].strip()
        except IndexError:
            exit('No template index found! Insert "/// __START__" and "/// __END__" to your code!')
    content = content.replace('/// __TEMPLATE__', '')
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
            exit('usage: tmpm -c template (algorithm)')
    temp_name += '.md'
    if os.path.exists(config['template_root'] + temp_name):
        if input('Template %s is already exist, would you cover it?[y/n]:' % temp_name) == 'n':
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
        exit('usage: tmpm -a template algorithm')
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
            content = re.findall('##(.*?)\n.*?```.*?\n(.*?)```', file.read(), re.S)
            for i, v in enumerate(content):
                print('[%d] %s' % (i + 1, v[0].strip()), end=' ' if i + 1 % 10 else '\n')
            indx = int(input('%s选择:' % ('\n' if len(content) % 10 else ''))) - 1
            content = content[indx]
        with open(config['compile_filename'], 'r') as file:
            content = file.read().replace('/// __TEMPLATE__', content[1].strip() + '\n/// __TEMPLATE__')
        with open(config['compile_filename'], 'w') as file:
            file.write(content)
    else:
        exit('No template named: %s' % temp_name)


def h():
    print(basic_string_replace('(tmpm.py) usage:\n'
                               '   * [tmpm -h]: for help\n'
                               '   * [tmpm -r]: select copy and init\n'
                               '   * [tmpm -r backup]: init "compile_filename" to template/backup\n'
                               '   * [tmpm -c backup]: create or cover a backup\n'
                               '   * [tmpm -c template algorithm]: create template and write algorithm\n'
                               '   * [tmpm -a template algorithm]: add algorithm to template\n'
                               '   * [tmpm template]: insert algorithm in template'))


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
        ls = os.listdir(config['template_root'])
        rls = []
        cnt = 1
        for i in ls:
            if '.' not in i:
                print('[%d] %s' % (cnt, i), end='\t' if cnt % 8 else '\n')
                rls.append(i)
                cnt += 1
        if cnt % 8:
            print()
        try:
            indx = int(input('选择:'))
            if indx < 0 or indx > len(rls):
                raise IndexError
        except:
            exit('ERROR!')
        file_name = rls[indx - 1]
        return init(file_name)
    if os.path.exists(config['template_root'] + file_name):
        init(file_name)
    else:
        exit('No such backup')


def main():
    if len(sys.argv) == 1:
        init()
    elif '-h' in sys.argv:
        h()
    elif '-c' in sys.argv:
        create()
    elif '-a' in sys.argv:
        append()
    elif '-r' in sys.argv:
        revert()
    else:
        join()


if __name__ == '__main__':
    main()
