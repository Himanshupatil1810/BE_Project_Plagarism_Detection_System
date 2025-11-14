# Presentation Content for Plagiarism Detection System

## 1. Proposed System / Methodology

### Overview
Our system uses a **hybrid approach** combining traditional text matching with AI-powered semantic analysis to detect plagiarism accurately and efficiently.

### Core Methodology

#### **Two-Stage Detection Process**

**Stage 1: Fast Candidate Selection**
- Uses **Full-Text Search (FTS5)** to quickly find potential matches
- Extracts key terms from the uploaded document
- Searches through 27,000+ reference documents in seconds
- Selects top 100 most relevant candidates for detailed analysis
- **Benefit**: Reduces processing time from hours to minutes

**Stage 2: Detailed Similarity Analysis**
- Compares uploaded document with selected candidates using two methods:
  - **TF-IDF Method**: Detects exact copy-paste and word-for-word matches
  - **BERT AI Method**: Detects paraphrased content and semantic similarity
- Calculates similarity scores (0% to 100%) for each comparison
- Identifies specific plagiarized sections and their sources

#### **Dual Detection Methods**

**1. TF-IDF (Traditional Method)**
- **Purpose**: Catches direct copying and word-for-word plagiarism
- **How it works**: Converts text into numerical vectors and compares them
- **Best for**: Exact matches, copied sentences, unchanged content
- **Weight**: 40% of final score

**2. BERT AI (Advanced Method)**
- **Purpose**: Catches paraphrased and reworded plagiarism
- **How it works**: Uses AI to understand meaning, not just words
- **Best for**: Rephrased content, changed word order, semantic similarity
- **Weight**: 60% of final score

#### **Blockchain Integration**
- Stores plagiarism reports on blockchain for tamper-proof verification
- Ensures reports cannot be modified after creation
- Provides transparent and verifiable results
- Uses IPFS for decentralized document storage

### Key Advantages
✅ **Fast**: Processes large databases (27k+ documents) in minutes
✅ **Accurate**: Combines two detection methods for comprehensive analysis
✅ **Smart**: AI understands meaning, not just word matching
✅ **Secure**: Blockchain ensures report integrity
✅ **Scalable**: Handles growing document databases efficiently

---

## 2. Design and Implementation

### System Architecture

```
┌─────────────────┐
│   User Uploads  │
│   Document      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  File Parser    │  ← Extracts text from PDF, DOCX, TXT
│  Text Cleaner   │  ← Removes noise, normalizes text
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Stage 1: FTS   │  ← Fast candidate selection (Top 100)
│  Search Engine  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Stage 2:       │
│  TF-IDF Checker│  ← Traditional similarity (40% weight)
│  BERT Checker  │  ← AI semantic similarity (60% weight)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Report         │  ← Generates detailed plagiarism report
│  Generator      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Blockchain     │  ← Stores report hash for verification
│  IPFS Storage   │  ← Stores full report data
│  Database       │  ← Saves report details
└─────────────────┘
```

### Component Breakdown

#### **1. Frontend Layer**
- **Technology**: HTML, JavaScript
- **Function**: User interface for document upload
- **Features**: File upload, progress display, report viewing

#### **2. Backend API Layer**
- **Technology**: Flask (Python web framework)
- **Function**: RESTful API endpoints
- **Key Endpoints**:
  - `POST /check` - Upload and check document
  - `GET /reports/<id>` - View report details
  - `GET /verify/<hash>` - Verify report on blockchain
  - `GET /stats` - System statistics

#### **3. Detection Engine**
- **PlagiarismService**: Main orchestrator
  - Coordinates file parsing, text cleaning, candidate search
  - Manages TF-IDF and BERT detection methods
  - Generates comprehensive reports

#### **4. Detection Models**
- **TFIDFChecker**: 
  - Uses scikit-learn's TfidfVectorizer
  - Cosine similarity calculation
  - Fast and efficient for exact matches

- **BERTChecker**:
  - Uses Sentence-BERT model (all-MiniLM-L6-v2)
  - Converts text to semantic embeddings
  - Detects meaning-based similarities

#### **5. Data Layer**
- **Database**: SQLite with FTS5 (Full-Text Search)
  - Stores 27,000+ reference documents
  - Fast indexed searches
  - Plagiarism reports storage

- **Data Sources**:
  - Wikipedia articles
  - arXiv research papers
  - PAN dataset (plagiarism benchmark)
  - Sample academic papers

#### **6. Blockchain Integration**
- **BlockchainService**: 
  - Connects to Ethereum/Polygon network
  - Stores report hashes in smart contracts
  - Enables tamper-proof verification

- **IPFSService**:
  - Decentralized file storage
  - Stores full report data
  - Reduces blockchain storage costs

#### **7. Report Generation**
- **ReportService**:
  - Calculates overall plagiarism score
  - Identifies plagiarized sections
  - Ranks sources by similarity
  - Provides recommendations
  - Generates detailed JSON reports

### Implementation Details

#### **File Processing**
- Supports multiple formats: PDF, DOCX, TXT
- Text extraction and cleaning pipeline
- Handles encoding issues and special characters

#### **Optimization Strategies**
- **FTS5 Indexing**: Fast candidate selection (Stage 1)
- **Batch Processing**: Processes top 100 candidates only
- **Thread Safety**: Fresh database connections for concurrent requests
- **Caching**: Reuses model instances (BERT, TF-IDF)

#### **Security Features**
- Document hashing (SHA-256) for integrity
- Blockchain verification for report authenticity
- User submission tracking
- Report immutability

### Technology Stack

**Backend:**
- Python 3.8+
- Flask (Web Framework)
- SQLite with FTS5 (Database)
- scikit-learn (TF-IDF)
- sentence-transformers (BERT)

**AI/ML:**
- Sentence-BERT (all-MiniLM-L6-v2)
- TF-IDF Vectorization
- Cosine Similarity

**Blockchain:**
- Web3.py (Ethereum integration)
- Solidity Smart Contracts
- IPFS (Decentralized Storage)

**Data Processing:**
- NLTK (Text preprocessing)
- pdfplumber (PDF parsing)
- python-docx (DOCX parsing)

### System Flow Example

1. **User uploads document** → File saved to uploads folder
2. **Text extraction** → Content extracted from PDF/DOCX/TXT
3. **Text cleaning** → Normalized, stemmed, stopwords removed
4. **FTS search** → Finds top 100 candidate documents
5. **TF-IDF comparison** → Calculates similarity with each candidate
6. **BERT comparison** → Calculates semantic similarity
7. **Score calculation** → Weighted average (40% TF-IDF + 60% BERT)
8. **Report generation** → Creates detailed JSON report
9. **Storage** → Saves to database, blockchain, and IPFS
10. **Response** → Returns plagiarism percentage and details

### Performance Metrics
- **Processing Speed**: 100 documents analyzed in ~2-5 minutes
- **Database Size**: Handles 27,000+ reference documents
- **Accuracy**: Dual-method approach improves detection rate
- **Scalability**: Optimized for large document collections

