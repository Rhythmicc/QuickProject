import os
from QuickStart_Rhy import remove, dir_char
from QuickProject.Commander import Commander

app = Commander()


@app.command()
def upload(msg: list):
    remove('dist')
    if os.system('python3 setup.py sdist'):
        os.system('python setup.py sdist')
    os.system(f'twine upload dist{dir_char}*')
    os.system('git add .')
    os.system(f'git commit -m "{" ".join(msg)}"')
    os.system('git push')


@app.command()
def post(path: str):
    os.system(f'Qpro scp {path}')


@app.command()
def get(path: str):
    os.system(f'Qpro get {path}')


if __name__ == '__main__':
    app()
