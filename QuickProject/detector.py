import difflib
import os
import shutil
import webbrowser as wb
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from QuickProject import get_config


def read_file(filename):
    try:
        with open(filename.replace('\ ', ' '), 'r') as f:
            return f.readlines()
    except IOError:
        messagebox.showerror("ERROR:", "没有找到文件:%s" % filename)
        return


def compare_file(f1, f2, out_file):
    file1_content = read_file(f1.strip())
    file2_content = read_file(f2.strip())
    d = difflib.HtmlDiff()
    result = d.make_file(file1_content, file2_content)
    with open(out_file, 'w') as f:
        f.writelines(result)


def get_path1():
    global file1
    file1 = filedialog.askopenfilename()
    path1.set(file1)


def get_path2():
    global file2
    file2 = filedialog.askopenfilename()
    path2.set(file2)


def get_path3():
    global file3
    file3 = filedialog.askopenfilename()
    path3.set(file3)
    ll.configure(fg='black')


def remove(path):
    if os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)


def cmp():
    if not file1 or not file2:
        messagebox.showerror("文件数不足", "请选择两个文件进行对比")
        return
    cp1 = len(sys.argv) < 2 or sys.argv[1].startswith('-p')
    cp2 = len(sys.argv) < 2 or sys.argv[1].endswith('p')
    file_path1 = 'content1'
    file_path2 = 'content2'
    if file3 == '使用默认输入文件':
        if cp1:
            os.system('qrun -br -i -f %s > content1' % file1.replace(' ', '\ '))
        else:
            file_path1 = file1
        if cp2:
            os.system('qrun -br -i -f %s > content2' % file2.replace(' ', '\ '))
        else:
            file_path2 = file2
    else:
        if cp1:
            os.system('qrun -br -if %s -f %s > content1' % (file3.replace(' ', '\ '), file1.replace(' ', '\ ')))
        else:
            file_path1 = file1
        if cp2:
            os.system('qrun -br -if %s -f %s > content2' % (file3.replace(' ', '\ '), file2.replace(' ', '\ ')))
        else:
            file_path2 = file2
    compare_file(file_path1, file_path2, './res.html')
    res_path = os.path.abspath('./res.html')
    wb.open('file://%s' % res_path)
    remove('content1')
    remove('content2')


status = {
    '-pp': '程序--程序',
    '-pf': '程序--文件',
    '-fp': '文件--程序',
    '-ff': '文件--文件',
}

title_status = '默认' if len(sys.argv) < 2 else status[sys.argv[1]]
width = 30
win = tk.Tk()
win.title('对拍器 %s' % title_status)
file1, path1 = '', tk.StringVar()
file2, path2 = '', tk.StringVar()
file3, path3 = '使用默认输入文件', tk.StringVar()
path3.set(file3)
ll = tk.Label(win, textvariable=path3, width=width, fg='red')


def main():
    if not get_config() and sys.argv[1] != '-ff':
        from QuickProject import QproDefaultConsole, QproErrorString
        return QproDefaultConsole.print(QproErrorString, "You must run \"Qpro -init\" first")
    tk.Label(win, text='%12s' % "文件1路径:").grid(row=0, column=0)
    tk.Label(win, textvariable=path1, width=width).grid(row=0, column=1)
    tk.Button(win, text="路径选择", command=get_path1).grid(row=0, column=2)
    tk.Label(win, text='%12s' % "文件2路径:").grid(row=1, column=0)
    tk.Label(win, textvariable=path2, width=width).grid(row=1, column=1)
    tk.Button(win, text="路径选择", command=get_path2).grid(row=1, column=2)
    if len(sys.argv) < 2 or 'p' in sys.argv[1]:
        tk.Label(win, text='%12s' % "输入文件:").grid(row=2, column=0)
        ll.grid(row=2, column=1)
        tk.Button(win, text="路径选择", command=get_path3).grid(row=2, column=2)
    tk.Button(win, text="对比", command=cmp).grid(row=3, column=1)
    tk.mainloop()


if __name__ == '__main__':
    main()
