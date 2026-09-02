from pathlib import Path
from bs4 import BeautifulSoup
from markdownify import markdownify

from rag_with_trpg.crawl.config import CrawlConfig

SITE_TITLE_SEP = " - "

def converter(config: CrawlConfig, raw_files: list[Path], md_files: list[Path]):
  if len(md_files) == 0:
    extracting(config, raw_files)
  print(content_evaluate(config, md_files))

def extracting(config: CrawlConfig, raw_files: list[Path]):
  config.md_path.mkdir(parents=True, exist_ok=True)

  for raw in raw_files:
    html = raw.read_text(encoding="utf-8")
    title, content = extract(html)
    # print(f"title: {title}, content: {content}")
    new_page_path = config.md_path / f"{title}.md"
    new_page_path.parent.mkdir(parents=True, exist_ok=True)
    new_page_path.write_text(content, encoding="utf-8")
    print(f"저장 확인 - 파일명: {title} 위치: {new_page_path}")

def content_evaluate(config: CrawlConfig, md_files: list[Path]):
  result: list[str] = []
  for md in md_files:
    content = md.read_text(encoding="utf-8")
    if is_index_page(content):
      result.append(md.name)
  return result

def extract(html: str) -> tuple[str, str]:
  soup = BeautifulSoup(html, 'html.parser')
  title: str = title_decision(soup)
  contents = soup.find_all('section')

  result: str = "".join(
    markdownify(str(section), heading_style="ATX") + "\n"
      for section in contents
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
