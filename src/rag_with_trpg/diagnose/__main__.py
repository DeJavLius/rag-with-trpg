from transformers import AutoTokenizer

def main() -> None:
    tok = AutoTokenizer.from_pretrained("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

if __name__ == "__main__":
    main()
