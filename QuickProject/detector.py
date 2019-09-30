import difflib
import os
import webbrowser as wb
import sys
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox


if sys.platform.startswith('win'):
    dir_char = '\\'
else:
    dir_char = '/'


def read_file(filename):
    try:
        with open(filename, 'r') as f:
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


def cmp():
    if not file1 or not file2:
        messagebox.showerror("文件数不足", "请选择两个文件进行对比")
        return
    if file3 == '使用默认输入文件':
        os.system('QProRun -br -i -f %s > content1' % file1)
        os.system('QProRun -br -i -f %s > content2' % file2)
    else:
        os.system('QProRun -br -if %s -f %s > content1' % (file3, file1))
        os.system('QProRun -br -if %s -f %s > content2' % (file3, file2))
    compare_file('content1', 'content2', './res.html')
    wb.open('file://res.html')
    os.remove('content1')
    os.remove('content2')


win = tk.Tk()
win.title('对拍器')
file1, path1 = '', tk.StringVar()
file2, path2 = '', tk.StringVar()
file3, path3 = '使用默认输入文件', tk.StringVar()
path3.set(file3)
width = 30
tk.Label(win, text='%12s' % "文件1路径:").grid(row=0, column=0)
tk.Label(win, textvariable=path1, width=width).grid(row=0, column=1)
tk.Button(win, text="路径选择", command=get_path1).grid(row=0, column=2)
tk.Label(win, text='%12s' % "文件2路径:").grid(row=1, column=0)
tk.Label(win, textvariable=path2, width=width).grid(row=1, column=1)
tk.Button(win, text="路径选择", command=get_path2).grid(row=1, column=2)
tk.Label(win, text='%12s' % "输入文件:").grid(row=2, column=0)
ll = tk.Label(win, textvariable=path3, width=width, fg='red')
ll.grid(row=2, column=1)
tk.Button(win, text="路径选择", command=get_path3).grid(row=2, column=2)
tk.Button(win, text="对比", command=cmp).grid(row=3, column=1)


def main():
    if not os.path.exists('project_configure.csv'):
        exit("You must run \"Qpro -init\" first")
    tk.mainloop()


if __name__ == '__main__':
    main()
