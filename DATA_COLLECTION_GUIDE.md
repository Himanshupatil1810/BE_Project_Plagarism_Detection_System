# 📊 Data Collection Guide - Blockchain + AI Plagiarism Detection System

## 🎯 **Understanding Data Collection Requirements**

### **1. Plagiarism Types We Detect:**
- **Copy-Paste**: Exact text matches (TF-IDF detection)
- **Paraphrasing**: Rephrased content (BERT semantic detection)
- **Rephrased Content**: Similar meaning, different words (AI-powered)

### **2. Blockchain Benefits:**
- **Immutability**: Reports cannot be modified after storage
- **Transparency**: Public verification of all reports
- **Decentralized Verification**: No single point of failure
- **Smart Contracts**: Automated, tamper-proof validation

---

## 📚 **Data Collection Process**

### **Step 1: Database Setup**
```sql
-- Documents table for reference corpus
CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    content TEXT,
    source TEXT,           -- wikipedia, arxiv, PAN_2011, sample
    doc_type TEXT,         -- reference, suspicious, original
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Step 2: Multi-Source Collection**

#### **A. Wikipedia Articles** 📚
```python
# Collects academic articles on various topics
topics = [
    "Artificial Intelligence", "Machine Learning", "Deep Learning",
    "Natural Language Processing", "Computer Vision", "Robotics",
    "Quantum Computing", "Cybersecurity", "Blockchain"
]
```

#### **B. arXiv Research Papers** 📄
```python
# Collects research papers from multiple categories
categories = ["cs.AI", "cs.LG", "cs.CL", "cs.CV"]
# Uses arXiv API to fetch papers
```

#### **C. PAN Dataset 2011** 📊
```python
# Your plagiarism detection benchmark dataset
# Supports CSV, XML, and TXT formats
# Contains original and plagiarized text pairs
```

#### **D. Sample Academic Papers** 🎓
```python
# Curated academic content for testing
# Covers various subjects and writing styles
```

---

## 🔧 **PAN Dataset Integration**

### **Supported Formats:**
1. **CSV Format**: `pan_dataset.csv`
2. **XML Format**: `pan_dataset.xml`
3. **TXT Directory**: Multiple `.txt` files

### **Required Directory Structure:**
```
data/
├── raw/
│   ├── pan_dataset_2011.csv          # Your PAN dataset
│   ├── pan_dataset_2011.xml          # Alternative format
│   └── pan_dataset_2011/             # TXT files directory
├── processed/                        # Processed data
└── database.db                       # SQLite database
```

### **PAN Dataset Processing:**
```python
# Auto-detects format and processes accordingly
processor = PANDatasetProcessor()
processor.auto_detect_and_process("data/raw/pan_dataset_2011.csv")
```

---

## 🚀 **How to Add Your PAN Dataset**

### **Option 1: Place in Recommended Location**
```bash
# Create directory
mkdir -p data/raw

# Copy your PAN dataset to:
data/raw/pan_dataset_2011.csv
# OR
data/raw/pan_dataset_2011.xml
# OR
data/raw/pan_dataset_2011/
```

### **Option 2: Use the Processor Script**
```bash
# Run the PAN dataset processor
python pan_dataset_processor.py

# It will auto-detect your dataset format
```

### **Option 3: Manual Integration**
```python
from pan_dataset_processor import PANDatasetProcessor

processor = PANDatasetProcessor()
processor.auto_detect_and_process("path/to/your/pan_dataset")
```

---

## 📊 **Data Collection Workflow**

### **1. Initialize Database**
```bash
python init_database.py
```

### **2. Collect from All Sources**
```bash
python data_collector.py
```

### **3. Process PAN Dataset**
```bash
python pan_dataset_processor.py
```

### **4. Verify Collection**
```bash
python status.py
```

---

## 🔍 **Data Quality & Validation**

### **Content Validation:**
- **Minimum Length**: 50 characters
- **Encoding**: UTF-8 support
- **Format**: Clean text extraction
- **Duplicates**: Automatic detection and handling

### **Source Tracking:**
- **Wikipedia**: Academic articles
- **arXiv**: Research papers
- **PAN_2011**: Your benchmark dataset
- **Sample**: Curated content

### **Metadata Storage:**
- **Title**: Document identifier
- **Content**: Full text content
- **Source**: Data source origin
- **Type**: Reference/suspicious/original
- **Timestamp**: Collection date

---

## 📈 **Expected Dataset Size**

### **Current Collection:**
- **Wikipedia**: ~19 articles
- **arXiv**: ~50 papers per category
- **Sample**: 5 curated papers
- **PAN_2011**: Your dataset size

### **Target Collection:**
- **Minimum**: 100+ documents
- **Optimal**: 1000+ documents
- **Maximum**: 10,000+ documents

---

## 🛠️ **Database Configuration**

### **No Password Required:**
- **Database**: SQLite (file-based)
- **Location**: `data/database.db`
- **Access**: Direct file access
- **Backup**: Copy the `.db` file

### **Database Features:**
- **ACID Compliance**: Reliable transactions
- **Thread Safety**: Multi-user support
- **Indexing**: Fast text searches
- **Backup**: Easy file copying

---

## 🧪 **Testing Data Collection**

### **Check Current Status:**
```bash
python status.py
```

### **View Database Contents:**
```python
from services.data_service import Database

db = Database("data/database.db")
docs = db.fetch_all_documents()
print(f"Total documents: {len(docs)}")

# Show breakdown by source
sources = {}
for doc in docs:
    source = doc[3]
    sources[source] = sources.get(source, 0) + 1

for source, count in sources.items():
    print(f"{source}: {count} documents")
```

### **Test Plagiarism Detection:**
```bash
python test_api.py
```

---

## 📋 **Next Steps for You**

### **1. Place Your PAN Dataset:**
```bash
# Create the directory
mkdir -p data/raw

# Copy your PAN dataset to one of these locations:
# data/raw/pan_dataset_2011.csv
# data/raw/pan_dataset_2011.xml  
# data/raw/pan_dataset_2011/
```

### **2. Run Data Collection:**
```bash
# Process your PAN dataset
python pan_dataset_processor.py

# Collect from all sources
python data_collector.py
```

### **3. Verify Integration:**
```bash
# Check system status
python status.py

# Test plagiarism detection
python test_api.py
```

---

## ❓ **Questions for You**

1. **What format is your PAN dataset 2011?** (CSV, XML, TXT files)
2. **What's the approximate size?** (number of documents)
3. **Does it contain both original and plagiarized pairs?**
4. **Would you like me to help you place it in the right location?**

---

## 🎯 **Expected Results**

After integrating your PAN dataset, you should see:
- **Increased Reference Corpus**: More documents for comparison
- **Better Detection Accuracy**: More diverse content for training
- **Comprehensive Testing**: Real plagiarism cases for validation
- **Production Ready**: Full dataset for deployment

**Your PAN dataset will significantly enhance our plagiarism detection capabilities!** 🚀

