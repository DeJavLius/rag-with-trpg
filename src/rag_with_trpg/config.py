import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]

"""
title: claude 작성 python script
content: 작업 규칙에 따라 crawl 본문 작성은 요청하지 않고 env 호출 및 기타 AI 미정의 개발 구현에서는 정리 및 구현을 요구함
"""
def load_config() -> None:
  """공용 설정을 먼저 읽고, 로컬 비밀값이 덮어쓰게 한다."""
  load_dotenv(ROOT / ".env.shared")
  load_dotenv(ROOT / ".env", override=True)

def require_env(name: str) -> str:
  """미설정, 빈 문자열, 공백만 입력을 모두 걸러낸 환경변수 값을 돌려준다."""
  value = os.getenv(name, "").strip()

  if not value:
    raise RuntimeError(f"환경변수 {name} 가 비어 있습니다. .env.shared / .env 를 확인하세요.")

  return value

def require_path(name: str, *parts: str) -> Path:
  """환경변수의 경로를 프로젝트 루트 기준으로 확정한다. 루트 밖은 거부한다."""
  base = Path(require_env(name)).expanduser()
  path = (base if base.is_absolute() else ROOT / base).joinpath(*parts).resolve()

  if not path.is_relative_to(ROOT):
    raise RuntimeError(f"환경변수 {name} 가 프로젝트 밖을 가리킵니다: {path}")

  return path
