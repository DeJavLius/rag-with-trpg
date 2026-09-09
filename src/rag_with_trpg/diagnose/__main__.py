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

    if config.do_compare:
        model_dict: dict[str, SentenceTransformer] = {}

        match config.model_index:
            case 0:
                model_dict["paraphrase"] = SentenceTransformer(
                    "paraphrase-multilingual-MiniLM-L12-v2"
                )
            case 1:
                model_dict["BAAI"] = SentenceTransformer("BAAI/bge-m3")
            case 2:
                model_dict["intfloat"] = SentenceTransformer(
                    "intfloat/multilingual-e5-large"
                )
            case 3:
                model_dict["jhgan"] = SentenceTransformer("jhgan/ko-sroberta-multitask")

        if config.model_index > 3:
            model_dict["paraphrase"] = SentenceTransformer(
                "paraphrase-multilingual-MiniLM-L12-v2"
            )
            model_dict["BAAI"] = SentenceTransformer("BAAI/bge-m3")
            model_dict["intfloat"] = SentenceTransformer(
                "intfloat/multilingual-e5-large"
            )
            model_dict["jhgan"] = SentenceTransformer("jhgan/ko-sroberta-multitask")

        compare(config, model_dict)


if __name__ == "__main__":
    main()
