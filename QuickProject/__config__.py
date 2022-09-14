from inquirer_rhy.prompt import prompt
import sys
import json
from rich.console import Console

QproDefaultConsole = Console()
system = sys.platform
if system.startswith('win'):
    dir_char = '\\'
else:
    dir_char = '/'


def _ask(question: dict):
    try:
        if 'name' not in question:
            question['name'] = 'NoName'
        return prompt(question)[question['name']]
    except:
        exit(0)


default_language = {
    'type': 'input',
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

problems = {
    'default_language': default_language,
    'default_pip': {
        'type': 'input',
        'message': 'Input the default pip | 输入默认pip:',
        'default': 'pip3'
    },
    'using_gitee': {
        'type': 'confirm',
        'message': 'Use gitee as default git source | 是否默认使用gitee作为git源? ',
        'default': False
    }
}


def _init_config(configPath: str):
    config = {}
    for k, v in problems.items():
        config[k] = _ask(v)
    with open(configPath, 'w') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    QproDefaultConsole.print(
        '\nYour configuration table has been stored\n你的配置表被存储在: [bold green]' + '%s' % configPath + '[/bold green]')
    QproDefaultConsole.print('[bold red]\nqs will not use your configuration do '
                             'anything!\nQpro不会用您的配置表做任何事情![/bold red]')
    _ask({
        'type': 'confirm',
        'message': 'Confirm | 确认',
        'default': True
    })


class QproConfig:
    import json

    def __init__(self, configPath, isExists):
        self.path = configPath
        if not isExists:
            _init_config(configPath)
        else:
            try:
                with open(configPath, 'r') as f:
                    self.config = QproConfig.json.load(f)
            except:
                with open(configPath, 'r', encoding='utf8') as f:
                    self.config = QproConfig.json.load(f, encoding='utf8')

    def update(self):
        with open(self.path, 'w') as f:
            QproConfig.json.dump(self.config, f, indent=4, separators=(',', ': '))

    def select(self, key: str):
        if key not in self.config and key in problems:
            self.config[key] = _ask(problems[key])
            self.update()
        return self.config.get(key, None)
