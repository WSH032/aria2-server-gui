<!-- The content will be also use in `docs/CONTRIBUTING/CONTRIBUTING.md` by `pymdownx.snippets` -->
<!-- Do not use any **relative link** and  **GitHub-specific syntax** ！-->
<!-- Do not rename or move the file -->

# Contributing

> The guide is modified from [mkdocstrings](https://mkdocstrings.github.io/contributing/#contributing)

Contributions are welcome, and they are greatly appreciated! Every little bit helps, and credit will always be given.

## Environment setup

First, `fork` and `clone` the repository, then `cd` to the directory.

We use [`hatch`](https://github.com/pypa/hatch) and [`pre-commit`](https://pre-commit.com/) to manage our project.

You can install them with:

```shell
# https://pypa.github.io/pipx/
python3 -m pip install --user pipx

pipx install hatch
pipx install pre-commit
```

!!! note
    check `requirements.txt` to know the version of `hatch` and `pre-commit` we use.

Then, initialize the env with:

```shell
# https://hatch.pypa.io/latest/environment/
# IMPORTANT: Create hatch venv before running pre-commit
hatch env create default
hatch env create fmt
hatch env create docs

# IMPORTANT: init pyright-python before running pre-commit
#     issue: https://github.com/RobertCraigie/pyright-python/issues/200
hatch run default:pyright --help

# Init pre-commit
# https://pre-commit.com/#3-install-the-git-hook-scripts
pre-commit install
pre-commit run --all-files

# enter the dev environment
hatch shell default
```

That's all! Now, you can start to develop.

## Code style

The source code is in `src/`

We use [Ruff](https://github.com/astral-sh/ruff), [Pyright](https://github.com/Microsoft/pyright/)
 and [Codespell](https://github.com/codespell-project/codespell) to format, lint our code and type check.

Please check `pyproject.toml` to know our style.

If you want to format your code, you can use the following command:

```shell
hatch run fmt:fmt
hatch run fmt:spell-fix
```

or, dry run to check:

```shell
hatch run fmt:fmt-check
```

If you want to perform type checking, you can use the following command:

```shell
hatch run type-check
```

!!! tip
    If you use `VSCode`, we strongly recommend you to install the extensions in `.vscode/extensions.json`.<br>
    Because our code style rules are quite strict.<br>
    These extensions can help you know where need to be fixed when coding.

## Testing

We use [pytest](https://docs.pytest.org/en/stable/) to test our code.

The test source code is in `tests/`

You can run the testing with:

```shell
hatch run test
```

## Documentation

We use [mkdocs](https://www.mkdocs.org), [mkdocs-material](https://squidfunk.github.io/mkdocs-material), [mkdocstrings](https://mkdocstrings.github.io) to build our documentation.

The documentation source code is in `docs/`, `mkdocs.yml`,
 may be there is also some source code in `scripts/` or somewhere (check `mkdocs.yml` to find that).

Live-reloading docs:

```shell
hatch run docs:mkdocs serve
```

Build docs:

```shell
hatch run docs:build
```

### mkdocs reference

!!! tip

    - [mkdocs/getting-started](https://www.mkdocs.org/getting-started/)
    - [mkdocs-material/getting-started](https://squidfunk.github.io/mkdocs-material/getting-started/)

### Code Docstring styles

!!! warning

    We use `Google` style to write docstrings, please refer to

      - [mkdocstrings-python's documentation](https://mkdocstrings.github.io/python/usage/docstrings/google/)
      - [Napoleon's documentation](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html)
      - [Griffe's documentation](https://mkdocstrings.github.io/griffe/docstrings/)

## PR

- PRs should target the `main` branch.
- Keep branches up to date by `rebase` before merging.
- Do not add multiple unrelated things in same PR.
- Do not submit PRs where you just take existing lines and reformat them without changing what they do.
- Do not change other parts of the code that are not yours for formatting reasons.
- Do not use your clone's main branch to make a PR - create a branch and PR that.

### Edit `CHANGELOG.md`

If you have made the corresponding changes, please record them in `CHANGELOG.md`.

### Commit message convention

Commit messages must follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/),
or, `pre-commit` may be reject your commit.

!!! info
    If you don't know how to finish these, it's okay, feel free to initiate a PR, I will help you continue.

## More

There may still be some useful commands in `pyproject.toml`, you can refer to [hatch/environment/scripts](https://hatch.pypa.io/latest/config/environment/overview/#scripts) to use them.

!!! info
    If you find that the commands given in the above examples are incorrect, please open an issue, we greatly appreciate it.

---

## 😢

!!! warning
    The following 👇 content is for the maintainers of this project, may be you don't need to read it.

---

## deploy-docs

please refer to `.github/workflows/docs.yml`

## CI: lint-test

please refer to `.github/workflows/lint-test.yml`

## Publish and Release 🚀

**^^First, check-out to a new branch, edit `CHANGELOG.md` to record the changes.^^**

Then, please refer to:

- `.github/workflows/publish.yml`
- <https://github.com/frankie567/hatch-regex-commit>
- <https://hatch.pypa.io/latest/version/#updating>

Update version in **^^new branch^^** with:

```shell
git add .
hatch version {new_version}
```

It will create a commit and tag automatically.

Then, push the **new branch** with **tag** to GitHub, and create a PR to `main` branch.

!!! warning
    The `bump version` PR must have **only one commit with the corresponding tag**; otherwise, it will be rejected.

Review the PR, if it's ok, **rebase** it to `main` branch **^^in local^^**

!!! warning
    **DO NOT rebase with tag in GitHub**, refer to <https://docs.github.com/zh/authentication/managing-commit-signature-verification/about-commit-signature-verification#signature-verification-for-rebase-and-merge>

Check if everything is ok, for example:

- **check if the tag is on the `main` branch**.
- check if the link in `CHANGELOG.md` is correct.

If so, make a `approve` in environment `pypi` for the workflow.

After that, the `publish.yml` workflow will build and publish the package to PyPI.

Finally, edit the `draft release` created by `publish.yml` workflow, and publish the release.

!!! warning
    The creating of tag needs signature verification,<br>
    please refer to <https://docs.github.com/en/authentication/managing-commit-signature-verification/about-commit-signature-verification>
