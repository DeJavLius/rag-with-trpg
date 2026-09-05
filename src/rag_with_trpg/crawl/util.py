import shutil
from pathlib import Path

from bs4 import BeautifulSoup

HEAD_SECTIONS: str = "###### "
SITE_TITLE_SEP = " - "


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


def title_decision(soup: BeautifulSoup) -> str:
    if soup.title is None:
        return "_"

    title = soup.title.get_text(strip=True)
    _, sep, page = title.partition(SITE_TITLE_SEP)

    return page.strip() if sep else title


def md_head_counter(path: Path) -> tuple[str, int, list[int]]:
    title = path.stem
    markdown = path.read_text(encoding="utf-8")
    md_total, md_head_count = header_counting(markdown)
    return title, md_total, md_head_count


def header_counting(content: str) -> tuple[int, list[int]]:
    total = len(content)

    head_count: list[int] = [0 for _ in range(6)]
    for h in range(6):
        header = HEAD_SECTIONS[h:]
        head_count[5 - h] = content.count(header)
        content = content.replace(header, "")

    return total, head_count


def serialize(values: list) -> str:
    return "".join([f"h{i + 1}: ({v}) " if v > 0 else "" for i, v in enumerate(values)])


def find_file(path_list: list[Path], keyword: str) -> Path | None:
    for p in path_list:
        if p.stem == keyword:
            return p

    return None
