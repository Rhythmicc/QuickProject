from QuickProject.Commander import Commander
from . import *

app = Commander()


@app.command()
def build(name: str):
    """
    构建项目
    """
    with QproDefaultConsole.status('正在构建项目'):
        st, ct = external_exec('yarn run build')
    if st != 0:
        from QuickProject import QproErrorString
        QproDefaultConsole.print(QproErrorString, ct)


@app.command()
def post():
    """
    发布项目
    """


def main():
    """
    注册为全局命令时, 默认采用main函数作为命令入口, 请勿将此函数用作它途.
    When registering as a global command, default to main function as the command entry, do not use it as another way.
    """
    app()


if __name__ == '__main__':
    main()
