from __future__ import annotations

import os
import sys

from .commander import Commander, str2bool
from .console import (
    QproDefaultConsole,
    QproDefaultStatus,
    QproErrorString,
    QproInfoString,
    QproWarnString,
    Status,
    VeyaDefaultConsole,
    VeyaDefaultStatus,
    VeyaErrorString,
    VeyaInfoString,
    VeyaWarnString,
    VeyoDefaultConsole,
    VeyoDefaultStatus,
    VeyoErrorString,
    VeyoInfoString,
    VeyoWarnString,
    _ask,
    ask,
    console,
    err_str,
    info_str,
    set_timeout,
    status,
    warn_str,
)
from .exec import external_exec, remove
from .i18n import _lang, get_lang, set_lang, user_lang

name = "veyo"
user_root = os.path.expanduser("~")
dir_char = os.sep

__all__ = [
    "Commander",
    "Status",
    "ask",
    "_ask",
    "console",
    "status",
    "info_str",
    "warn_str",
    "err_str",
    "external_exec",
    "remove",
    "set_timeout",
    "str2bool",
    "user_root",
    "user_lang",
    "dir_char",
    "get_lang",
    "set_lang",
    "_lang",
    "VeyoDefaultConsole",
    "VeyoDefaultStatus",
    "VeyoInfoString",
    "VeyoWarnString",
    "VeyoErrorString",
    "VeyaDefaultConsole",
    "VeyaDefaultStatus",
    "VeyaInfoString",
    "VeyaWarnString",
    "VeyaErrorString",
    "QproDefaultConsole",
    "QproDefaultStatus",
    "QproInfoString",
    "QproWarnString",
    "QproErrorString",
    "os",
    "sys",
]
