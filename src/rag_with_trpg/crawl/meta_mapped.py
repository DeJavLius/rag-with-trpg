from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

from bs4 import BeautifulSoup

from rag_with_trpg.crawl.config import CrawlConfig
from rag_with_trpg.crawl.util import header_counting

"""
title: claude 작성 python script — 시그니처 전용
content: D-20 조건부. 시그니처·docstring·함정만 AI 가 적었고 본문은 직접 쓴다.
         목적은 provenance(원문 URL) 보존 — D-07 응답 각주와 3주차 청킹 메타데이터의 재료.
"""

# D-04 — 인덱스 페이지는 「직업」 1건. raw 39 → md 38.
# 코퍼스가 바뀌면 D-04 를 재판정한 뒤에 이 값을 고친다. 조용히 늘리지 않는다.
# 내 판단: meta data file을 형식 자유롭게 네이밍을 정하게 하고 json으로 고정
EXPECTED_EXCLUDED = 1


@dataclass(frozen=True)
class PageEntry:
    slug: str  # PK. "직업/마법사/마법사-주문" — 하이픈이 살아 있는 원본
    parent: str | None  # 부모의 slug. 루트면 None
    title: str  # "마법사 주문" — <title> 에서 (D-28)
    url: str  # 퍼센트 인코딩된 og:url 원본. D-07 각주에 그대로 붙일 값
    raw: str  # "raw/직업/마법사/마법사주문.html"
    md: str | None  # "md/마법사 주문.md" — 제외되면 None
    excluded: str | None  # "index" | None
    chars: int
    headings: list[int]  # 인덱스 + 1 위치가 header 크기


def save_index(path: Path, config: CrawlConfig, entries: list[PageEntry]) -> None:
    """메타데이터 파일을 쓴다. `pages` 는 **slug 를 키로 하는 평면 map** 이다.

    중첩 트리로 안 쓰는 이유 — 소비자가 전부 단건 조회다. D-07 응답 각주(청크 → url),
    3주차 청킹 메타데이터, D-26 라우팅(조상 체인) 셋 다 아래로 순회하지 않는다.

    위치는 md_path 바깥이라 `converter()` 첫 줄의 `clear_dir(config.md_path)` 에 안 지워진다.
    파일명은 호출자가 path 로 정한다 — 이름은 설정, 확장자는 json 고정.

    ⚠️ slug 는 키이므로 값 안에 다시 넣지 않는다. 두 곳이 어긋날 자리를 만들지 않는다.
    ⚠️ `json.dump(..., ensure_ascii=False, indent=2, sort_keys=True)`.
       ensure_ascii 기본값(True)으로 쓰면 한글이 \\uc9c1\\uc5c5 이 되어 git diff 가 안 읽힌다.
       sort_keys 는 덤이 아니다 — 슬러그 사전순이면 **부모가 자식 바로 앞에 와서**
       평면 map 도 눈으로 트리처럼 읽힌다.
    ⚠️ counts 에 raw / md / excluded 를 함께 넣는다. S1 건수 가드의 판정 재료다.
    """
    raise NotImplementedError


def source_url(soup: BeautifulSoup) -> str:
    url = soup.find("meta", attrs={"property": "og:url"})

    if url is None:
        raise RuntimeError("url not found")

    return url.get("content")


def slug_of(url: str, url_keyword: str) -> str:
    return unquote(url).replace(url_keyword, "")


def parent_of(slug: str) -> str | None:
    nodes = slug.split("/")
    return None if len(nodes) == 1 else nodes[-2]
