from sentence_transformers import SentenceTransformer

from rag_with_trpg.diagnose.config import DiagnoseConfig


def compare(config: DiagnoseConfig, model_dict: dict[str, SentenceTransformer]):
    print(f"paraphrase-multilingual-MiniLM-L12-v2: 차원: {model_dict["paraphrase"].config.hidden_size}")
    print(f"BAAI/bge-m3: 차원: {model_dict["BAAI"].config.hidden_size}")
    print(f"intfloat/multilingual-e5-large: 차원: {model_dict["intfloat"].config.hidden_size}")
    print(f"jhgan/ko-sroberta-multitask: 차원: {model_dict["jhgan"].config.hidden_size}")
