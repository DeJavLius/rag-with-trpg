from pathlib import Path

from bs4 import BeautifulSoup
from markdownify import markdownify as md

from rag_with_trpg.crawl.config import CrawlConfig
from rag_with_trpg.crawl.meta_mapped import EXPECTED_EXCLUDED
from rag_with_trpg.crawl.util import clear_dir, save_file

SITE_TITLE_SEP = " - "


def converter(config: CrawlConfig, raw_files: list[Path], md_files: list[Path]):
    if not len(md_files) > 0 or config.re_create:
        clear_dir(config.md_path)
        extracting(config, raw_files)


def extracting(config: CrawlConfig, raw_files: list[Path]):
    config.md_path.mkdir(parents=True, exist_ok=True)

    exclude_titles: list[str] = []
    for raw in raw_files:
        html = raw.read_text(encoding="utf-8")
        title, content = extract(html)

        if not is_index_page(content):
            # print(f"title: {title}, content: {content}")
            save_file(title, config.md_path / f"{title}.md", content)
        else:
            exclude_titles.append(title)

    # D-04 「반드시 출력한다」 — 0건이어도 찍는다. 침묵하면 그게 곧 버그다.
    print(
        f"미 저장 파일 {len(exclude_titles)}건: "
        f"{"".join([f"{t}.md " for t in exclude_titles])}"
    )

    if len(exclude_titles) != EXPECTED_EXCLUDED:
        raise RuntimeError(
            f"인덱스 제외가 {len(exclude_titles)}건이다 (기대 {EXPECTED_EXCLUDED}건). "
            f"임계값보다 extract() 가 깨졌을 가능성을 먼저 본다 — D-04 · D-21 4번"
        )


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
