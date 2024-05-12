<!-- The content will be also use in `docs/index.md` by `pymdownx.snippets` -->
<!-- Do not use any **relative link** and  **GitHub-specific syntax** ！-->
<!-- Do not rename or move the file -->

# aria2-server-gui

<p align="center">
    <em>aria2 server with gui, python/desktop/remote downloader</em>
    <br>
    <em>带有GUI的aria2服务器，可作为 python/桌面/远程 下载器</em>
</p>


!!! warning

    This repo is a work in progress...

> [!WARNING]
>
> Due to time constraints, I have decided to halt the development of this project. Originally, I intended to create a remote Python downloader, but it turns out that using Python for GUI development is not a good approach.
>
> The project currently has a demo version available for use. Please refer to the following instructions to use it.
>
> If needed, feel free to fork this project.
>
> Alternative projects that can be used instead: [aria2p](https://github.com/pawamoy/aria2p), [persepolis](https://github.com/persepolisdm/persepolis).

## Features

A remote downloader with account management and login system.

- Frontend: `nicegui` and `AriaNg`.
- Backend: `aria2`, `FastAPI`, and `uvicorn`.
- Database management: `alembic` and `sqlalchemy`.
- Login system management: `fastapi-user`.
- CLI program: `typer`.

Additionally, it includes an SSL self-signed certificate generator `src/aria2_server/cli/utils/mkcert.py`

## Usage

```bash
git clone https://github.com/WSH032/aria2-server-gui.git
cd aria2-server-gui
python -m pip install -e .

aria2-server --help
```

---

| | |
| - | - |
| CI/CD   | [![CI: lint-test]][CI: lint-test#link] [![pre-commit.ci status]][pre-commit.ci status#link] <br> [![CI: docs]][CI: docs#link] [![CI: publish]][CI: publish#link]  |
| Code    | [![codecov]][codecov#link] [![Code style: black]][Code style: black#link] [![Ruff]][Ruff#link] [![Checked with pyright]][Checked with pyright#link] |
| Package | [![PyPI - Version]][PyPI#link] [![PyPI - Downloads]][PyPI#link] [![PyPI - Python Version]][PyPI#link] |
| Meta    | [![Hatch project]][Hatch project#link] [![GitHub License]][GitHub License#link] |

---

Documentation: <https://wsh032.github.io/aria2-server-gui/>

Source Code: <https://github.com/WSH032/aria2-server-gui/>

---

## development

- If you find any issues, please don't hesitate to [open an issue](https://github.com/WSH032/aria2-server-gui/issues).
- If you need assistance, feel free to [start a discussion](https://github.com/WSH032/aria2-server-gui/discussions).
- Follow our `CONTRIBUTING.md`, [PR Welcome!](https://github.com/WSH032/aria2-server-gui/pulls)
- Security 😰❗: We value any security vulnerabilities, [please report to us privately](https://github.com/WSH032/aria2-server-gui/security), pretty appreciated for that.

English is not the native language of the author (me), so if you find any areas for improvement in the documentation, your feedback is welcome.

If you think this project helpful, consider giving it a star ![GitHub Repo stars](https://img.shields.io/github/stars/wsh032/aria2-server-gui?style=social), which makes me happy. :smile:

---

<details>

<summary>for develeoper</summary>

1. 修改所有带有 `EDIT` 注释的地方
2. 按照[pypa](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)的指南去 `pypi` 申请 `Trusted Publisher`
3. 删掉本用法部分

纯python打包参考 <https://github.com/WSH032/fastapi-proxy-lib>
带有不同平台的二进制依赖打包参考 <https://github.com/WSH032/aria2-wheel>

</details>

<!-- link -->

<!-- ci/cd -->
[CI: lint-test]: https://github.com/WSH032/aria2-server-gui/actions/workflows/lint-test.yml/badge.svg
[CI: lint-test#link]: https://github.com/WSH032/aria2-server-gui/actions/workflows/lint-test.yml
[CI: docs]: https://github.com/WSH032/aria2-server-gui/actions/workflows/docs.yml/badge.svg
[CI: docs#link]: https://github.com/WSH032/aria2-server-gui/actions/workflows/docs.yml
[CI: publish]: https://github.com/WSH032/aria2-server-gui/actions/workflows/publish.yml/badge.svg
[CI: publish#link]: https://github.com/WSH032/aria2-server-gui/actions/workflows/publish.yml
[pre-commit.ci status]: https://results.pre-commit.ci/badge/github/WSH032/aria2-server-gui/main.svg
[pre-commit.ci status#link]: https://results.pre-commit.ci/latest/github/WSH032/aria2-server-gui/main
<!-- code -->
[Code style: black]: https://img.shields.io/badge/code%20style-black-000000.svg
[Code style: black#link]: https://github.com/psf/black
[GitHub License]: https://img.shields.io/github/license/WSH032/aria2-server-gui?color=9400d3
[GitHub License#link]: https://github.com/WSH032/aria2-server-gui/blob/main/LICENSE
[Ruff]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
[Ruff#link]: https://github.com/astral-sh/ruff
[Checked with pyright]: https://microsoft.github.io/pyright/img/pyright_badge.svg
[Checked with pyright#link]: https://microsoft.github.io/pyright
<!-- package -->
[PyPI - Version]: https://img.shields.io/pypi/v/aria2-server?logo=pypi&label=PyPI&logoColor=gold
[PyPI - Downloads]: https://img.shields.io/pypi/dm/aria2-server?color=blue&label=Downloads&logo=pypi&logoColor=gold
[PyPI - Python Version]: https://img.shields.io/pypi/pyversions/aria2-server?logo=python&label=Python&logoColor=gold
[PyPI#link]: https://pypi.org/project/aria2-server
<!-- meta -->
[Hatch project]: https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg
[Hatch project#link]: https://github.com/pypa/hatch
[codecov]: https://codecov.io/gh/WSH032/aria2-server-gui/graph/badge.svg?token=62QQU06E8X
[codecov#link]: https://codecov.io/gh/WSH032/aria2-server-gui
