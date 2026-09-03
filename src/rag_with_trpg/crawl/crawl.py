import time
from pathlib import Path
from urllib.parse import quote

import httpx
from bs4 import BeautifulSoup

from rag_with_trpg.crawl.config import CrawlConfig
from rag_with_trpg.crawl.util import clear_dir


def crawler(config: CrawlConfig, raw_files: list[Path]):
    crawler_restart_flag = len(raw_files) == 0 or config.re_crawl
    if crawler_restart_flag:
        print(
            f"initial: {'재수집 수행' if config.re_crawl else '수집 파일 없음'}, 최초 수집 시작: {config.raw_path}"
        )
        target_crawl(config)
    else:
        for raw in raw_files:
            html = raw.read_text(encoding="utf-8")
            soup = BeautifulSoup(html, "html.parser")
            wrong_check = soup.find_all("h1")

            if len(wrong_check) > 0:
                for w in wrong_check:
                    if w.text == "404":
                        print(
                            "wrong crawl: 파일 중 잘못 크롤링된 파일이 있음. 전역 재수집 시작"
                        )
                        crawler_restart_flag = True
                        break
            else:
                print("empty content: 파일은 있으나 수집된 내용이 없음")
                crawler_restart_flag = True

        if crawler_restart_flag:
            clear_dir(config.raw_path)
            target_crawl(config)


def target_crawl(config: CrawlConfig):
    config.raw_path.mkdir(parents=True, exist_ok=True)

    home_html = fetch(config.site_url + quote(config.url_keyword))
    links = enroll_all_links(home_html, config.url_keyword)

    for link in links:
        file_name = link.replace(config.url_keyword, "").removesuffix("/")
        page_html = fetch(config.site_url + quote(link))
        new_page_path = config.raw_path / f"{file_name.replace('-', '')}.html"
        new_page_path.parent.mkdir(parents=True, exist_ok=True)
        new_page_path.write_text(page_html, encoding="utf-8")
        print(f"저장 확인 - 파일명: {file_name} 위치: {new_page_path}")
        time.sleep(1)


def fetch(url: str) -> str:
    r = httpx.get(url, follow_redirects=True, timeout=5)
    return r.text


def enroll_all_links(home_html: str, target_url: str) -> list[str]:
    soup = BeautifulSoup(home_html, "html.parser")
    links = [str(a["href"]) for a in soup.find_all("a", href=True)]
    endpoints = sorted({l for l in links if l.startswith(target_url)})
    return endpoints
