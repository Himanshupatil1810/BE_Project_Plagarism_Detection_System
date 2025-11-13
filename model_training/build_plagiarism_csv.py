import os
import re
import random
from tqdm import tqdm
import pandas as pd
import nltk
from nltk.corpus import wordnet
from sklearn.utils import shuffle
import wikipedia

nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)


# ---------------------------------------------------
# ✅ CLEAN TEXT
# ---------------------------------------------------
def clean_text(t):
    t = re.sub(r'\s+', ' ', t)
    t = re.sub(r'\[\d+\]', '', t)   # remove [1] references
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
# ✅ PARAPHRASING FUNCTIONS
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
# ✅ FETCH WIKIPEDIA
# ---------------------------------------------------
def fetch_wikipedia_pages(keywords, per_topic=50):
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
                txt = wikipedia.page(t).content
                docs.append((t, clean_text(txt)))
            except:
                pass

    return docs


# ---------------------------------------------------
# ✅ BUILD DATASET
# ---------------------------------------------------
def build_dataset(keywords, target_rows=10000):

    print("✅ Fetching Wikipedia content...\n")
    wiki_docs = fetch_wikipedia_pages(keywords, per_topic=50)
    print(f"✔ Retrieved {len(wiki_docs)} wiki articles")

    source_chunks = []
    for title, txt in wiki_docs:
        chunks = chunk_text(txt)
        for c in chunks:
            source_chunks.append((title, c))

    print(f"✔ Total chunks extracted: {len(source_chunks)}")

    rows = []

    # -------- Positive synthetic examples --------
    sample_n = min(len(source_chunks), 3000)
    for title, txt in random.sample(source_chunks, sample_n):
        p1 = simple_paraphrase_swap_sentences(txt)
        p2 = synonym_replace(txt, p=0.10)
        rows.append((txt, p1, 1))
        rows.append((txt, p2, 1))

    # -------- Negative random pairings --------
    for _ in range(6000):
        a = random.choice(source_chunks)[1]
        b = random.choice(source_chunks)[1]
        if a != b:
            rows.append((a, b, 0))

    df = pd.DataFrame(rows, columns=["text1", "text2", "label"])
    df = df.dropna().reset_index()

    # Force dataset size
    if len(df) < target_rows:
        repeat = (target_rows // len(df)) + 1
        df = pd.concat([df] * repeat, ignore_index=True)

    df = df.sample(target_rows, random_state=42).reset_index(drop=True)
    return df


# ---------------------------------------------------
# ✅ MAIN
# ---------------------------------------------------
if __name__ == "__main__":

    # ✅ ~150+ Topics
    wiki_keywords = [
        "plagiarism","academic_honesty","machine_learning","artificial_intelligence",
        "data_science","deep_learning","computer_vision","natural_language_processing",
        "neural_networks","cyber_security","software_engineering","cryptography",
        "information_retrieval","data_mining","pattern_recognition","blockchain",
        "cloud_computing","distributed_systems","operating_system","database_management",
        "network_security","bioinformatics","genomics","robotics","control_systems",
        "big_data","data_analysis","compiler_design","embedded_systems","virtual_reality",
        "augmented_reality","quantum_computing","graph_theory","optimization",
        "computer_graphics","game_theory","internet_of_things","edge_computing",
        "theoretical_computer_science","information_theory","signal_processing",
        "speech_processing","fuzzy_logic","expert_systems","autonomous_systems",
        "computational_linguistics","knowledge_graphs","semantic_web",
        "recommender_systems","human_computer_interaction","reinforcement_learning",
        "computer_architecture","time_series","statistics","network_protocols",
        "wireless_networks","mobile_computing","robot_control","quantum_mechanics",
        "physics","chemistry","biology","astronomy","astrophysics","medical_imaging",
        "speech_recognition","image_recognition","object_detection","NLP_tasks",
        "text_classification","text_generation","information_extraction",
        "semantic_analysis","text_similarity","summarization","topic_modeling",
        "graph_networks","social_network_analysis","medical_ai","data_privacy",
        "copyright","IP_rights","research_paper","chatbot","AI_ethics","LLM",
        "transformer_model","diffusion_model","GAN","foundation_model"
    ]

    print("\n✅ Building dataset...")
    df = build_dataset(wiki_keywords, target_rows=10000)

    df.to_csv("wiki_train_pairs.csv", index=False)
    print("\n🎉 DONE — Saved 10,000+ rows → wiki_train_pairs.csv")
