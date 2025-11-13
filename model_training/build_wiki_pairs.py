import os
import re
import random
from tqdm import tqdm
import pandas as pd
import nltk
from nltk.corpus import wordnet
from sklearn.utils import shuffle
import wikipedia

# Download required NLP models
nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)


# ---------------------------------------------------
# ✅ CLEAN TEXT
# ---------------------------------------------------
def clean_text(t):
    t = re.sub(r'\s+', ' ', t)
    t = re.sub(r'\[\d+\]', '', t)   # remove [1] citations
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


def synonym_replace(text, p=0.08):
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
# ✅ FETCH WIKIPEDIA WITH RETRY + TITLE FILTER
# ---------------------------------------------------
def fetch_wikipedia_pages(keywords, per_topic=20):
    docs = []
    seen_titles = set()

    for k in keywords:
        try:
            results = wikipedia.search(k, results=per_topic)
        except:
            continue

        for t in results:
            if t in seen_titles:
                continue
            seen_titles.add(t)

            try:
                page = wikipedia.page(t, auto_suggest=False)
                docs.append((t, clean_text(page.content)))
            except:
                try:
                    page = wikipedia.page(t)
                    docs.append((t, clean_text(page.content)))
                except:
                    pass

    return docs


# ---------------------------------------------------
# ✅ BUILD DATASET
# ---------------------------------------------------
def build_dataset(keywords, target_rows=10000):

    print("✅ Fetching Wikipedia content...\n")

    wiki_docs = fetch_wikipedia_pages(keywords, per_topic=25)
    print(f"✔ Retrieved {len(wiki_docs)} wiki articles")

    source_chunks = []

    # Extract text chunks
    for title, txt in wiki_docs:
        chunks = chunk_text(txt)
        for c in chunks:
            source_chunks.append((title, c))

    print(f"✔ Total chunks extracted: {len(source_chunks)}")

    # Prevent empty issue
    if len(source_chunks) == 0:
        print("❌ ERROR: No text extracted. Exiting.")
        return pd.DataFrame(columns=["text1", "text2", "label"])

    rows = []

    # -------- Positive examples --------
    sample_n = min(len(source_chunks), 3000)
    for title, txt in random.sample(source_chunks, sample_n):
        p1 = simple_paraphrase_swap_sentences(txt)
        p2 = synonym_replace(txt, p=0.12)
        rows.append((txt, p1, 1))
        rows.append((txt, p2, 1))

    # -------- Negative examples --------
    for _ in range(6000):
        a = random.choice(source_chunks)[1]
        b = random.choice(source_chunks)[1]
        if a != b:
            rows.append((a, b, 0))

    df = pd.DataFrame(rows, columns=["text1", "text2", "label"])
    df = df.dropna().reset_index(drop=True)

    # Guarantee size
    if len(df) < target_rows:
        repeat = (target_rows // len(df)) + 1
        df = pd.concat([df] * repeat, ignore_index=True)

    df = df.sample(target_rows, random_state=42).reset_index(drop=True)
    return df


# ---------------------------------------------------
# ✅ MAIN
# ---------------------------------------------------
if __name__ == "__main__":

    # ✅ Verified broader topic list
    wiki_keywords = [
        "Machine learning","Deep learning","Artificial intelligence",
        "Neural networks","Reinforcement learning","Cryptography",
        "Data mining","Software engineering","Cybersecurity",
        "Data science","Computer vision","NLP","Robotics",
        "Quantum computing","Operating system","Database","Genomics",
        "Medical imaging","Astronomy","Physics","Chemistry","Biology",
        "Statistics","Signal processing","Algorithm","Optimization",
        "Computer architecture","Blockchain","Cloud computing",
        "Distributed systems","Game theory","Compiler","Autonomous car",
        "Internet of Things","Edge computing","Data privacy","Copyright",
        "Research paper","Text generation","Knowledge graph",
        "Speech recognition","Image recognition","Topic modeling",
        "Summarization","GAN","Transformer","LLM","Diffusion model",
        "Bioinformatics","Quantum mechanics","Astrophysics","Big data",
        "Vision transformer","Genetic algorithm"
    ]

    print("\n✅ Building dataset...")
    df = build_dataset(wiki_keywords, target_rows=10000)

    df.to_csv("wiki_train_pairs.csv", index=False)
    print("\n🎉 DONE — Saved → wiki_train_pairs.csv (10,000 rows)")
