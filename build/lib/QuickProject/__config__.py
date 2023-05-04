import os

from langsrc import LanguageDetector
import sys
import json
from rich.console import Console

QproDefaultConsole = Console()
system = sys.platform
if system.startswith("win"):
    dir_char = "\\"
else:
    dir_char = "/"

_guess_pip_path = os.path.join(os.path.dirname(sys.executable), "pip3")
_guess_pip_path = _guess_pip_path if os.path.exists(_guess_pip_path) else "pip3"


class Status:
    def __init__(
        self,
        status,
        *,
        spinner: str = "dots",
        spinner_style: str = "status.spinner",
        speed: float = 1.0,
        refresh_per_second: float = 12.5,
    ) -> None:
        self._status = QproDefaultConsole.status(
            status,
            spinner=spinner,
            spinner_style=spinner_style,
            speed=speed,
            refresh_per_second=refresh_per_second,
        )
        self.started = False

    def __call__(
        self,
        status,
        *,
        spinner: str = "dots",
        spinner_style: str = "status.spinner",
        speed: float = 1.0,
    ):
        self._status.update(
            status,
            spinner=spinner,
            spinner_style=spinner_style,
            speed=speed,
        )
        return self

    def update(
        self,
        status,
        *,
        spinner: str = "dots",
        spinner_style: str = "status.spinner",
        speed: float = 1.0,
    ):
        self._status.update(
            status,
            spinner=spinner,
            spinner_style=spinner_style,
            speed=speed,
        )

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def start(self):
        if not self.started:
            self._status.start()
            self.started = True

    def stop(self):
        if self.started:
            self._status.stop()
            self.started = False

    @property
    def status(self):
        return self.started


QproDefaultStatus = Status("")


def set_timeout(num: int):
    """
    定时函数装饰器

    Timing function decorator

    :param num: 时间（秒）
    :return: wrapper
    """

    assert isinstance(num, int) and num > 0, "num must be a positive integer"

    def wrapper(func):
        def handle(signum, frame):
            raise RuntimeError

        def run(*args, **kwargs):
            import signal

            try:
                signal.signal(signal.SIGALRM, handle)
                signal.alarm(num)
                res = func(*args, **kwargs)
                signal.alarm(0)
                return res
            except RuntimeError:
                return None

        return run

    return wrapper


def _ask(question: dict, timeout: int = 0, _init: bool = False):
    from inquirer_rhy.prompt import prompt

    record_status = QproDefaultStatus.status

    if timeout:

        @set_timeout(timeout)
        def ask():
            try:
                res = prompt(
                    question,
                    keyboard_interrupt_msg=_lang["UserInterrupt"]
                    if not _init
                    else None,
                )[question["name"]]
            except:
                os.system("stty echo")
                res = question.get("default", None)
            finally:
                if record_status:
                    QproDefaultStatus.start()
                return res

    else:

        def ask():
            try:
                res = prompt(
                    question,
                    keyboard_interrupt_msg=_lang["UserInterrupt"]
                    if not _init
                    else None,
                )[question["name"]]
            except Exception as e:
                QproDefaultConsole.print(repr(e))
                res = None
            finally:
                if record_status:
                    QproDefaultStatus.start()
                return res

    if "name" not in question:
        question["name"] = "NoName"
    QproDefaultStatus.stop()
    return ask()


default_language = {
    "type": "input",
    "message": """Select your language, the flowing content is available choice
  选择你的语言，下述内容为合法选项

    zh  (Chinese)  en  (English)  fra (French)  
    ru  (Russian)  spa (Spanish)  ara (Arabic) 

  Input the default language | 输入默认语言:""",
    "validate": lambda val: val
    in ["zh", "en", "fra", "spa", "ara", "ru", "Not Set | 暂不配置"],
    "default": "Not Set | 暂不配置",
}

problems = {
    "default_language": default_language,
    "default_pip": {
        "type": "input",
        "message": "Input the default pip | 输入默认pip:",
        "default": _guess_pip_path,
    },
    "using_gitee": {
        "type": "confirm",
        "message": "Use gitee as default git source | 是否默认使用gitee作为git源? ",
        "default": False,
    },
}


def _init_config(configPath: str):
    config = {}
    for k, v in problems.items():
        config[k] = _ask(v, _init=True)
    with open(configPath, "w") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    QproDefaultConsole.print(
        "\nYour configuration table has been stored\n你的配置表被存储在: [bold green]"
        + "%s" % configPath
        + "[/bold green]"
    )
    QproDefaultConsole.print(
        "[bold red]\nqs will not use your configuration do "
        "anything!\nQpro不会用您的配置表做任何事情![/bold red]"
    )
    _ask({"type": "confirm", "message": "Confirm | 确认", "default": True})


class QproConfig:
    def __init__(self, configPath, isExists):
        self.path = configPath
        if not isExists:
            _init_config(configPath)
        try:
            with open(configPath, "r") as f:
                self.config = json.load(f)
        except:
            with open(configPath, "r", encoding="utf8") as f:
                self.config = json.load(f)

    def update(self):
        with open(self.path, "w") as f:
            json.dump(self.config, f, indent=4, separators=(",", ": "))

    def select(self, key: str):
        if key not in self.config and key in problems:
            self.config[key] = _ask(problems[key])
            self.update()
        return self.config.get(key, None)


user_root = os.path.expanduser("~")

_qpro_config = QproConfig(
    user_root + dir_char + ".qprorc", os.path.exists(user_root + dir_char + ".qprorc")
)

user_lang = _qpro_config.select("default_language")
_lang = LanguageDetector(
    user_lang, os.path.join(os.path.dirname(__file__), "lang.json")
)
