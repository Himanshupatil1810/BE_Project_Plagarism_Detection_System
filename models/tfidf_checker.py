from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class TFIDFChecker:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()

    def calculate_similarity(self, doc1, doc2):
        """
        Takes two documents (already cleaned) and returns cosine similarity score.
        """
        tfidf_matrix = self.vectorizer.fit_transform([doc1, doc2])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        return similarity[0][0]  # single value between 0 and 1
