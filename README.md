<!-- The content will be also use in `docs/index.md` by `pymdownx.snippets` -->
<!-- Do not use any **relative link** and  **GitHub-specific syntax** ！-->
<!-- Do not rename or move the file -->

# pyproject-template

<p align="center">
    <em>Stubborn python project scaffold</em>  <!-- EDIT -->
    <br>
    <em>固执己见的python项目手脚架</em>  <!-- EDIT -->
</p>

## 用法

1. 按照 `CONTRIBUTING.md` 初始化项目
2. 修改所有带有 `EDIT` 注释的地方
3. 将 `github仓库设置`，`环境变量机密`，`保护规则` 设置得和本仓库（`pyproject-template`）完全一致
4. 申请[codecov](https://app.codecov.io/gh/)和[pre-commit.ci](https://results.pre-commit.ci/)的BOT APP
5. 按照[pypa](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)的指南去 `pypi` 申请 `Trusted Publisher`
6. 同步个人的`VSCode`设置和扩展
7. 删掉本用法部分
8. Python，启动！✨

纯python打包参考 <https://github.com/WSH032/fastapi-proxy-lib>
带有不同平台的二进制依赖打包参考 <https://github.com/WSH032/aria2-wheel>

---

| | |
| - | - |
| CI/CD   | [![CI: lint-test]][CI: lint-test#link] [![pre-commit.ci status]][pre-commit.ci status#link] <br> [![CI: docs]][CI: docs#link] [![CI: publish]][CI: publish#link]  |
| Code    | [![codecov]][codecov#link] [![Code style: black]][Code style: black#link] [![Ruff]][Ruff#link] [![Checked with pyright]][Checked with pyright#link] |
| Package | [![PyPI - Version]][PyPI#link] [![PyPI - Downloads]][PyPI#link] [![PyPI - Python Version]][PyPI#link] |
| Meta    | [![Hatch project]][Hatch project#link] [![GitHub License]][GitHub License#link] |

---

Documentation: <https://wsh032.github.io/pyproject-template/>  <!-- EDIT -->

Source Code: <https://github.com/WSH032/pyproject-template/>  <!-- EDIT -->

---

## development

- If you find any issues, please don't hesitate to [open an issue](https://github.com/WSH032/pyproject-template/issues).  <!-- EDIT: repo name -->
- If you need assistance, feel free to [start a discussion](https://github.com/WSH032/pyproject-template/discussions).  <!-- EDIT: repo name -->
- Follow our `CONTRIBUTING.md`, [PR Welcome!](https://github.com/WSH032/pyproject-template/pulls)  <!-- EDIT: repo name -->
- Security 😰❗: We value any security vulnerabilities, [please report to us privately](https://github.com/WSH032/pyproject-template/security), pretty appreciated for that.  <!-- EDIT: repo name -->

English is not the native language of the author (me), so if you find any areas for improvement in the documentation, your feedback is welcome.

If you think this project helpful, consider giving it a star ![GitHub Repo stars](https://img.shields.io/github/stars/wsh032/pyproject-template?style=social), which makes me happy. :smile:  <!-- EDIT: repo name -->

<!-- link -->

<!-- ci/cd -->
<!-- EDIT: repo name  👇 -->
[CI: lint-test]: https://github.com/WSH032/pyproject-template/actions/workflows/lint-test.yml/badge.svg
[CI: lint-test#link]: https://github.com/WSH032/pyproject-template/actions/workflows/lint-test.yml
[CI: docs]: https://github.com/WSH032/pyproject-template/actions/workflows/docs.yml/badge.svg
[CI: docs#link]: https://github.com/WSH032/pyproject-template/actions/workflows/docs.yml
[CI: publish]: https://github.com/WSH032/pyproject-template/actions/workflows/publish.yml/badge.svg
[CI: publish#link]: https://github.com/WSH032/pyproject-template/actions/workflows/publish.yml
[pre-commit.ci status]: https://results.pre-commit.ci/badge/github/WSH032/pyproject-template/main.svg
[pre-commit.ci status#link]: https://results.pre-commit.ci/latest/github/WSH032/pyproject-template/main
<!-- EDIT: repo name 👆 -->
<!-- code -->
[Code style: black]: https://img.shields.io/badge/code%20style-black-000000.svg
[Code style: black#link]: https://github.com/psf/black
<!-- EDIT: repo name --> [GitHub License]: https://img.shields.io/github/license/WSH032/pyproject-template?color=9400d3
<!-- EDIT: repo name --> [GitHub License#link]: https://github.com/WSH032/pyproject-template/blob/main/LICENSE
[Ruff]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
[Ruff#link]: https://github.com/astral-sh/ruff
[Checked with pyright]: https://microsoft.github.io/pyright/img/pyright_badge.svg
[Checked with pyright#link]: https://microsoft.github.io/pyright
<!-- package -->
<!-- EDIT: repo name  👇 -->
[PyPI - Version]: https://img.shields.io/pypi/v/<EDIT>?logo=pypi&label=PyPI&logoColor=gold
[PyPI - Downloads]: https://img.shields.io/pypi/dm/<EDIT>?color=blue&label=Downloads&logo=pypi&logoColor=gold
[PyPI - Python Version]: https://img.shields.io/pypi/pyversions/<EDIT>?logo=python&label=Python&logoColor=gold
[PyPI#link]: https://pypi.org/project/<EDIT>
<!-- EDIT: repo name 👆 -->
<!-- meta -->
[Hatch project]: https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg
[Hatch project#link]: https://github.com/pypa/hatch
<!-- EDIT: repo name --> [codecov]: https://codecov.io/gh/WSH032/pyproject-template/graph/badge.svg?token=62QQU06E8X
<!-- EDIT: repo name --> [codecov#link]: https://codecov.io/gh/WSH032/pyproject-template
