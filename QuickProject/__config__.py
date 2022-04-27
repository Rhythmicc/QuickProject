from inquirer_rhy.prompt import prompt
import sys
from rich.console import Console

QproDefaultConsole = Console()
system = sys.platform
if system.startswith('win'):
    dir_char = '\\'
else:
    dir_char = '/'

default_language = {
    'type': 'input',
    'name': 'default_language',
    'message': """Select your language, the flowing content is available choice
  选择你的语言，下述内容为合法选项

    zh  (Chinese) en  (English)  jp  (Japanese) kor (Korean)   fra (French), 
    spa (Spanish) th  (Thailand) ara (al-ummah) ru  (Russian)  pt  (Portuguese), 
    de  (Germany) it  (Italy)    el  (Greece)   nl  (Poland)   bul (Bulgaria),
    est (Estonia) dan (Denmark)  fin (Finland)  cs  (Czech)    rom (Romania),
    slo (Iceland) swe (Sweden)   hu  (Hungary)  vie (Vietnam)

  Input the default language | 输入默认语言:""",
    'validate': lambda val: val in ['zh', 'en', 'jp', 'kor', 'fra',
                                    'spa', 'th', 'ara', 'ru', 'pt',
                                    'de', 'it', 'el', 'nl', 'bul',
                                    'est', 'dan', 'fin', 'cs', 'rom',
                                    'slo', 'swe', 'hu', 'vie', 'Not Set | 暂不配置'],
    'default': 'Not Set | 暂不配置'
}

default_pip = {
    'type': 'input',
    'name': 'default_pip',
    'message': 'Input the default pip | 输入默认pip:',
    'default': 'pip3'
}


class QproConfig:
    import json

    def __init__(self, configPath, isExists):
        self.path = configPath
        if isExists:
            try:
                with open(configPath, 'r') as f:
                    self.config = QproConfig.json.loads(f.read())
            except:
                with open(configPath, 'r', encoding='utf8') as f:
                    self.config = QproConfig.json.loads(f.read(), encoding='utf8')
        else:
            self.config = QproConfig.json.loads("""{
    "default_language": "",
    "default_pip": ""
}""")
            res = prompt([default_language, default_pip])
            self.config['default_language'] = res['default_language'] if res['default_language'] != 'Not Set | 暂不配置' else 'en'
            self.config['default_pip'] = res['default_pip']
            self.update()
            QproDefaultConsole.print(
                '\nYour configuration table has been stored\n你的配置表被存储在: [bold green]' + '%s' % configPath + '[/bold '
                                                                                                            'green]')
            QproDefaultConsole.print('[bold red]\nqs will not use your configuration do '
                                     'anything!\nQpro不会用您的配置表做任何事情![/bold red]')
            prompt({
                'type': 'confirm',
                'message': 'Confirm | 确认',
                'name': 'done',
                'default': True
            })

    def update(self):
        with open(self.path, 'w') as f:
            QproConfig.json.dump(self.config, f, indent=4, separators=(',', ': '))

    def select(self, key: str):
        if key not in self.config:
            exec(f'res = prompt([{key}])')
            exec(f"self.config['{key}'] = res['{key}']")
            self.update()
        return self.config[key]


def _ask(question):
    try:
        return prompt(question)[question['name']]
    except:
        exit(0)
