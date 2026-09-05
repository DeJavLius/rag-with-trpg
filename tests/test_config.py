from dataclasses import FrozenInstanceError

import pytest

from rag_with_trpg.config import ROOT, require_env, require_path
from rag_with_trpg.crawl.config import CrawlConfig

"""
title: claude 작성 python script — 테스트 본문
content: D-20 조건부 (2026-09-04 개정). 「무엇을 잠그나」와 기대값은 직접 정하고,
         pytest 문법·monkeypatch 배선은 AI 가 적었다.
         config.py 소관 — 설정이 조용히 빈 값으로 통과하지 않는지 (D-21 4번의 설정판).
"""

ENV = {
    "DW_SITE": "https://sites.google.com/",
    "URL_KEYWORD": "/view/dwtemporary/",
    "USER_AGENT": "rag-with-trpg-test",
    "CORPORA_DUNGEONWORLD_PATH": "corpora/dungeonworld/",
    "META_FILE": "meta",
    "RE_CRAWL": "0",
    "RE_CREATE": "0",
}


@pytest.fixture
def env(monkeypatch):
    """.env 를 읽지 않고 환경변수만 세운다 — 로컬 .env 값에 테스트가 흔들리지 않게."""
    for key, value in ENV.items():
        monkeypatch.setenv(key, value)
    return monkeypatch


# ─── require_env — 빈 값이 조용히 통과하지 않는다 ─────────────────────
def test_require_env_returns_value(env):
    assert require_env("META_FILE") == "meta"


def test_require_env_raises_when_unset(monkeypatch):
    monkeypatch.delenv("결코_없는_변수", raising=False)

    with pytest.raises(RuntimeError):
        require_env("결코_없는_변수")


@pytest.mark.parametrize("value", ["", "   ", "\t\n"])
def test_require_env_rejects_blank(monkeypatch, value: str):
    """빈 문자열·공백만 있는 값도 미설정으로 본다.

    dotenv 는 `KEY=` 를 빈 문자열로 읽는다. 통과시키면 URL 이 사이트 루트가 되어
    엉뚱한 곳을 크롤링한다 — 에러 없이.
    """
    monkeypatch.setenv("BLANK_KEY", value)

    with pytest.raises(RuntimeError):
        require_env("BLANK_KEY")


def test_require_env_strips_surrounding_space(monkeypatch):
    monkeypatch.setenv("PADDED", "  meta  ")

    assert require_env("PADDED") == "meta"


# ─── require_path — 프로젝트 밖을 가리키지 않는다 ──────────────────────
def test_require_path_resolves_under_root(env):
    path = require_path("CORPORA_DUNGEONWORLD_PATH", "raw")

    assert path == ROOT / "corpora" / "dungeonworld" / "raw"


def test_require_path_rejects_escape(monkeypatch):
    """`../` 로 저장소 밖을 가리키면 거부한다.

    clear_dir 가 이 경로를 통째로 비우므로, 밖을 가리키면 남의 디렉터리를 지운다.
    """
    monkeypatch.setenv("ESCAPE_PATH", "../../..")

    with pytest.raises(RuntimeError):
        require_path("ESCAPE_PATH")


def test_require_path_rejects_absolute_outside_root(monkeypatch):
    monkeypatch.setenv("ABS_PATH", "/tmp")

    with pytest.raises(RuntimeError):
        require_path("ABS_PATH")


# ─── CrawlConfig.from_env — 필드 누락을 잡는다 ────────────────────────
def test_from_env_reads_every_field(env):
    """필드가 늘 때 .env 갱신을 잊으면 여기서 먼저 깨진다."""
    config = CrawlConfig.from_env()

    assert config.site_url == "https://sites.google.com"
    assert config.url_keyword == "/view/dwtemporary/"
    assert config.user_agent == "rag-with-trpg-test"
    assert config.meta_file == "meta"
    assert config.raw_path == ROOT / "corpora" / "dungeonworld" / "raw"
    assert config.md_path == ROOT / "corpora" / "dungeonworld" / "md"


def test_from_env_strips_trailing_slash_on_site_url(monkeypatch, env):
    """site_url + link 로 URL 을 만들므로 끝 슬래시가 남으면 `//` 가 된다."""
    monkeypatch.setenv("DW_SITE", "https://sites.google.com/")

    assert CrawlConfig.from_env().site_url == "https://sites.google.com"


@pytest.mark.parametrize(
    "value, expected", [("1", True), ("0", False), ("", None), ("true", False)]
)
def test_flags_are_only_true_on_one(monkeypatch, env, value: str, expected):
    """플래그는 "1" 일 때만 참이다. "true" 를 참으로 읽으면 의도치 않은 재수집이 돈다."""
    if value == "":
        monkeypatch.setenv("RE_CRAWL", value)
        with pytest.raises(RuntimeError):
            CrawlConfig.from_env()
        return

    monkeypatch.setenv("RE_CRAWL", value)

    assert CrawlConfig.from_env().re_crawl is expected


def test_config_is_frozen(env):
    """설정은 실행 중에 바뀌지 않는다. 바꾸려면 dataclasses.replace 로 새로 만든다."""
    config = CrawlConfig.from_env()

    with pytest.raises(FrozenInstanceError):
        config.meta_file = "other"  # type: ignore[misc]
