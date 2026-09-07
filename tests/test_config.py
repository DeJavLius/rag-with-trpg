from dataclasses import FrozenInstanceError

import pytest

from rag_with_trpg.config import (
    ROOT,
    Config,
    load_config,
    require_bool_env,
    require_env,
    require_json_env,
    require_path,
)
from rag_with_trpg.crawl.config import CrawlConfig
from rag_with_trpg.diagnose.config import DiagnoseConfig

"""
title: claude 작성 python script — 테스트 본문
content: D-20 조건부 (2026-09-04 개정). 「무엇을 잠그나」와 기대값은 직접 정하고,
         pytest 문법·monkeypatch 배선은 AI 가 적었다.
         config.py 소관 — 설정이 조용히 빈 값으로 통과하지 않는지 (D-21 4번의 설정판).
"""

CORPORA = ROOT / "corpora" / "dungeonworld"

ENV = {
    "DW_SITE": "https://sites.google.com/",
    "URL_KEYWORD": "/view/dwtemporary/",
    "USER_AGENT": "rag-with-trpg-test",
    "CORPORA_DUNGEONWORLD_PATH": "corpora/dungeonworld/",
    "INDEX_FILE": "index",
    "META_FILE": "meta",
    "META_RESULT_FILE": "diagnose",
    "EMBED_TEST_MODEL": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    "EMBED_TEST_MAX_SEQ": "128",
    "DO_CRAWL": "0",
    "DO_CREATE": "0",
    "DO_DIAGNOSE": "0",
    "DO_MODEL_COMPARE": "0",
}


@pytest.fixture
def env(monkeypatch):
    """.env 를 읽지 않고 환경변수만 세운다 — 로컬 .env 값에 테스트가 흔들리지 않게."""
    for key, value in ENV.items():
        monkeypatch.setenv(key, value)
    return monkeypatch


# ─── require_env — 빈 값이 조용히 통과하지 않는다 ─────────────────────
def test_require_env_returns_value(env):
    assert require_env("INDEX_FILE") == "index"


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
    monkeypatch.setenv("PADDED", "  index  ")

    assert require_env("PADDED") == "index"


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


# ─── require_json_env — 파일명이 .json 경로 하나로 확정된다 ─────────────
def test_require_json_env_appends_suffix(env):
    """`.json` 은 확장자다. 경로 한 칸(`index/.json`)이 되면 파일이 안 열린다.

    joinpath(".json") 은 디렉터리를 하나 더 만든다 — 파일이 없다는 에러가
    한참 뒤 read_text 에서 나므로 원인이 설정이라는 걸 알기 어렵다.
    """
    path = require_json_env("INDEX_FILE")

    assert path == CORPORA / "index.json"
    assert path.suffix == ".json"
    assert path.parent == CORPORA


def test_require_json_env_rejects_escape(monkeypatch, env):
    """파일명으로도 코퍼스 밖을 못 가리킨다 — require_path 의 검사를 그대로 탄다."""
    monkeypatch.setenv("INDEX_FILE", "../../../../etc/passwd")

    with pytest.raises(RuntimeError):
        require_json_env("INDEX_FILE")


# ─── require_bool_env — "1" 만 참이다 ──────────────────────────────
@pytest.mark.parametrize(
    "value, expected",
    [("1", True), ("0", False), ("true", False), ("True", False), ("yes", False)],
)
def test_require_bool_env(monkeypatch, value: str, expected: bool):
    """「true」 를 참으로 읽으면 의도치 않은 재수집·재변환이 돈다."""
    monkeypatch.setenv("FLAG", value)

    assert require_bool_env("FLAG") is expected


def test_require_bool_env_rejects_blank(monkeypatch):
    """빈 값은 False 가 아니라 에러다. 미설정과 「끔」을 구분한다."""
    monkeypatch.setenv("FLAG", "")

    with pytest.raises(RuntimeError):
        require_bool_env("FLAG")


# ─── Config — JSON 3종이 서로 다른 파일이어야 한다 ─────────────────────
def test_config_json_files_are_distinct(env):
    """셋이 같은 파일을 가리키면 뒤 단계가 앞 단계 산출물을 덮어쓴다.

    load_config() 는 환경변수 「값」의 중복만 본다. 이름이 달라도 from_config 가
    같은 변수를 두 번 읽으면 그 검사를 그냥 지나간다 — 그래서 여기서 한 번 더 본다.
    """
    config = Config.from_config()

    assert config.index_file == CORPORA / "index.json"
    assert config.meta_file == CORPORA / "meta.json"
    assert config.meta_result_file == CORPORA / "diagnose.json"
    assert len({config.index_file, config.meta_file, config.meta_result_file}) == 3


def test_config_paths_are_under_root(env):
    config = Config.from_config()

    assert config.raw_path == CORPORA / "raw"
    assert config.md_path == CORPORA / "md"


# ─── load_config — 파일명 중복을 멈춘다 ────────────────────────────
def test_load_config_rejects_duplicate_file_names(monkeypatch, env):
    """META_FILE 이 INDEX_FILE 과 같으면 인덱스가 계측 결과에 덮인다."""
    monkeypatch.setenv("META_FILE", "index")

    with pytest.raises(RuntimeError):
        load_config()


def test_load_config_restores_values_from_shared_file(monkeypatch, env):
    """지워진 값은 .env.shared 에서 되돌아온다 — 그게 이 함수의 일이다.

    중복 검사가 monkeypatch 값으로 도는 이유이기도 하다: .env.shared 는
    override=False 로 읽으므로 이미 세워진 환경변수를 덮지 않는다.
    """
    monkeypatch.delenv("META_RESULT_FILE", raising=False)

    load_config()

    assert require_env("META_RESULT_FILE")
    assert require_env("META_FILE") == "meta"  # monkeypatch 값이 살아 있다


# ─── from_config — 필드 누락을 잡는다 ──────────────────────────────
def test_crawl_config_reads_every_field(env):
    """필드가 늘 때 .env 갱신을 잊으면 여기서 먼저 깨진다."""
    config = CrawlConfig.from_config()

    assert config.site_url == "https://sites.google.com"
    assert config.url_keyword == "/view/dwtemporary/"
    assert config.user_agent == "rag-with-trpg-test"
    assert config.index_file == CORPORA / "index.json"
    assert config.raw_path == CORPORA / "raw"
    assert config.md_path == CORPORA / "md"
    assert config.do_crawl is False
    assert config.do_create is False


def test_diagnose_config_reads_every_field(env):
    """DiagnoseConfig 도 같은 기반을 쓴다 — 기반이 바뀌면 둘 다 여기서 깨진다."""
    config = DiagnoseConfig.from_config()

    assert config.embed_test_model.endswith("paraphrase-multilingual-MiniLM-L12-v2")
    assert config.embed_test_max_seq == 128
    assert config.meta_file == CORPORA / "meta.json"
    assert config.meta_result_file == CORPORA / "diagnose.json"
    assert config.do_diagnose is False
    assert config.do_model_compare is False


def test_from_config_strips_trailing_slash_on_site_url(monkeypatch, env):
    """site_url + link 로 URL 을 만들므로 끝 슬래시가 남으면 `//` 가 된다."""
    monkeypatch.setenv("DW_SITE", "https://sites.google.com/")

    assert CrawlConfig.from_config().site_url == "https://sites.google.com"


@pytest.mark.parametrize("value, expected", [("1", True), ("0", False)])
def test_flags_reach_the_config(monkeypatch, env, value: str, expected: bool):
    monkeypatch.setenv("DO_CRAWL", value)

    assert CrawlConfig.from_config().do_crawl is expected


def test_blank_flag_stops_config(monkeypatch, env):
    """빈 플래그는 조용히 False 가 되지 않는다."""
    monkeypatch.setenv("DO_CRAWL", "")

    with pytest.raises(RuntimeError):
        CrawlConfig.from_config()


def test_config_is_frozen(env):
    """설정은 실행 중에 바뀌지 않는다. 바꾸려면 dataclasses.replace 로 새로 만든다."""
    config = CrawlConfig.from_config()

    with pytest.raises(FrozenInstanceError):
        config.index_file = CORPORA / "other.json"  # type: ignore[misc]
