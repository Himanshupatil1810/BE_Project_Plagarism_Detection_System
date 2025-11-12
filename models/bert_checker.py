from sentence_transformers import SentenceTransformer, util

class BERTChecker:
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize with a pretrained Sentence-BERT model.
        """
        self.model = SentenceTransformer(model_name)

    def calculate_similarity(self, doc1, doc2):
        """
        Takes two documents and returns semantic similarity score (0–1).
        """
        # Encode texts into dense embeddings
        embedding1 = self.model.encode(doc1, convert_to_tensor=True)
        embedding2 = self.model.encode(doc2, convert_to_tensor=True)

        # Compute cosine similarity between embeddings
        similarity = util.cos_sim(embedding1, embedding2)
        return float(similarity[0][0])  # Extract scalar value
