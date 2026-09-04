from dataclasses import replace

import pytest
from bs4 import BeautifulSoup

from rag_with_trpg.crawl.convert import (
    converter,
    extract,
    is_index_page,
    title_decision,
)


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


def test_title_decision_without_separator(home_html):
    soup = BeautifulSoup(home_html, "html.parser")

    assert title_decision(soup) == soup.title.get_text(strip=True)


def test_title_decision_strips_site_name(body_html):
    soup = BeautifulSoup(body_html, "html.parser")
    title = title_decision(soup)

    assert " - " not in title
    assert soup.title.get_text(strip=True).endswith(title)


def test_is_index_page_boundary(index_html, body_html):
    _, index_md = extract(index_html)
    _, body_md = extract(body_html)

    assert is_index_page(index_md)
    assert not is_index_page(body_md)
