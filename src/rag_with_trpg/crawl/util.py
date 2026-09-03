import shutil
from pathlib import Path


def clear_dir(path: Path) -> None:
    if not path.is_dir():
        return

    for child in path.iterdir():
        if child.is_dir() and not child.is_symlink():
            shutil.rmtree(child)
        else:
            child.unlink()
