import unittest
from sentence_transformers import SentenceTransformer

class MyTestCase(unittest.TestCase):
    def test_something(self):

        m = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        print("max_seq_length =", m.max_seq_length)
        print("dim =", m.get_sentence_embedding_dimension())
        print("dim =", m.get_embedding_dimension())

if __name__ == '__main__':
    unittest.main()
