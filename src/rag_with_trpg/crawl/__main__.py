from rag_with_trpg.config import load_config
from rag_with_trpg.crawl.config import CrawlConfig
from rag_with_trpg.crawl.convert import converter
from rag_with_trpg.crawl.crawl import crawler
from rag_with_trpg.crawl.meta_mapped import mapper
from rag_with_trpg.crawl.util import md_head_counter, serialize


def main() -> None:
    print("crawl: config environment load")
    load_config()
    config = CrawlConfig.from_env()
    init_files = list(config.raw_path.rglob("*.html"))

    print("crawl: start raw file check and crawling")
    crawler(config, init_files)

    print("crawl: start convert raw html into markdown")
    raw_files = list(config.raw_path.rglob("*.html"))
    check_md_files = list(config.md_path.rglob("*.md"))
    indexed_files = converter(config, raw_files, check_md_files)

    print("crawl: start markdown file heading check")
    converted_md_files = list(config.md_path.rglob("*.md"))

    for md_file in converted_md_files:
        title, md_total, head_count = md_head_counter(md_file)
        print(
            f"{title} files line: {md_total}, total: {sum(head_count)}, headers: {serialize(head_count)}"
        )

    print("crawl: start making meta data with markdown & html")
    mapper(config, raw_files, converted_md_files, indexed_files)


if __name__ == "__main__":
    main()
