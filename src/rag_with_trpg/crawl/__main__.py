from rag_with_trpg.config import load_config
from rag_with_trpg.crawl.config import CrawlConfig
from rag_with_trpg.crawl.convert import converter
from rag_with_trpg.crawl.crawl import crawler


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
    converter(config, raw_files, check_md_files)

    print("crawl: start markdown file heading check")
    converted_md_files = list(config.md_path.rglob("*.md"))

    head_sections: str = "###### "
    for md_file in converted_md_files:
        title = md_file.stem
        md = md_file.read_text(encoding="utf-8")
        md_total = len(md)

        head_count: list[int] = [0 for _ in range(6)]
        for h in range(6):
            header = head_sections[h:]
            head_count[5 - h] = md.count(header)
            md = md.replace(header, "")

        print(
            f"{title} files line: {md_total}, total: {sum(head_count)}, headers: {serialize(head_count)}"
        )


def serialize(val: list) -> str:
    return "".join([f"[{i + 1}: {v}] " for i, v in enumerate(val)])


if __name__ == "__main__":
    main()
