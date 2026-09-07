import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
I_F = "INDEX_FILE"
M_F = "META_FILE"
M_R_F = "META_RESULT_FILE"

"""
title: claude 작성 python script
content: 작업 규칙에 따라 crawl 본문 작성은 요청하지 않고 env 호출 및 기타 AI 미정의 개발 구현에서는 정리 및 구현을 요구함
"""


@dataclass(frozen=True)
class Config:
    base_path: str
    raw_path: Path
    md_path: Path
    index_file: Path
    meta_file: Path
    meta_result_file: Path

    @classmethod
    def from_config(cls) -> "Config":
        return cls(
            base_path=require_env("CORPORA_DUNGEONWORLD_PATH"),
            raw_path=pre_require_path("raw"),
            md_path=pre_require_path("md"),
            index_file=require_json_env("INDEX_FILE"),
            meta_file=require_json_env("META_FILE"),
            meta_result_file=require_json_env("META_RESULT_FILE"),
        )


def load_config() -> None:
    """공용 설정을 먼저 읽고, 로컬 비밀값이 덮어쓰게 한다."""
    load_dotenv(ROOT / ".env.shared")
    load_dotenv(ROOT / ".env", override=True)

    if len({require_env(I_F), require_env(M_F), require_env(M_R_F)}) < 3:
        raise RuntimeError(
            f"환경변수 {I_F}, {M_F}, {M_R_F} 중 같은 값이 있습니다. 각각의 파일명을 지정해 주세요."
        )


def require_json_env(name: str) -> Path:
    """파일명 환경변수를 코퍼스 루트 밑의 `<이름>.json` 경로로 확정한다.

    joinpath(".json") 은 확장자가 아니라 `<이름>/.json` 이라는 경로 한 칸을 더 만든다.
    파일명 결합은 문자열로 하고, 루트 밖 검사는 require_path 에 맡긴다.
    """
    return pre_require_path(f"{require_env(name)}.json")


def require_bool_env(name: str) -> bool:
    return require_env(name) == "1"


def require_env(name: str) -> str:
    """미설정, 빈 문자열, 공백만 입력을 모두 걸러낸 환경변수 값을 돌려준다."""
    value = os.getenv(name, "").strip()

    if not value:
        raise RuntimeError(
            f"환경변수 {name} 가 비어 있습니다. .env.shared / .env 를 확인하세요."
        )

    return value


def pre_require_path(*parts: str) -> Path:
    return require_path("CORPORA_DUNGEONWORLD_PATH", *parts)


def require_path(name: str, *parts: str) -> Path:
    """환경변수의 경로를 프로젝트 루트 기준으로 확정한다. 루트 밖은 거부한다."""
    base = Path(require_env(name)).expanduser()
    path = (base if base.is_absolute() else ROOT / base).joinpath(*parts).resolve()

    if not path.is_relative_to(ROOT):
        raise RuntimeError(f"환경변수 {name} 가 프로젝트 밖을 가리킵니다: {path}")

    return path
