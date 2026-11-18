from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

import veyo
from veyo import (
    Commander,
    QproDefaultConsole,
    QproDefaultStatus,
    VeyoDefaultConsole,
    VeyoDefaultStatus,
    _ask,
    ask,
    console,
    err_str,
    external_exec,
    get_lang,
    info_str,
    remove,
    set_lang,
    set_timeout,
    status,
    warn_str,
)


class TestVeyoCore(unittest.TestCase):
    def test_exports_and_aliases(self) -> None:
        self.assertIs(console, VeyoDefaultConsole)
        self.assertIs(console, QproDefaultConsole)
        self.assertIs(status, VeyoDefaultStatus)
        self.assertIs(status, QproDefaultStatus)
        self.assertIs(ask, _ask)
        self.assertIn("[", info_str)
        self.assertIn("[", warn_str)
        self.assertIn("[", err_str)

    def test_i18n_switch(self) -> None:
        orig = get_lang()
        try:
            set_lang("zh")
            self.assertEqual(get_lang(), "zh")
            self.assertEqual(veyo._lang["SubCommand"], "子命令")
            set_lang("en")
            self.assertEqual(get_lang(), "en")
            self.assertEqual(veyo._lang["SubCommand"], "Subcommand")
        finally:
            set_lang(orig)

    def test_commander_dispatch_and_hooks(self) -> None:
        app = Commander("demo", custom_complete=True)
        calls: list[tuple[str, int, bool, str]] = []

        @app.command()
        def greet_user(
            user_name: str,
            repeat: int = 1,
            loud: bool = False,
            _secret: str = "internal",
        ) -> str:
            """
            Greet a user

            :param user_name: Name of the user
            :param repeat: Repeat count
            :param loud: Uppercase output
            """
            msg = user_name.upper() if loud else user_name
            calls.append((msg, repeat, loud, _secret))
            return f"{msg}:{repeat}:{_secret}"

        res = app(["greet-user", "alice", "--repeat", "3", "--loud"])
        self.assertEqual(res, "ALICE:3:internal")
        self.assertEqual(calls[-1], ("ALICE", 3, True, "internal"))

        res2 = app.real_call("greet_user", "bob", 2, False, "custom_secret")
        self.assertEqual(res2, "bob:2:custom_secret")

        app.bind_pre_call(
            "greet_user",
            lambda user_name, repeat=1, loud=False: user_name != "blocked",
        )
        res_blocked = app(["greet-user", "blocked"])
        self.assertIsNone(res_blocked)
        self.assertEqual(len(calls), 2)

    def test_commander_merge_and_completion(self) -> None:
        app1 = Commander("merged-cli", custom_complete=True)
        app2 = Commander("sub", custom_complete=True)

        @app1.custom_complete("target")
        def deploy():
            return ["dev", {"name": "prod", "description": "Production"}]

        @app1.command()
        def deploy(target: str) -> str:
            """Deploy target"""
            return target

        @app2.command()
        def ping() -> str:
            """Ping check"""
            return "pong"

        merged = app1 + app2
        self.assertEqual(merged(["deploy", "prod"]), "prod")
        self.assertEqual(merged(["ping"]), "pong")

        with tempfile.TemporaryDirectory() as tmpdir:
            prev = os.getcwd()
            os.chdir(tmpdir)
            try:
                merged.generate_complete(is_script=True)
                zsh_file = Path(tmpdir) / "complete" / "zsh" / "_merged-cli"
                rc_file = Path(tmpdir) / ".merged-clirc"
                self.assertTrue(zsh_file.exists())
                self.assertTrue(rc_file.exists())
                content = zsh_file.read_text(encoding="utf-8")
                self.assertIn("#compdef merged-cli", content)
                self.assertIn("deploy:'Deploy target'", content)
                self.assertIn("prod:'Production'", content)
            finally:
                os.chdir(prev)

    def test_external_exec_and_remove(self) -> None:
        code, out = external_exec("printf 'hello\\nworld\\n'", without_output=True)
        self.assertEqual(code, 0)
        self.assertEqual(out.strip().splitlines(), ["hello", "world"])

        with tempfile.TemporaryDirectory() as tmpdir:
            target_dir = Path(tmpdir) / "nested" / "dir"
            target_dir.mkdir(parents=True)
            (target_dir / "file.txt").write_text("data", encoding="utf-8")
            remove(Path(tmpdir) / "nested")
            self.assertFalse((Path(tmpdir) / "nested").exists())

    def test_set_timeout(self) -> None:
        import time

        @set_timeout(1)
        def slow() -> str:
            time.sleep(2)
            return "done"

        @set_timeout(2)
        def fast() -> str:
            return "ok"

        self.assertEqual(fast(), "ok")
        self.assertIsNone(slow())


if __name__ == "__main__":
    unittest.main()
