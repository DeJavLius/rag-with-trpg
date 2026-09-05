from dataclasses import dataclass
from pathlib import Path

from rag_with_trpg.config import require_env, require_path


@dataclass(frozen=True)
class DiagnoseConfig:
    base_path: str
    meta_file: str
    md_path: Path
    diagnose_file: str

    @classmethod
    def from_env(cls) -> "DiagnoseConfig":
        return cls(
            base_path=require_env("CORPORA_DUNGEONWORLD_PATH"),
            meta_file=require_env("META_FILE"),
            md_path=require_path("CORPORA_DUNGEONWORLD_PATH", "md"),
            diagnose_file=require_env("DIAGNOSE_FILE")
        )
