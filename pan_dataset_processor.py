#!/usr/bin/env python3
"""
PAN Dataset 2011 Processor
Handles different PAN dataset formats and integrates with our plagiarism detection system
"""

import os
import csv
import xml.etree.ElementTree as ET
import pandas as pd
from services.data_service import Database, DataCollector

class PANDatasetProcessor:
    def __init__(self, db_path="data/database.db"):
        self.db = Database(db_path)
        self.collector = DataCollector(self.db)
    
    def process_pan_dataset_csv(self, file_path):
        """Process PAN dataset in CSV format"""
        print(f"📊 Processing PAN dataset CSV: {file_path}")
        
        try:
            df = pd.read_csv(file_path)
            print(f"   Found {len(df)} records")
            
            # Common column names in PAN datasets
            text_columns = ['text', 'content', 'document', 'suspicious_text', 'original_text']
            title_columns = ['title', 'filename', 'id', 'document_id']
            
            # Find the text column
            text_col = None
            for col in text_columns:
                if col in df.columns:
                    text_col = col
                    break
            
            if not text_col:
                print("❌ No text column found. Available columns:", df.columns.tolist())
                return False
            
            # Find title column
            title_col = None
            for col in title_columns:
                if col in df.columns:
                    title_col = col
                    break
            
            if not title_col:
                title_col = 'id'  # Use index as title
            
            # Process each document
            added_count = 0
            for idx, row in df.iterrows():
                try:
                    content = str(row[text_col])
                    title = str(row[title_col]) if title_col in row else f"PAN_2011_{idx}"
                    
                    # Clean and validate content
                    if len(content.strip()) > 50:  # Minimum content length
                        self.db.add_document(
                            title=f"PAN_2011_{title}",
                            content=content,
                            source="PAN_2011",
                            doc_type="reference"
                        )
                        added_count += 1
                        
                        if added_count % 100 == 0:
                            print(f"   Processed {added_count} documents...")
                            
                except Exception as e:
                    print(f"   ⚠️ Error processing row {idx}: {str(e)}")
                    continue
            
            print(f"✅ Successfully added {added_count} documents from PAN dataset")
            return True
            
        except Exception as e:
            print(f"❌ Error processing PAN dataset: {str(e)}")
            return False
    
    def process_pan_dataset_xml(self, file_path):
        """Process PAN dataset in XML format"""
        print(f"📊 Processing PAN dataset XML: {file_path}")
        
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            added_count = 0
            
            # Common XML structures in PAN datasets
            for doc in root.findall('.//document'):
                try:
                    # Try different possible text elements
                    text_elements = ['text', 'content', 'body', 'suspicious_text', 'original_text']
                    content = None
                    
                    for elem in text_elements:
                        text_elem = doc.find(elem)
                        if text_elem is not None and text_elem.text:
                            content = text_elem.text.strip()
                            break
                    
                    if content and len(content) > 50:
                        # Get title/ID
                        title = doc.get('id', f"PAN_2011_{added_count}")
                        if 'title' in doc.attrib:
                            title = doc.attrib['title']
                        
                        self.db.add_document(
                            title=f"PAN_2011_{title}",
                            content=content,
                            source="PAN_2011",
                            doc_type="reference"
                        )
                        added_count += 1
                        
                        if added_count % 100 == 0:
                            print(f"   Processed {added_count} documents...")
                            
                except Exception as e:
                    print(f"   ⚠️ Error processing document: {str(e)}")
                    continue
            
            print(f"✅ Successfully added {added_count} documents from PAN dataset")
            return True
            
        except Exception as e:
            print(f"❌ Error processing PAN dataset: {str(e)}")
            return False
    
    def process_pan_dataset_txt(self, directory_path):
        """Process PAN dataset in TXT format (multiple files)"""
        print(f"📊 Processing PAN dataset TXT directory: {directory_path}")
        
        try:
            added_count = 0
            
            for filename in os.listdir(directory_path):
                if filename.endswith('.txt'):
                    file_path = os.path.join(directory_path, filename)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read().strip()
                        
                        if len(content) > 50:
                            self.db.add_document(
                                title=f"PAN_2011_{filename}",
                                content=content,
                                source="PAN_2011",
                                doc_type="reference"
                            )
                            added_count += 1
                            
                            if added_count % 100 == 0:
                                print(f"   Processed {added_count} documents...")
                                
                    except Exception as e:
                        print(f"   ⚠️ Error processing {filename}: {str(e)}")
                        continue
            
            print(f"✅ Successfully added {added_count} documents from PAN dataset")
            return True
            
        except Exception as e:
            print(f"❌ Error processing PAN dataset: {str(e)}")
            return False
    
    def auto_detect_and_process(self, path):
        """Auto-detect PAN dataset format and process accordingly"""
        print(f"🔍 Auto-detecting PAN dataset format at: {path}")
        
        if os.path.isfile(path):
            if path.endswith('.csv'):
                return self.process_pan_dataset_csv(path)
            elif path.endswith('.xml'):
                return self.process_pan_dataset_xml(path)
            else:
                print("❌ Unsupported file format. Please provide CSV or XML file.")
                return False
        elif os.path.isdir(path):
            return self.process_pan_dataset_txt(path)
        else:
            print("❌ Path not found.")
            return False
    
    def get_dataset_stats(self):
        """Get statistics about the loaded dataset"""
        docs = self.db.fetch_all_documents()
        
        print("\n📊 Dataset Statistics:")
        print(f"   Total documents: {len(docs)}")
        
        # Count by source
        sources = {}
        for doc in docs:
            source = doc[3]  # source column
            sources[source] = sources.get(source, 0) + 1
        
        print("\n📈 Breakdown by source:")
        for source, count in sources.items():
            print(f"   {source}: {count} documents")
        
        # Count PAN dataset specifically
        pan_docs = [doc for doc in docs if doc[3] == "PAN_2011"]
        print(f"\n🎯 PAN 2011 Dataset: {len(pan_docs)} documents")
        
        return len(docs), sources

def main():
    """Main function to process PAN dataset"""
    print("🚀 PAN Dataset 2011 Processor")
    print("=" * 50)
    
    processor = PANDatasetProcessor()
    
    # Ask user for PAN dataset path
    print("\n📁 Please provide the path to your PAN dataset 2011:")
    print("   - For CSV file: path/to/dataset.csv")
    print("   - For XML file: path/to/dataset.xml") 
    print("   - For TXT directory: path/to/dataset/folder")
    
    # For now, let's try common locations
    possible_paths = [
        "data/raw/pan_dataset_2011.csv",
        "data/raw/pan_dataset_2011.xml",
        "data/raw/pan_dataset_2011/",
        "pan_dataset_2011.csv",
        "pan_dataset_2011.xml",
        "pan_dataset_2011/"
    ]
    
    found_path = None
    for path in possible_paths:
        if os.path.exists(path):
            found_path = path
            break
    
    if found_path:
        print(f"✅ Found PAN dataset at: {found_path}")
        success = processor.auto_detect_and_process(found_path)
        
        if success:
            processor.get_dataset_stats()
        else:
            print("❌ Failed to process PAN dataset")
    else:
        print("❌ PAN dataset not found in common locations.")
        print("Please place your PAN dataset in one of these locations:")
        for path in possible_paths:
            print(f"   - {path}")
        print("\nOr run this script with the correct path as an argument.")

if __name__ == "__main__":
    main()

