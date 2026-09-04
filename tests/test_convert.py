import re
from dataclasses import replace

import pytest
from bs4 import BeautifulSoup
from conftest import EXPECTED_MD

from rag_with_trpg.crawl import convert
from rag_with_trpg.crawl.convert import (
    converter,
    extract,
    is_index_page,
    title_decision,
)

"""
title: claude 작성 python script — 테스트 본문
content: D-20 조건부 (2026-09-04 개정). 「무엇을 잠그나」와 기대값은 직접 정하고,
         pytest 문법·픽스처 배선·assert 표현은 AI 가 적었다.
         각 테스트가 잠그는 결정 번호를 주석 한 줄로 남긴다.
"""

# markdownify 가 <a> 를 남겼을 때 나오는 형태: [텍스트](/view/...)
MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\([^)]*\)")

# <section> 밖에만 있는 Google Sites 크롬. 본문에 섞이면 선택자가 틀린 것이다.
NAVIGATION_MARKERS = ("Google Sites", "Report abuse", "Page details")


# ─── D-29 · 가장 중요 ────────────────────────────────────────────────
def test_no_markdown_links(raw_files):
    """strip=['a','img'] 가 살아 있는지 잠근다.

    지우면 에러 없이 갭이 5.6배 → 1.8배로 무너지고 제외가 0건이 된다
    (2026-09-04 실측: strip 제거 시 39개 중 임계값 미만 0개).
    """
    offenders = [
        raw.name
        for raw in raw_files
        if MARKDOWN_LINK.search(extract(raw.read_text(encoding="utf-8"))[1])
    ]

    assert offenders == []


# ─── <section> 선택자 (D-33) ─────────────────────────────────────────
def test_extract_drops_navigation(raw_files):
    """네비게이션·푸터가 본문에 섞이지 않는다."""
    offenders = [
        (raw.name, marker)
        for raw in raw_files
        for marker in NAVIGATION_MARKERS
        if marker in extract(raw.read_text(encoding="utf-8"))[1]
    ]

    assert offenders == []


# ─── D-04 건수 가드 ──────────────────────────────────────────────────
def test_excluded_count_is_one(tmp_config, raw_files):
    """raw 39 → md 38. 제외는 정확히 「직업」 1건."""
    converter(tmp_config, raw_files, [])

    assert len(list(tmp_config.md_path.glob("*.md"))) == EXPECTED_MD


def test_guard_stops_when_nothing_excluded(tmp_config, raw_files, monkeypatch):
    """제외가 0건이면 조용히 통과하지 않고 멈춘다 (D-21 4번)."""
    monkeypatch.setattr(convert, "is_index_page", lambda markdown: False)

    with pytest.raises(RuntimeError, match="인덱스 제외가 0건"):
        converter(tmp_config, raw_files, [])


# ─── converter 분기 ──────────────────────────────────────────────────
def test_converter_writes_md(tmp_config, raw_files):
    converter(tmp_config, raw_files, [])

    assert list(tmp_config.md_path.glob("*.md"))


def test_converter_skips_when_md_exists(tmp_config, raw_files):
    converter(tmp_config, raw_files, [tmp_config.md_path / "already.md"])

    assert not tmp_config.md_path.exists()


@pytest.mark.parametrize("re_create", [True, False])
def test_re_create_controls_rebuild(make_config, raw_files, re_create):
    config = make_config(re_create=re_create)
    converter(config, raw_files, [config.md_path / "already.md"])

    assert config.md_path.is_dir() is re_create


def test_replace_overrides_single_flag(tmp_config, raw_files):
    config = replace(tmp_config, re_create=True)
    converter(config, raw_files, [config.md_path / "already.md"])

    assert list(config.md_path.glob("*.md"))


# ─── D-28 제목 소스 ──────────────────────────────────────────────────
def test_title_decision_without_separator(home_html):
    soup = BeautifulSoup(home_html, "html.parser")

    assert title_decision(soup) == soup.title.get_text(strip=True)


def test_title_decision_strips_site_name(body_html):
    soup = BeautifulSoup(body_html, "html.parser")
    title = title_decision(soup)

    assert " - " not in title
    assert soup.title.get_text(strip=True).endswith(title)


# ─── D-04 임계값 경계 ────────────────────────────────────────────────
def test_is_index_page_boundary(index_html, body_html):
    _, index_md = extract(index_html)
    _, body_md = extract(body_html)

    assert is_index_page(index_md)
    assert not is_index_page(body_md)
