from dataclasses import dataclass
from pathlib import Path

from rag_with_trpg.config import require_env, require_path

@dataclass(frozen=True)
class CrawlConfig:
  site_url: str
  url_keyword: str
  raw_path: Path
  md_path: Path
  re_crawl: bool
  re_create: bool

  @classmethod
  def from_env(cls) -> "CrawlConfig":
    return cls(
      site_url=require_env("DW_SITE").rstrip("/"),
      url_keyword=require_env("URL_KEYWORD"),
      raw_path=require_path("CORPORA_DUNGEONWORLD_PATH", "raw"),
      md_path=require_path("CORPORA_DUNGEONWORLD_PATH", "md"),
      re_crawl=require_env("RE_CRAWL") == "1",
      re_create=require_env("RE_CREATE") == "1",
  )
