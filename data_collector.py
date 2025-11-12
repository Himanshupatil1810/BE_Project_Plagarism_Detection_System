import os
import sys
import arxiv
import requests
from services.data_service import Database, DataCollector

def collect_comprehensive_dataset():
    """Collect comprehensive dataset from multiple sources"""
    # Init DB + Collector
    db = Database("data/database.db")
    collector = DataCollector(db)

    print("🚀 Starting comprehensive dataset collection...")

    # 1) Add Wikipedia Articles (expanded topics)
    topics = [
        "Artificial Intelligence", "Machine Learning", "Deep Learning", "Natural Language Processing",
        "Computer Vision", "Robotics", "Quantum Computing", "Cybersecurity", "Blockchain",
        "Data Science", "Big Data", "Cloud Computing", "Internet of Things", "Software Engineering",
        "Database Systems", "Computer Networks", "Operating Systems", "Algorithms", "Data Structures"
    ]
    print("📚 Collecting Wikipedia articles...")
    collector.add_from_wikipedia(topics)
    
    # 2) Add arXiv papers
    print("📄 Collecting arXiv papers...")
    collector.add_from_arxiv(["cs.AI", "cs.LG", "cs.CL", "cs.CV"], max_results=50)

    # 3) Load PAN dataset if available
    pan_path = "data/raw/pan_dataset.csv"
    if os.path.exists(pan_path):
        print("📊 Loading PAN dataset...")
        collector.add_from_pan_dataset(pan_path)
    else:
        print("⚠️ PAN dataset not found, skipping...")

    # 4) Add sample academic papers
    print("🎓 Adding sample academic papers...")
    collector.add_sample_academic_papers()

    # 5) Fetch all docs and show statistics
    docs = db.fetch_all_documents()
    print(f"\n📂 Dataset Collection Complete!")
    print(f"📊 Total documents in database: {len(docs)}")
    
    # Show breakdown by source
    sources = {}
    for doc in docs:
        source = doc[3]  # source column
        sources[source] = sources.get(source, 0) + 1
    
    print("\n📈 Breakdown by source:")
    for source, count in sources.items():
        print(f"  {source}: {count} documents")

    db.close()

if __name__ == "__main__":
    collect_comprehensive_dataset()
