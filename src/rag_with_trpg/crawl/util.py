import shutil
from pathlib import Path


def save_file(file_name: str, path: Path, content: str):
    print(f"저장 확인 - 파일명: {file_name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def clear_dir(path: Path) -> None:
    if not path.is_dir():
        return

    for child in path.iterdir():
        if child.is_dir() and not child.is_symlink():
            shutil.rmtree(child)
        else:
            child.unlink()
