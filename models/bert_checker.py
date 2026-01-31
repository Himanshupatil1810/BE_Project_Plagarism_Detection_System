"""
Semantic similarity checker using Sentence-BERT.

On some Windows setups, PyTorch DLLs may fail to load (WinError 1114).
In that case we gracefully disable BERT-based checks so the rest of
the system (TF-IDF, blockchain, IPFS, API) continues to work.
"""

from typing import Optional

try:
    from sentence_transformers import SentenceTransformer, util  # type: ignore

    _BERT_AVAILABLE = True
except Exception as e:  # ImportError, OSError, etc.
    # Avoid hard crash when torch DLLs are missing/broken.
    print(f"[BERT] Disabled: could not load SentenceTransformer ({e})")
    SentenceTransformer = None  # type: ignore
    util = None  # type: ignore
    _BERT_AVAILABLE = False


class BERTChecker:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize with a pretrained Sentence-BERT model if available.
        """
        self.model_name = model_name
        self.model: Optional["SentenceTransformer"] = None  # type: ignore

        if _BERT_AVAILABLE:
            try:
                self.model = SentenceTransformer(model_name)  # type: ignore
                print(f"[BERT] Loaded model: {model_name}")
            except Exception as e:
                print(f"[BERT] Failed to load model '{model_name}': {e}")
                self.model = None
        else:
            print("[BERT] Running in disabled mode (similarity will be 0.0)")

    def calculate_similarity(self, doc1: str, doc2: str) -> float:
        """
        Takes two documents and returns semantic similarity score (0–1).
        Falls back to 0.0 if BERT is not available.
        """
        if not self.model or not _BERT_AVAILABLE or util is None:
            return 0.0

        # Encode texts into dense embeddings
        embedding1 = self.model.encode(doc1, convert_to_tensor=True)
        embedding2 = self.model.encode(doc2, convert_to_tensor=True)

        # Compute cosine similarity between embeddings
        similarity = util.cos_sim(embedding1, embedding2)
        return float(similarity[0][0])  # Extract scalar value
