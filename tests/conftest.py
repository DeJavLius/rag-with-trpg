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
def tmp_config(tmp_path: Path, raw_dir: Path) -> CrawlConfig:
    """md_path 만 임시 디렉터리로 돌린 설정. 실제 corpora/md/ 를 건드리지 않는다.

    from_env() 를 거치지 않으므로 .env 없이도 돈다 (D-15).
    site_url / url_keyword 는 변환 경로에서 쓰이지 않아 고정값을 넣는다.
    """
    return CrawlConfig(
        site_url="https://example.invalid",
        url_keyword="/view/dwtemporary/",
        raw_path=raw_dir,
        md_path=tmp_path / "md",
        re_crawl=False,
        re_create=True,
    )
