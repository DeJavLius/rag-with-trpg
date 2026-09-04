from pathlib import Path

import pytest

from rag_with_trpg.config import ROOT
from rag_with_trpg.crawl.config import CrawlConfig

"""
title: claude 작성 python script
content: 테스트 픽스처(보일러플레이트)만 정의한다. 실제 검증(assert)은 각 test_*.py 에서 직접 작성한다.
"""

# 판정 경계에 쓰이는 페이지 3종 (D-04 / D-28 / D-29)
INDEX_PAGE = "직업.html"  # 인덱스 — strip 적용 175자
HOME_PAGE = "홈.html"  # 홈 — 972자. <title> 에 " - " 가 없는 유일한 페이지
BODY_PAGE = "액션.html"  # 본문 — 헤딩 24개

INDEX_MD = "직업.md"  # 인덱스 — strip 적용 175자
HOME_MD = "던전월드 한국어 공개판 임시 웹페이지.md"  # 홈 — 972자. <title> 에 " - " 가 없는 유일한 페이지
BODY_MD = "액션.md"  # 본문 — 헤딩 24개


@pytest.fixture(scope="session")
def raw_dir() -> Path:
    """크롤링 원본 HTML 디렉터리. 읽기 전용으로만 쓴다."""
    return ROOT / "corpora" / "dungeonworld" / "raw"


@pytest.fixture(scope="session")
def raw_files(raw_dir: Path) -> list[Path]:
    """raw/ 의 HTML 전체. 하위 디렉터리를 포함한다."""
    return sorted(raw_dir.rglob("*.html"))


@pytest.fixture(scope="session")
def read_raw(raw_dir: Path):
    """raw/ 에서 파일 하나를 이름으로 읽는 헬퍼를 돌려준다."""

    def _read(name: str) -> str:
        return (raw_dir / name).read_text(encoding="utf-8")

    return _read


@pytest.fixture(scope="session")
def index_html(read_raw) -> str:
    return read_raw(INDEX_PAGE)


@pytest.fixture(scope="session")
def home_html(read_raw) -> str:
    return read_raw(HOME_PAGE)


@pytest.fixture(scope="session")
def body_html(read_raw) -> str:
    return read_raw(BODY_PAGE)


@pytest.fixture
def make_config(tmp_path: Path, raw_dir: Path):
    """CrawlConfig 를 만들어 주는 팩토리. 호출 시점에 인자를 넣는다.

    fixture 는 인자를 직접 못 받으므로, 인자가 필요한 설정은 팩토리로 감싼다.
    from_env() 를 거치지 않으므로 .env 없이도 돈다 (D-15).
    site_url / url_keyword 는 변환 경로에서 쓰이지 않아 고정값을 넣는다.
    md_path 만 임시 디렉터리로 돌려 실제 corpora/md/ 를 건드리지 않는다.
    """

    def _make(*, re_crawl: bool = False, re_create: bool = False) -> CrawlConfig:
        return CrawlConfig(
            site_url="https://example.invalid",
            url_keyword="/view/dwtemporary/",
            raw_path=raw_dir,
            md_path=tmp_path / "md",
            re_crawl=re_crawl,
            re_create=re_create,
        )

    return _make


@pytest.fixture
def tmp_config(make_config) -> CrawlConfig:
    """플래그 기본값(False/False) 설정. 플래그만 바꿀 땐 dataclasses.replace 를 쓴다."""
    return make_config()
