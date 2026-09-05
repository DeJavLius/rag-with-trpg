from dataclasses import dataclass
from pathlib import Path

from rag_with_trpg.config import require_env, require_path


@dataclass(frozen=True)
class CrawlConfig:
    site_url: str
    url_keyword: str
    user_agent: str
    base_path: str
    raw_path: Path
    md_path: Path
    meta_file: str
    re_crawl: bool
    re_create: bool

    @classmethod
    def from_env(cls) -> "CrawlConfig":
        return cls(
            site_url=require_env("DW_SITE").rstrip("/"),
            url_keyword=require_env("URL_KEYWORD"),
            user_agent=require_env("USER_AGENT"),
            base_path=require_env("CORPORA_DUNGEONWORLD_PATH"),
            raw_path=require_path("CORPORA_DUNGEONWORLD_PATH", "raw"),
            md_path=require_path("CORPORA_DUNGEONWORLD_PATH", "md"),
            meta_file=require_env("META_FILE"),
            re_crawl=require_env("RE_CRAWL") == "1",
            re_create=require_env("RE_CREATE") == "1",
        )
