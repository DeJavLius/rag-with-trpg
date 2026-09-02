import os
import time
from pathlib import Path
from dotenv import load_dotenv

import httpx
from bs4 import BeautifulSoup
from urllib.parse import quote

_ROOT = Path(__file__).resolve().parents[2]

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

def main():
  load_dotenv(_ROOT / ".env.shared")
  dw_site_url = os.getenv("DW_SITE")
  url_prev_keyword = os.getenv("URL_KEYWORD")
  base_path = os.getenv("CORPORA_DUNGEONWORLD_PATH") + "raw"
  file_path = Path(base_path)
  file_path.mkdir(parents=True, exist_ok=True)

  home_html = fetch(dw_site_url + quote(url_prev_keyword))
  links = enroll_all_links(home_html, url_prev_keyword)

  html_files: dict[str, str] = dict()
  for link in links:
    file_name = link.replace(url_prev_keyword, "").removesuffix("/")

    if html_files.get(file_name, None) is None:
      page_html = fetch(dw_site_url + quote(link))
      html_files[file_name] = page_html
      time.sleep(1)

  for name, page in html_files.items():
    new_page_path= file_path / f"{name.replace("-", "")}.html"
    new_page_path.parent.mkdir(parents=True, exist_ok=True)
    new_page_path.write_text(page, encoding="utf-8")
    print(f"저장 확인: 파일명: {name} 위치: {new_page_path}")

if __name__ == "__main__":
  main()