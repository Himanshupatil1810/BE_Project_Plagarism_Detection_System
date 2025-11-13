import os
import re
import random
from tqdm import tqdm
import pandas as pd
import nltk
from nltk.corpus import wordnet
from sklearn.utils import shuffle
import arxiv

nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)


# ---------------------------------------------------
# ✅ CLEAN TEXT
# ---------------------------------------------------
def clean_text(t):
    t = re.sub(r'\s+', ' ', t)
    return t.strip()


# ---------------------------------------------------
# ✅ CHUNK TEXT
# ---------------------------------------------------
def chunk_text(text, words_per_chunk=200, overlap=50):
    tokens = nltk.word_tokenize(text)
    chunks = []
    i = 0
    while i < len(tokens):
        chunk = tokens[i:i + words_per_chunk]
        if len(chunk) > 50:
            chunks.append(' '.join(chunk))
        i += (words_per_chunk - overlap)
    return [clean_text(c) for c in chunks]


# ---------------------------------------------------
# ✅ PARAPHRASING
# ---------------------------------------------------
def simple_paraphrase_swap_sentences(text):
    sents = nltk.sent_tokenize(text)
    if len(sents) <= 1:
        return text
    random.shuffle(sents)
    return ' '.join(sents)


def synonym_replace(text, p=0.07):
    tokens = nltk.word_tokenize(text)
    new_tokens = []
    for tok in tokens:
        if random.random() < p:
            syns = wordnet.synsets(tok)
            if syns:
                lemmas = [l.name().replace("_", " ") for s in syns for l in s.lemmas()]
                if lemmas:
                    new_tokens.append(random.choice(lemmas))
                    continue
        new_tokens.append(tok)
    return ' '.join(new_tokens)


# ---------------------------------------------------
# ✅ FETCH ARXIV
# ---------------------------------------------------
def fetch_arxiv_papers(query_list, per_query=200):
    docs = []
    for q in query_list:
        try:
            search = arxiv.Search(
                query=q,
                max_results=per_query,
                sort_by=arxiv.SortCriterion.SubmittedDate
            )
            for r in search.results():
                try:
                    txt = f"{r.title}\n\n{r.summary}"
                    docs.append((r.entry_id, clean_text(txt)))
                except:
                    pass
        except:
            pass
    return docs


# ---------------------------------------------------
# ✅ BUILD DATASET
# ---------------------------------------------------
def build_dataset(query_list, target_rows=10000):

    print("✅ Fetching arXiv content...\n")
    arxiv_docs = fetch_arxiv_papers(query_list, per_query=200)
    print(f"✔ Retrieved {len(arxiv_docs)} arXiv papers")

    source_chunks = []
    for title, txt in arxiv_docs:
        chunks = chunk_text(txt)
        for c in chunks:
            source_chunks.append((title, c))

    print(f"✔ Total chunks extracted: {len(source_chunks)}")

    rows = []

    # -------- Positive examples --------
    sample_n = min(len(source_chunks), 3000)
    for title, txt in random.sample(source_chunks, sample_n):
        p1 = simple_paraphrase_swap_sentences(txt)
        p2 = synonym_replace(txt, p=0.10)
        rows.append((txt, p1, 1))
        rows.append((txt, p2, 1))

    # -------- Negative examples --------
    for _ in range(6000):
        a = random.choice(source_chunks)[1]
        b = random.choice(source_chunks)[1]
        if a != b:
            rows.append((a, b, 0))

    df = pd.DataFrame(rows, columns=["text1", "text2", "label"])
    df = df.dropna().reset_index()

    # Force target size
    if len(df) < target_rows:
        repeat = (target_rows // len(df)) + 1
        df = pd.concat([df] * repeat, ignore_index=True)

    df = df.sample(target_rows, random_state=42).reset_index(drop=True)
    return df


# ---------------------------------------------------
# ✅ MAIN
# ---------------------------------------------------
if __name__ == "__main__":

    # ✅ ~150+ arXiv topics
    arxiv_queries = [
        "machine learning", "natural language processing", "deep learning",
        "artificial intelligence", "robotics", "data science", "quantum computing",
        "bioinformatics", "cybersecurity", "neural networks", "large language model",
        "recommender systems", "computer vision", "signal processing",
        "graph learning", "reinforcement learning", "pattern recognition",
        "computational linguistics", "optimization", "speech processing",
        "knowledge graphs", "big data", "data mining", "explainable AI",
        "systems ML", "HCI", "software engineering", "blockchain", "cryptography",
        "edge computing", "distributed systems", "multi agent learning",
        "computer graphics", "IoT", "AR VR", "autonomous vehicles",
        "diffusion models", "GAN", "transformer", "foundation models",
        "bio-signal processing", "medical imaging", "disease prediction",
        "computational biology", "astronomy ML", "astrophysics ML",
        "quantum ML", "federated learning", "secure ML", "adversarial ML",
        "model compression", "pruning", "distillation", "vision transformers",
        "summarization", "text classification", "zero-shot learning",
        "few-shot learning", "semantic search", "embedding models"
    ]

    print("\n✅ Building arXiv dataset...")
    df = build_dataset(arxiv_queries, target_rows=10000)

    df.to_csv("arxiv_train_pairs.csv", index=False)
    print("\n🎉 DONE — Saved 10,000+ rows → arxiv_train_pairs.csv")
