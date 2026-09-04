from dataclasses import dataclass
from pathlib import Path

from bs4 import BeautifulSoup

from rag_with_trpg.crawl.config import CrawlConfig

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
    slug: str  # "직업/마법사/마법사-주문" — 하이픈이 살아 있는 원본
    title: str  # "마법사 주문" — <title> 에서 (D-28)
    url: str  # 퍼센트 인코딩된 og:url 원본. D-07 각주에 그대로 붙일 값
    raw: str  # "raw/직업/마법사/마법사주문.html"
    md: str | None  # "md/마법사 주문.md" — 제외되면 None
    excluded: str | None  # "index" | None
    chars: int
    headings: dict[str, int]


def source_url(soup: BeautifulSoup) -> str:
    """<meta property="og:url"> 의 content.

    raw 39/39 에 존재한다 (2026-09-04 실측).

    ⚠️ 없을 때 "" 를 돌려주지 않는다. 빈 문자열은 뒤 단계에서 조용히 통과해
       D-21 4번(필터가 아무것도 안 거름)을 그대로 재현한다. 예외를 던진다.
    ⚠️ `soup.find("meta", attrs={"property": "og:url"})` 로 찾는다.
       kwargs 로도 되지만 `class` 처럼 예약어인 속성이 섞이면 규칙이 갈린다.
    """
    raise NotImplementedError


def slug_of(url: str, url_keyword: str) -> str:
    """og:url 에서 원본 슬러그를 뽑는다. "직업/마법사/마법사-주문".

    ⚠️ 파일 경로에서 만들면 안 된다 — crawl.py 가 `replace('-', '')` 로 하이픈을 지웠고
       그 변환은 비가역이다. 하이픈이 남아 있는 곳은 og:url 뿐이고 39개 중 19개가 걸린다.
    ⚠️ url 은 퍼센트 인코딩돼 있다. 슬러그는 `urllib.parse.unquote` 결과를 쓰고,
       PageEntry.url 에는 인코딩된 원본을 그대로 넣는다 (링크로 쓸 값이라서).
    """
    raise NotImplementedError


def count_headings(markdown: str) -> dict[str, int]:
    """레벨별 ATX 헤딩 개수. {"1": 24, "2": 0, ... "6": 0}

    ⚠️ `#` 뒤의 공백까지 세야 한다. 공백을 빼면 본문 안의 `#` 가 h1 으로 잡힌다.
       지금 코퍼스는 줄머리가 아닌 `#` 가 0개라 안 걸리지만 코퍼스 B/C 에는 코드 블록이 있다.
    ⚠️ 키가 int 면 json.dump 가 문자열로 바꾼다. 처음부터 str 로 둔다.
    """
    raise NotImplementedError


def build_tree(entries: list[PageEntry]) -> dict:
    """슬러그를 "/" 로 쪼개 중첩 dict 로 접는다. 노드 키는 슬러그의 마지막 세그먼트.

    ⚠️ 페이지이면서 부모인 노드가 있다 — `직업/마법사` 와 `직업/마법사/마법사-주문` 이
       둘 다 실재한다. 한 노드가 md 와 children 을 동시에 가져야 한다.
    ⚠️ 현재 최대 깊이는 3 (`직업/마법사/마법사-주문`).
    """
    raise NotImplementedError


def save_index(path: Path, config: CrawlConfig, entries: list[PageEntry]) -> None:
    """`corpora/dungeonworld/index.json` 을 쓴다.

    위치가 md_path 바깥이라 `converter()` 첫 줄의 `clear_dir(config.md_path)` 에 안 지워진다.

    ⚠️ `json.dump(..., ensure_ascii=False, indent=2, sort_keys=True)`.
       ensure_ascii 기본값(True)으로 쓰면 한글이 \\uc9c1\\uc5c5 이 되어 git diff 가 안 읽힌다.
    ⚠️ counts 에 raw / md / excluded 를 함께 넣는다. S1 건수 가드의 판정 재료다.
    """
    raise NotImplementedError
