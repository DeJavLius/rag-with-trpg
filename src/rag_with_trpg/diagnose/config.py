from dataclasses import dataclass
from pathlib import Path

from rag_with_trpg.config import require_env, require_path


@dataclass(frozen=True)
class DiagnoseConfig:
    base_path: str
    index_file: Path
    md_path: Path
    meta_file: Path
    meta_result_file: Path
    embed_test_model: str
    embed_test_max_seq: int

    @classmethod
    def from_env(cls) -> "DiagnoseConfig":
        return cls(
            base_path=require_env("CORPORA_DUNGEONWORLD_PATH"),
            index_file=require_path(
                "CORPORA_DUNGEONWORLD_PATH", f"{require_env("INDEX_FILE")}.json"
            ),
            md_path=require_path("CORPORA_DUNGEONWORLD_PATH", "md"),
            meta_file=require_path(
                "CORPORA_DUNGEONWORLD_PATH", f"{require_env("META_FILE")}.json"
            ),
            meta_result_file=require_path(
                "CORPORA_DUNGEONWORLD_PATH", f"{require_env("META_RESULT_FILE")}.json"
            ),
            embed_test_model=require_env("EMBED_TEST_MODEL"),
            embed_test_max_seq=int(require_env("EMBED_TEST_MAX_SEQ")),
        )
