from dataclasses import dataclass

from rag_with_trpg.config import Config, require_bool_env, require_env


@dataclass(frozen=True)
class DiagnoseConfig(Config):
    embed_test_model: str
    embed_test_max_seq: int
    do_diagnose: bool
    do_model_compare: bool

    @classmethod
    def from_config(cls) -> "DiagnoseConfig":
        config: Config = Config.from_config()
        return cls(
            base_path=config.base_path,
            raw_path=config.raw_path,
            md_path=config.md_path,
            index_file=config.index_file,
            meta_file=config.meta_file,
            meta_result_file=config.meta_result_file,
            embed_test_model=require_env("EMBED_TEST_MODEL"),
            embed_test_max_seq=int(require_env("EMBED_TEST_MAX_SEQ")),
            do_diagnose=require_bool_env("DO_DIAGNOSE"),
            do_model_compare=require_bool_env("DO_MODEL_COMPARE"),
        )
