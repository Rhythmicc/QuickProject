from __future__ import annotations

import concurrent.futures
import os
import shutil
from subprocess import PIPE, Popen
from typing import Any
from .console import console, status


def remove(path: str | os.PathLike[str]) -> None:
    """Remove a file, symlink, or directory tree if it exists."""
    if os.path.islink(path) or os.path.isfile(path):
        os.remove(path)
    elif os.path.isdir(path):
        shutil.rmtree(path)


def external_exec(
    cmd: str,
    without_output: bool = False,
    without_stdout: bool = False,
    without_stderr: bool = False,
    __expose: bool = False,
    __no_wait: bool = False,
    __bypass: bool = False,
    cwd: str | os.PathLike[str] | None = None,
) -> tuple[int, str] | Popen[str]:
    """
    Execute an external shell command with concurrent streaming of stdout and stderr.

    :param cmd: Command string to execute
    :param without_output: Suppress all console output while still capturing output text
    :param without_stdout: Do not capture or print stdout
    :param without_stderr: Do not capture or print stderr
    :param __expose: Enable Rich protocol directives (__START__, __STOP__, __TITLE__, __RULE__, __MARKDOWN__, __EXECUTE__)
    :param __no_wait: Return the Popen process object immediately without waiting
    :param __bypass: Print raw lines directly via built-in print() instead of Rich console
    :param cwd: Optional working directory for the command
    :return: (return_code, combined_output) or Popen instance when __no_wait is True
    """
    if __expose:
        from rich.markdown import Markdown

    protocol_prefixes = (
        "__START__",
        "__STOP__",
        "__TITLE__",
        "__RULE__",
        "__MARKDOWN__",
        "__EXECUTE__",
    )

    def _drain(pipe: Any, content: list[str] | None, ignore_output: bool) -> None:
        for raw_line in iter(pipe.readline, ""):
            if content is not None:
                content.append(raw_line)
            line = raw_line.strip()
            if ignore_output:
                continue
            if __bypass:
                print(line, flush=True)
                continue
            if line.startswith(protocol_prefixes):
                if not __expose:
                    continue
                if line.startswith("__START__"):
                    status(line.replace("__START__", "", 1).strip()).start()
                elif line.startswith("__STOP__"):
                    status.stop()
                elif line.startswith("__TITLE__"):
                    console.print(Markdown("# " + line.replace("__TITLE__", "", 1).strip()))
                elif line.startswith("__RULE__"):
                    console.rule(line.replace("__RULE__", "", 1).strip())
                elif line.startswith("__MARKDOWN__"):
                    console.print(
                        Markdown(
                            line.replace("__MARKDOWN__", "", 1).replace("\\n", "\n").strip()
                        )
                    )
                elif line.startswith("__EXECUTE__"):
                    os.system(line.replace("__EXECUTE__", "", 1).strip())
            else:
                console.print(line)

    output_content: list[str] = []
    process = Popen(
        cmd,
        shell=True,
        stdout=PIPE,
        stderr=PIPE,
        bufsize=1,
        encoding="utf-8",
        errors="replace",
        cwd=cwd,
    )

    if __no_wait:
        return process

    try:
        with concurrent.futures.ThreadPoolExecutor(2) as executor:
            futures = [
                executor.submit(
                    _drain,
                    process.stdout,
                    None if without_stdout else output_content,
                    without_output or without_stdout,
                ),
                executor.submit(
                    _drain,
                    process.stderr,
                    None if without_stderr else output_content,
                    without_output or without_stderr,
                ),
            ]
            concurrent.futures.wait(futures)

        ret_code = process.wait()
        if process.stdout:
            process.stdout.close()
        if process.stderr:
            process.stderr.close()
        return ret_code, "".join(output_content)
    except KeyboardInterrupt:
        process.terminate()
        try:
            process.wait(timeout=3)
        except Exception:
            process.kill()
        if process.stdout:
            process.stdout.close()
        if process.stderr:
            process.stderr.close()
        raise
