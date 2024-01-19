"""Static files."""

from pathlib import Path

__all__ = ("aria_ng_static_files", "favicon")

_here = Path(__file__).parent


aria_ng_static_files: Path = _here / "AriaNg"
assert aria_ng_static_files.is_dir(), f"Directory {aria_ng_static_files} does not exist"

favicon: Path = _here / "rocket-24.svg"
assert favicon.is_file(), f"Favicon {favicon} does not exist"
