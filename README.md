# Veyo

> Formerly **QuickProject (`qpro`)** — distilled into a zero-config Python CLI framework and terminal toolkit.

**Veyo** turns plain Python functions into rich command-line applications and provides ergonomic primitives for subprocess streaming, terminal status spinners, and interactive prompts — with **zero import-time side effects** or configuration prompts.

---

## Features

- **`Commander`**: Decorator-driven CLI builder from Python function signatures, type annotations, default values, and `:param:` docstrings.
  - Automatic Rich help table generation (`app.help()`).
  - Pre-execution hooks (`app.bind_pre_call`), internal cross-command invocation (`app.real_call`), and command table composition (`app1 + app2`).
  - Built-in Zsh completion script generation (`<app> complete`).
- **`external_exec`**: Concurrent streaming execution of shell commands (`stdout` & `stderr`), with optional Rich UI protocol directives (`__START__`, `__STOP__`, `__TITLE__`, `__RULE__`, `__MARKDOWN__`).
- **Terminal & Interactive Primitives**:
  - `console` & `status`: Rich console and context-aware spinner (`with status("Working..."):` or `status("Updating...")`).
  - `ask`: Interactive terminal prompts (powered by `inquirer-rhy`) that automatically pause and resume active spinners and support timeout fallbacks.
  - `info_str`, `warn_str`, `err_str`: Ready-to-use Rich status prefixes with automatic `zh`/`en` locale detection.

---

## Installation

```bash
pip install veyo
# or with uv
uv add veyo
```

---

## Quick Start

### 1. Build a CLI App with `Commander`

```python
from veyo import Commander, console, info_str

app = Commander("my-tool")


@app.custom_complete("env")
def deploy():
    return ["dev", "staging", "prod"]


@app.command()
def deploy(env: str, tag: str = "latest", dry_run: bool = False):
    """
    Deploy service to target environment

    :param env: Target environment name
    :param tag: Image tag to deploy
    :param dry_run: Preview without executing
    """
    console.print(info_str, f"Deploying {tag} to {env} (dry_run={dry_run})")


if __name__ == "__main__":
    app()
```

Run your CLI:

```bash
python app.py                           # Prints Rich help table
python app.py deploy prod --tag v1.2.0  # Runs subcommand
python app.py complete                  # Generates complete/zsh/_my-tool
```

#### Advanced `Commander` Capabilities

- **Pre-call validation hook**:
  ```python
  def check_deploy(env: str, tag: str = "latest", dry_run: bool = False) -> bool:
      return env in {"dev", "staging", "prod"}

  app.bind_pre_call("deploy", check_deploy)
  ```
- **Call another subcommand internally**:
  ```python
  app.real_call("deploy", "staging", tag="v1.0.0")
  ```
- **Private parameters**: Parameters prefixed with `_` (e.g. `def cmd(name: str, _internal: bool = False)`) are omitted from CLI parsing and help tables, but can be passed via `app.real_call`.
- **Merge command apps**:
  ```python
  app = app_core + app_plugins
  ```

---

### 2. Stream Subprocesses with `external_exec`

```python
from veyo import external_exec, status

with status("Building package..."):
    code, output = external_exec("uv build", without_output=True)

# Stream output in real time
code, output = external_exec("pytest -q")

# Run in background without waiting (returns subprocess.Popen)
proc = external_exec("python -m http.server 8000", __no_wait=True)
```

---

### 3. Interactive Prompts & Spinner Coordination

```python
from veyo import ask, console, info_str, status

with status("Processing tasks...") as st:
    # Spinner automatically pauses while waiting for user input, then resumes!
    confirm = ask(
        {
            "type": "confirm",
            "message": "Continue to next step?",
            "default": True,
        },
        timeout=10,  # Falls back to default (True) after 10s of inactivity
    )
    st("Finishing up...")

console.print(info_str, f"User answered: {confirm}")
```

---

### 4. Language & Compatibility Aliases

Veyo detects `zh` or `en` automatically from `VEYO_LANG` / `LC_ALL` / `LANG` without creating config files or prompting on import. You can also switch it programmatically:

```python
from veyo import set_lang

set_lang("zh")  # or "en"
```

For backward compatibility with upper-level libraries built on `QuickProject`:
- `_ask` aliases `ask`
- `VeyoDefaultConsole` / `QproDefaultConsole` alias `console`
- `VeyoDefaultStatus` / `QproDefaultStatus` alias `status`
- `VeyoInfoString` / `QproInfoString`, `VeyoWarnString` / `QproWarnString`, `VeyoErrorString` / `QproErrorString` alias `info_str`, `warn_str`, `err_str`
