from pathlib import Path

from bs4 import BeautifulSoup
from markdownify import markdownify as md

from rag_with_trpg.crawl.config import CrawlConfig
from rag_with_trpg.crawl.util import clear_dir, save_file

SITE_TITLE_SEP = " - "


def converter(config: CrawlConfig, raw_files: list[Path], md_files: list[Path]):
    if not len(md_files) > 0 or config.re_create:
        clear_dir(config.md_path)
        extracting(config, raw_files)


def extracting(config: CrawlConfig, raw_files: list[Path]):
    config.md_path.mkdir(parents=True, exist_ok=True)

    for raw in raw_files:
        html = raw.read_text(encoding="utf-8")
        title, content = extract(html)

        if not is_index_page(content):
            # print(f"title: {title}, content: {content}")
            save_file(title, config.md_path / f"{title}.md", content)
        else:
            print(f"미저장 인덱싱 파일: {title}, {len(content)}")


def extract(html: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    title: str = title_decision(soup)
    contents = soup.find_all("section")

    indexed_content: list[str] = []
    for content in contents:
        indexed_content.append(str(content))

    result: str = "".join(
        md(str(section), heading_style="ATX", strip=["a", "img"]).replace("\xa0", " ")
        + "\n"
        for section in indexed_content
    )

    return title, result


def title_decision(soup: BeautifulSoup) -> str:
    if soup.title is None:
        return "_"

    title = soup.title.get_text(strip=True)
    _, sep, page = title.partition(SITE_TITLE_SEP)

    return page.strip() if sep else title


def is_index_page(markdown: str) -> bool:
    return len(markdown) < 500
