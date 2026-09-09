from sentence_transformers import SentenceTransformer

from rag_with_trpg.crawl.index_mapped import PageEntry
from rag_with_trpg.diagnose.config import DiagnoseConfig
from rag_with_trpg.util import load_json


def compare(config: DiagnoseConfig, model_dict: dict[str, SentenceTransformer]):
    load_json(PageEntry, config, "index_file")

    if config.do_model_compare:
        print(
            f"paraphrase-multilingual-MiniLM-L12-v2: 차원: {model_dict["paraphrase"].get_embedding_dimension()}"
        )
        print(f"BAAI/bge-m3: 차원: {model_dict["BAAI"].get_embedding_dimension()}")
        print(
            f"intfloat/multilingual-e5-large: 차원: {model_dict["intfloat"].get_embedding_dimension()}"
        )
        print(
            f"jhgan/ko-sroberta-multitask: 차원: {model_dict["jhgan"].get_embedding_dimension()}"
        )
