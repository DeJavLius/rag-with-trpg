from dataclasses import dataclass

from rag_with_trpg.config import Config, require_bool_env, require_env


@dataclass(frozen=True)
class CrawlConfig(Config):
    site_url: str
    url_keyword: str
    user_agent: str
    do_crawl: bool
    do_create: bool

    @classmethod
    def from_config(cls) -> "CrawlConfig":
        config: Config = Config.from_config()
        return cls(
            base_path=config.base_path,
            raw_path=config.raw_path,
            md_path=config.md_path,
            index_file=config.index_file,
            meta_file=config.meta_file,
            meta_result_file=config.meta_result_file,
            site_url=require_env("DW_SITE").rstrip("/"),
            url_keyword=require_env("URL_KEYWORD"),
            user_agent=require_env("USER_AGENT"),
            do_crawl=require_bool_env("DO_CRAWL"),
            do_create=require_bool_env("DO_CREATE"),
        )
