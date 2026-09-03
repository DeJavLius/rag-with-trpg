import unittest
from pathlib import Path

import pytest

from rag_with_trpg.config import load_config
from rag_with_trpg.crawl.config import CrawlConfig
from rag_with_trpg.crawl.convert import (
    converter,
    extract,
    extracting,
    is_index_page,
    title_decision,
)


class MyTestCase(unittest.TestCase):
    answer = 38

    @pytest.fixture
    def tmp_config(tmp_path):
        return CrawlConfig(
            site_url="https://example.test",
            url_keyword="/view/dwtemporary/",
            raw_path=Path("corpora/dungeonworld/raw"),  # 읽기만 — 실물 픽스처
            md_path=Path("corpora/dungeonworld/tmp_md"),  # 쓰기 — 임시
            re_crawl=False,
            re_create=True,
        )

    def test_converter(self):

        return


if __name__ == "__main__":
    unittest.main()
