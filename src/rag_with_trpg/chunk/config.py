from dataclasses import dataclass

from rag_with_trpg.config import Config, get_env


@dataclass(frozen=True, kw_only=True)
class ChunkConfig(Config):
    chunk_size: int
    chunk_overlap: int = 0
    chunk_min: int = 0
    semantic_percentile: int
    semantic_buffer: int

    @classmethod
    def _extra_kwargs(cls) -> dict[str, int]:
        return {
            "chunk_size": int(get_env("CHUNK_SIZE")),
            "chunk_overlap": int(get_env("CHUNK_OVERLAP")),
            "chunk_min": int(get_env("CHUNK_MIN")),
            "SEMANTIC_PERCENTILE": int(get_env("SEMANTIC_PERCENTILE")),
            "SEMANTIC_BUFFER": int(get_env("SEMANTIC_BUFFER")),
        }
