# QuickProject

> Do you know how to write Python functions?

Yes!

> Then you now know how to build command-line applications!

## [Docs](https://qpro-doc.rhythm.icu/)

## 构建与发布

- 使用 [uv](https://github.com/astral-sh/uv) 进行本地构建：

  ```bash
  uv run --with build python -m build
  ```

- 推送形如 `v*` 的标签或手动触发 GitHub Actions 工作流，即可自动构建并发布到 PyPI。记得在仓库的 `PYPI_API_TOKEN` 机密中配置 PyPI 的发布令牌。
