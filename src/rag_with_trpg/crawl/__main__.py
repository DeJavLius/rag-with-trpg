from rag_with_trpg.config import load_config
from rag_with_trpg.crawl.config import CrawlConfig
from rag_with_trpg.crawl.crawl import crawler
from rag_with_trpg.crawl.convert import converter

def main() -> None:
  print("crawl: config environment load")
  load_config()
  config = CrawlConfig.from_env()
  raw_files = list(config.raw_path.rglob("*.html"))
  md_files = list(config.md_path.rglob("*.md"))

  print("crawl: start raw file check and crawling")
  crawler(config, raw_files)

  print("crawl: start convert raw html into markdown")
  converter(config, raw_files, md_files)

if __name__ == "__main__":
  main()
