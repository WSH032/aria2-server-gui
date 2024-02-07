# pyright: basic

"""Generate the code reference pages and navigation.

Copy form: https://mkdocstrings.github.io/recipes/

NOTE: Keep the following directory structure:

📁 repo/
├── 📁 docs/
│   └── 📄 index.md
├── 📁 scripts/
│   └── 📄 gen_ref_pages.py
├── 📁 src/
│   └── 📁 project/
└── 📄 mkdocs.yml
"""

import re
from pathlib import Path

import mkdocs_gen_files  # pyright: ignore[reportMissingImports]

nav = mkdocs_gen_files.Nav()

SRC = Path(__file__).parent.parent / "src"
INDEX_MD_NAME = "index.md"

# matches strings that start with an underscore followed by any character except another underscore.
# exclude: _private
# include: hello, __hello, or __hello__
# see: https://mkdocstrings.github.io/python/usage/configuration/members/#filters
EXCLUDE_PATTERN = re.compile(r"^_[^_]")


for path in sorted(SRC.rglob("*.py")):
    module_path = path.relative_to(SRC).with_suffix("")
    doc_path = path.relative_to(SRC).with_suffix(".md")
    # Don't change the name "reference"
    # It's used in mkdocs.yml
    full_doc_path = Path("reference", doc_path)

    parts = tuple(module_path.parts)

    # TODO: optimize the performance of this part.
    # exclude private packages.
    # parts[0] is the top-level package, so we don't apply the pattern to it.
    # parts[-1] is the `.py` file (i.e., a module, not a package), so we don't apply the pattern to it.
    if any(EXCLUDE_PATTERN.search(part) for part in parts[1:-1]):
        continue

    if parts[-1] == "__init__":
        parts = parts[:-1]
        doc_path = doc_path.with_name(INDEX_MD_NAME)
        full_doc_path = full_doc_path.with_name(INDEX_MD_NAME)
    # exclude private modules
    elif EXCLUDE_PATTERN.search(parts[-1]):
        continue

    nav[parts] = doc_path.as_posix()

    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        ident = ".".join(parts)
        fd.writelines(f"::: {ident}")

    mkdocs_gen_files.set_edit_path(full_doc_path, Path("../") / path)

# Don't change the name "reference/SUMMARY.md"
# It's used in mkdocs.yml
with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
