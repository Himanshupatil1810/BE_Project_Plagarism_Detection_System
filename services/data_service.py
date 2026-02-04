import os
import sqlite3
import pandas as pd
import wikipediaapi

# ======================
# Database Helper Class
# ======================
class Database:
    def __init__(self, db_path="data/database.db"):
        # The path should be relative to the project root, not '..'
        # This assumes 'data' folder is in the same directory as 'app.py'
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_table()

    def create_table(self):
        # Step 1: Create main tables
        
        # Documents table for reference corpus
        documents_query = """
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            source TEXT,
            doc_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.conn.execute(documents_query)
        
        # Plagiarism reports table
        reports_query = """
        CREATE TABLE IF NOT EXISTS plagiarism_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_hash TEXT UNIQUE,
            document_hash TEXT,
            document_content TEXT,
            overall_score REAL,
            tfidf_score REAL,
            bert_score REAL,
            sources TEXT,
            metadata TEXT,
            blockchain_tx_hash TEXT,
            ipfs_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.conn.execute(reports_query)
        
        # User submissions table
        submissions_query = """
        CREATE TABLE IF NOT EXISTS user_submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            file_path TEXT,
            file_hash TEXT,
            user_id TEXT,
            report_id INTEGER,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (report_id) REFERENCES plagiarism_reports (id)
        )
        """
        self.conn.execute(submissions_query)
        
        # Step 2: Create indexes for performance
        try:
            # Index on source for faster filtering
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_documents_source ON documents(source)")
            # Index on doc_type for faster filtering
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_documents_type ON documents(doc_type)")
            # Index on created_at for time-based queries
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_documents_created ON documents(created_at)")
            print("[DB] Database indexes created for large dataset optimization")
        except Exception as e:
            print(f"[DB] Index creation warning: {str(e)}")
        
        # Step 3: Create the FTS5 virtual table
        print("[DB] Initializing Full-Text Search (FTS5) table...")
        fts_query = """
        CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
            title, 
            content, 
            source, 
            doc_type,
            -- This links the 'rowid' of this table to the 'id' of the documents table
            content='documents', 
            content_rowid='id'
        );
        """
        self.conn.execute(fts_query)

        # Step 4: Create triggers to keep FTS table in sync (FIXED)
        
        # Trigger for INSERTs
        insert_trigger_query = """
        CREATE TRIGGER IF NOT EXISTS documents_fts_insert_sync AFTER INSERT ON documents
        BEGIN
            INSERT INTO documents_fts(rowid, title, content, source, doc_type)
            VALUES (NEW.id, NEW.title, NEW.content, NEW.source, NEW.doc_type);
        END;
        """
        self.conn.execute(insert_trigger_query)

        # Trigger for DELETEs
        delete_trigger_query = """
        CREATE TRIGGER IF NOT EXISTS documents_fts_delete_sync AFTER DELETE ON documents
        BEGIN
            -- Delete the entry from the FTS table when a document is deleted
            DELETE FROM documents_fts WHERE rowid = OLD.id;
        END;
        """
        self.conn.execute(delete_trigger_query)

        # Trigger for UPDATEs
        update_trigger_query = """
        CREATE TRIGGER IF NOT EXISTS documents_fts_update_sync AFTER UPDATE ON documents
        BEGIN
            -- Delete the old record and insert the new one to reflect the update
            DELETE FROM documents_fts WHERE rowid = OLD.id;
            INSERT INTO documents_fts(rowid, title, content, source, doc_type)
            VALUES (NEW.id, NEW.title, NEW.content, NEW.source, NEW.doc_type);
        END;
        """
        self.conn.execute(update_trigger_query)
        
        print("[DB] FTS5 table and triggers created successfully.")
        
        # Step 5: Commit all changes
        self.conn.commit()

    def add_document(self, title, content, source="manual", doc_type="reference"):
        """Insert a document into DB"""
        query = "INSERT INTO documents (title, content, source, doc_type) VALUES (?, ?, ?, ?)"
        self.conn.execute(query, (title, content, source, doc_type))
        self.conn.commit()

    def fetch_all_documents(self):
        """Fetch all stored docs"""
        query = "SELECT id, title, content, source, doc_type FROM documents"
        return self.conn.execute(query).fetchall()

    def add_plagiarism_report(self, report_hash, document_hash, document_content, 
                             overall_score, tfidf_score, bert_score, sources, 
                             metadata, blockchain_tx_hash=None, ipfs_hash=None):
        """Insert a plagiarism report into DB"""
        query = """INSERT INTO plagiarism_reports 
                   (report_hash, document_hash, document_content, overall_score, 
                    tfidf_score, bert_score, sources, metadata, blockchain_tx_hash, ipfs_hash) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        self.conn.execute(query, (report_hash, document_hash, document_content, 
                                 overall_score, tfidf_score, bert_score, sources, 
                                 metadata, blockchain_tx_hash, ipfs_hash))
        self.conn.commit()

    # Updated by me
    def update_blockchain_tx(self, report_hash, blockchain_tx_hash):
        query = """
            UPDATE plagiarism_reports
            SET blockchain_tx_hash = ?
            WHERE report_hash = ?
        """
        self.conn.execute(query, (blockchain_tx_hash, report_hash))
        self.conn.commit()


    def update_ipfs_hash(self, report_hash, ipfs_hash):
        query = """
            UPDATE plagiarism_reports
            SET ipfs_hash = ?
            WHERE report_hash = ?
        """
        self.conn.execute(query, (ipfs_hash, report_hash))
        self.conn.commit()

    #till here
    
    def get_plagiarism_report(self, report_hash):
        """Get plagiarism report by hash"""
        query = "SELECT * FROM plagiarism_reports WHERE report_hash = ?"
        return self.conn.execute(query, (report_hash,)).fetchone()

    def get_all_plagiarism_reports(self):
        """Get all plagiarism reports"""
        query = "SELECT * FROM plagiarism_reports ORDER BY created_at DESC"
        return self.conn.execute(query).fetchall()

    def add_user_submission(self, filename, file_path, file_hash, user_id, report_id=None, status='pending'):
        """Add user submission record"""
        query = """INSERT INTO user_submissions 
                   (filename, file_path, file_hash, user_id, report_id, status) 
                   VALUES (?, ?, ?, ?, ?, ?)"""
        self.conn.execute(query, (filename, file_path, file_hash, user_id, report_id, status))
        self.conn.commit()

    def update_submission_status(self, submission_id, status, report_id=None):
        """Update submission status"""
        query = "UPDATE user_submissions SET status = ?, report_id = ? WHERE id = ?"
        self.conn.execute(query, (status, report_id, submission_id))
        self.conn.commit()

    def get_user_submissions(self, user_id=None):
        """Get user submissions"""
        if user_id:
            query = "SELECT * FROM user_submissions WHERE user_id = ? ORDER BY created_at DESC"
            return self.conn.execute(query, (user_id,)).fetchall()
        else:
            query = "SELECT * FROM user_submissions ORDER BY created_at DESC"
            return self.conn.execute(query).fetchall()

    def get_plagiarism_report_by_id(self, report_id):
        """Get plagiarism report by ID"""
        query = "SELECT * FROM plagiarism_reports WHERE id = ?"
        return self.conn.execute(query, (report_id,)).fetchone()

    def get_connection(self):
        """Get a fresh database connection for thread safety"""
        return sqlite3.connect(self.db_path, check_same_thread=False)
    
    def close(self):
        self.conn.close()


# ======================
# Data Collector Class
# ======================
class DataCollector:
    def __init__(self, db: Database):
        self.db = db
        self.wiki = wikipediaapi.Wikipedia(
            user_agent="PlagiarismDetectionSystem/1.0 (Educational Project)",
            language="en"
        )

    def add_from_wikipedia(self, topics):
        """Fetch Wikipedia articles for given topics and store them"""
        for topic in topics:
            page = self.wiki.page(topic)
            if page.exists():
                self.db.add_document(
                    title=page.title,
                    content=page.text,
                    source="wikipedia",
                    doc_type="reference"
                )
                print(f"[Data] Added Wikipedia article: {page.title}")
            else:
                print(f"❌ Page not found: {topic}")

    def add_from_pan_dataset(self, dataset_path="../data/raw/pan_dataset.csv"):
        """Load PAN dataset and store it"""
        if not os.path.exists(dataset_path):
            print("[Data] PAN dataset not found at", dataset_path)
            return

        df = pd.read_csv(dataset_path)

        for idx, row in df.iterrows():
            title = f"PAN_{idx}"
            content = row.get("text", "") or row.get("content", "")
            if content:
                self.db.add_document(
                    title=title,
                    content=content,
                    source="PAN",
                    doc_type="reference"
                )
        print(f"[Data] Added {len(df)} documents from PAN dataset")

    def add_from_arxiv(self, categories, max_results=50):
        """Fetch papers from arXiv and store them"""
        try:
            import arxiv
            
            for category in categories:
                print(f"[Data] Fetching papers from {category}...")
                
                # Search for papers in the category
                search = arxiv.Search(
                    query=f"cat:{category}",
                    max_results=max_results,
                    sort_by=arxiv.SortCriterion.Relevance
                )
                
                count = 0
                for paper in search.results():
                    try:
                        # Get paper details
                        title = paper.title
                        abstract = paper.summary
                        authors = ", ".join([author.name for author in paper.authors])
                        
                        # Combine title, authors, and abstract
                        content = f"Title: {title}\nAuthors: {authors}\nAbstract: {abstract}"
                        
                        self.db.add_document(
                            title=title,
                            content=content,
                            source="arxiv",
                            doc_type="reference"
                        )
                        count += 1
                        
                    except Exception as e:
                        print(f"[Data] Error processing paper: {str(e)}")
                        continue
                
                print(f"[Data] Added {count} papers from {category}")
                
        except ImportError:
            print("[Data] arxiv package not installed. Install with: pip install arxiv")
        except Exception as e:
            print(f"[Data] Error fetching arXiv papers: {str(e)}")

    def add_sample_academic_papers(self):
        """Add sample academic papers for testing"""
        sample_papers = [
            {
                "title": "Introduction to Machine Learning",
                "content": "Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from data. It involves training models on datasets to make predictions or decisions without being explicitly programmed for every task. Common techniques include supervised learning, unsupervised learning, and reinforcement learning."
            },
            {
                "title": "Deep Learning Fundamentals",
                "content": "Deep learning is a subset of machine learning that uses neural networks with multiple layers to model and understand complex patterns in data. It has revolutionized fields like computer vision, natural language processing, and speech recognition. Key architectures include convolutional neural networks (CNNs) and recurrent neural networks (RNNs)."
            },
            {
                "title": "Natural Language Processing Techniques",
                "content": "Natural Language Processing (NLP) is a field of artificial intelligence that focuses on the interaction between computers and human language. It involves tasks like text classification, sentiment analysis, machine translation, and question answering. Modern NLP relies heavily on transformer architectures and pre-trained language models."
            },
            {
                "title": "Computer Vision Applications",
                "content": "Computer vision is a field of artificial intelligence that enables computers to interpret and understand visual information from the world. It involves tasks like image classification, object detection, image segmentation, and facial recognition. Deep learning has significantly advanced the capabilities of computer vision systems."
            },
            {
                "title": "Blockchain Technology Overview",
                "content": "Blockchain is a distributed ledger technology that maintains a continuously growing list of records, called blocks, which are linked and secured using cryptography. It provides a decentralized and immutable way to record transactions and has applications in cryptocurrency, supply chain management, and digital identity verification."
            }
        ]
        
        for paper in sample_papers:
            self.db.add_document(
                title=paper["title"],
                content=paper["content"],
                source="sample",
                doc_type="reference"
            )
        
        print(f"[Data] Added {len(sample_papers)} sample academic papers")