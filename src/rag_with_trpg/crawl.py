import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

import httpx
from bs4 import BeautifulSoup

from .config import load_config, require_env, require_path


@dataclass(frozen=True)
class CrawlConfig:
  site_url: str
  url_keyword: str
  raw_path: Path

  @classmethod
  def from_env(cls) -> "CrawlConfig":
    return cls(
      site_url=require_env("DW_SITE").rstrip("/"),
      url_keyword=require_env("URL_KEYWORD"),
      raw_path=require_path("CORPORA_DUNGEONWORLD_PATH", "raw"),
    )

def fetch(url: str) -> str:
  r = httpx.get(url, follow_redirects=True, timeout=5)
  return r.text

def enroll_all_links(home_html: str, target_url: str) -> list[str]:
  soup = BeautifulSoup(home_html, 'html.parser')
  links = [a['href'] for a in soup.find_all('a', href=True)]
  endpoints = sorted(set(l for l in links if l.startswith(target_url)))
  return endpoints

def extract(html: str) -> tuple[str, str]:
  return html

def is_indexed_page(markdown: str) -> bool:
  return False

def crawler_init(config: CrawlConfig):
  config.raw_path.mkdir(parents=True, exist_ok=True)

  home_html = fetch(config.site_url + quote(config.url_keyword))
  links = enroll_all_links(home_html, config.url_keyword)

  html_files: dict[str, str] = dict()
  for link in links:
    file_name = link.replace(config.url_keyword, "").removesuffix("/")

    if html_files.get(file_name, None) is None:
      page_html = fetch(config.site_url + quote(link))
      html_files[file_name] = page_html
      time.sleep(1)

  for name, page in html_files.items():
    new_page_path = config.raw_path / f"{name.replace("-", "")}.html"
    new_page_path.parent.mkdir(parents=True, exist_ok=True)
    new_page_path.write_text(page, encoding="utf-8")
    print(f"저장 확인: 파일명: {name} 위치: {new_page_path}")

def clear_dir(path: Path) -> None:
  if not path.is_dir():
    return

  for child in path.iterdir():
    if child.is_dir() and not child.is_symlink():
      shutil.rmtree(child)
    else:
      child.unlink()

def main():
  load_config()
  config = CrawlConfig.from_env()
  raw_files = list(config.raw_path.rglob("*.html"))

  crawler_restart_flag = len(raw_files) == 0
  if crawler_restart_flag:
    print(f"error: 수집 파일 없음, 최초 수집 시작: {config.raw_path}")
    crawler_init(config)
  else:
    for raw in raw_files:
      html = raw.read_text(encoding="utf-8")
      soup = BeautifulSoup(html, 'html.parser')
      wrong_check = soup.find_all("h1")

      if len(wrong_check) > 0:
        for w in wrong_check:
          if w.text == "404":
            print("error: 파일 중 잘못 크롤링된 파일이 있음. 전역 재수집 시작")
            crawler_restart_flag = True
            break
      else:
        print("error: 파일은 있으나 수집된 내용이 없음")
        crawler_restart_flag = True

    if crawler_restart_flag:
      clear_dir(config.raw_path)
      crawler_init(config)

if __name__ == "__main__":
  main()
