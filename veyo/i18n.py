from __future__ import annotations

import locale
import os

_TRANSLATIONS: dict[str, dict[str, str]] = {
    "error": {"zh": "错误", "en": "ERRO"},
    "information": {"zh": "信息", "en": "INFO"},
    "warning": {"zh": "警告", "en": "WARN"},
    "Parameter": {"zh": "参数", "en": "Parameter"},
    "Description": {"zh": "描述", "en": "Description"},
    "NotFunction": {"zh": "不是函数", "en": "Not a function"},
    "CommandAlreadyExists": {"zh": "已经在命令表中", "en": "Already in command table"},
    "CantHaveDefaultValue": {
        "zh": "不能有默认值",
        "en": "Cannot have a default value",
    },
    "SubCommand": {"zh": "子命令", "en": "Subcommand"},
    "RequiredArgs": {"zh": "必填参数", "en": "Required Args"},
    "OptionalArgs": {"zh": "可选参数", "en": "Optional Args"},
    "OptionnalArgs": {"zh": "可选参数", "en": "Optional Args"},
    "NoSuchCommand": {"zh": "没有这个命令", "en": "No such command"},
    "NoCommandInput": {"zh": "没有输入命令", "en": "No command input"},
    "UserInterrupt": {"zh": "用户中断", "en": "User interrupt"},
    "OverwriteCompleteDir": {
        "zh": "complete 文件夹已存在，是否覆盖？",
        "en": "complete directory already exists, overwrite?",
    },
    "NoDescription": {"zh": "没有描述", "en": "No description"},
    "ScriptComplete": {
        "zh": "为了使 zsh 补全生效，请执行 `source .{}rc`",
        "en": "To enable zsh completion, run `source .{}rc`",
    },
}


def detect_system_lang(default: str = "en") -> str:
    """Detect preferred language ('zh' or 'en') from environment/locale without I/O prompts."""
    for env_key in ("VEYO_LANG", "VEYA_LANG", "LC_ALL", "LC_MESSAGES", "LANG"):
        val = os.environ.get(env_key, "").strip().lower()
        if val:
            if val.startswith("zh") or "chinese" in val:
                return "zh"
            if val.startswith("en") or "english" in val:
                return "en"
    try:
        loc, _ = locale.getlocale()
        if loc and loc.lower().startswith("zh"):
            return "zh"
    except Exception:
        pass
    return default


class LangDict:
    """Lightweight bilingual dictionary lookup compatible with legacy `_lang[key]` access."""

    def __init__(self, lang: str | None = None) -> None:
        self.lang = lang if lang in ("zh", "en") else detect_system_lang()

    def __getitem__(self, key: str) -> str:
        entry = _TRANSLATIONS.get(key)
        if not entry:
            return key
        return entry.get(self.lang, entry.get("en", key))

    def get(self, key: str, default: str | None = None) -> str | None:
        if key in _TRANSLATIONS:
            return self[key]
        return default


_lang = LangDict()
user_lang: str = _lang.lang


def get_lang() -> str:
    return _lang.lang


def set_lang(lang: str) -> None:
    """Set active language ('zh' or 'en')."""
    global user_lang
    normalized = "zh" if lang.lower().startswith("zh") else "en"
    _lang.lang = normalized
    user_lang = normalized
