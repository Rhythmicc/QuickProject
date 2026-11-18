from __future__ import annotations

import os
import signal
from typing import Any, Callable
from rich.console import Console
from .i18n import _lang

console = Console()


class Status:
    """Rich console status spinner wrapper supporting both context manager and direct call updates."""

    def __init__(
        self,
        status_text: str = "",
        *,
        spinner: str = "dots",
        spinner_style: str = "status.spinner",
        speed: float = 1.0,
        refresh_per_second: float = 12.5,
    ) -> None:
        self._status = console.status(
            status_text,
            spinner=spinner,
            spinner_style=spinner_style,
            speed=speed,
            refresh_per_second=refresh_per_second,
        )
        self.started = False

    def __call__(
        self,
        status_text: str,
        *,
        spinner: str = "dots",
        spinner_style: str = "status.spinner",
        speed: float = 1.0,
    ) -> Status:
        self.update(
            status_text,
            spinner=spinner,
            spinner_style=spinner_style,
            speed=speed,
        )
        return self

    def update(
        self,
        status_text: str,
        *,
        spinner: str = "dots",
        spinner_style: str = "status.spinner",
        speed: float = 1.0,
    ) -> None:
        self._status.update(
            status_text,
            spinner=spinner,
            spinner_style=spinner_style,
            speed=speed,
        )

    def __enter__(self) -> Status:
        self.start()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.stop()

    def start(self) -> None:
        if not self.started:
            self._status.start()
            self.started = True

    def stop(self) -> None:
        if self.started:
            self._status.stop()
            self.started = False

    @property
    def status(self) -> bool:
        return self.started


status = Status("")

err_str = f'[bold red][{_lang["error"]}][/]'
info_str = f'[bold cyan][{_lang["information"]}][/]'
warn_str = f'[bold yellow][{_lang["warning"]}][/]'

# Compatibility aliases
VeyoDefaultConsole = console
VeyoDefaultStatus = status
VeyoErrorString = err_str
VeyoInfoString = info_str
VeyoWarnString = warn_str

VeyaDefaultConsole = console
VeyaDefaultStatus = status
VeyaErrorString = err_str
VeyaInfoString = info_str
VeyaWarnString = warn_str

QproDefaultConsole = console
QproDefaultStatus = status
QproErrorString = err_str
QproInfoString = info_str
QproWarnString = warn_str


def set_timeout(num: int) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Timeout function decorator (in seconds).
    Returns None if execution exceeds `num` seconds.
    """
    if not isinstance(num, int) or num <= 0:
        raise ValueError("num must be a positive integer")

    def wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
        def handle(signum: int, frame: Any) -> None:
            raise TimeoutError

        def run(*args: Any, **kwargs: Any) -> Any:
            if not hasattr(signal, "SIGALRM"):
                return func(*args, **kwargs)
            prev_handler = signal.getsignal(signal.SIGALRM)
            try:
                signal.signal(signal.SIGALRM, handle)
                signal.alarm(num)
                return func(*args, **kwargs)
            except TimeoutError:
                return None
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, prev_handler)

        return run

    return wrapper


def ask(question: dict[str, Any], timeout: int = 0, qmark: str = "?") -> Any:
    """
    Prompt the user interactively in the terminal using `inquirer_rhy`.
    Automatically pauses and resumes the active `status` spinner if running.

    :param question: Question dictionary (`type`, `message`, `choices`, `default`, etc.)
    :param timeout: Optional timeout in seconds; returns `question.get("default")` on timeout
    :param qmark: Prompt prefix mark
    """
    from inquirer_rhy.prompt import prompt

    q = dict(question)
    q.setdefault("name", "NoName")
    record_status = status.status
    interrupt_msg = _lang["UserInterrupt"]

    if timeout:

        @set_timeout(timeout)
        def _do_ask() -> Any:
            return prompt(
                q,
                keyboard_interrupt_msg=interrupt_msg,
                qmark=qmark,
            )[q["name"]]

        status.stop()
        try:
            res = _do_ask()
            if res is None:
                os.system("stty echo 2>/dev/null")
                return q.get("default", None)
            return res
        except Exception:
            os.system("stty echo 2>/dev/null")
            return q.get("default", None)
        finally:
            if record_status:
                status.start()
    else:
        status.stop()
        try:
            return prompt(
                q,
                keyboard_interrupt_msg=interrupt_msg,
                qmark=qmark,
            )[q["name"]]
        except Exception as e:
            console.print(repr(e))
            return None
        finally:
            if record_status:
                status.start()


_ask = ask
