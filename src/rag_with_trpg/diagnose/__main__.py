from sentence_transformers import SentenceTransformer

from rag_with_trpg.config import load_config
from rag_with_trpg.diagnose.config import DiagnoseConfig
from rag_with_trpg.diagnose.diagnos import diagnose
from rag_with_trpg.diagnose.model_compare import compare


def main() -> None:
    print("[0] diagnose: config environment load")
    load_config()
    config = DiagnoseConfig.from_config()

    if config.do_diagnose:
        diagnose(config)

    if config.do_model_compare:
        model_dict: dict[str, SentenceTransformer] = {
            "paraphrase": SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2"),
            "BAAI": SentenceTransformer("BAAI/bge-m3"),
            "intfloat": SentenceTransformer("intfloat/multilingual-e5-large"),
            "jhgan": SentenceTransformer("jhgan/ko-sroberta-multitask"),
        }

        compare(config, model_dict)


if __name__ == "__main__":
    main()
