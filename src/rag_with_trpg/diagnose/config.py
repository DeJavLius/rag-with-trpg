from dataclasses import dataclass
from typing import Any

from rag_with_trpg.config import Config, require_bool_env, require_env


@dataclass(frozen=True, kw_only=True)
class DiagnoseConfig(Config):
    embed_test_model: str
    embed_test_max_seq: int
    model_local_only: bool
    do_diagnose: bool
    do_model_compare: bool

    @classmethod
    def _extra_kwargs(cls) -> dict[str, Any]:
        return {
            "embed_test_model": require_env("EMBED_TEST_MODEL"),
            "embed_test_max_seq": int(require_env("EMBED_TEST_MAX_SEQ")),
            "model_local_only": require_bool_env("MODEL_LOCAL_ONLY"),
            "do_diagnose": require_bool_env("DO_DIAGNOSE"),
            "do_model_compare": require_bool_env("DO_MODEL_COMPARE"),
        }
