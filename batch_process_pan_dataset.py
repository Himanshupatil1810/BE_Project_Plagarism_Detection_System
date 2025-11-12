#!/usr/bin/env python3
"""
Memory-Efficient Batch Processor for Large PAN Dataset
Processes large datasets in small batches to manage memory usage
"""

import os
import gc
import time
from services.data_service import Database

class BatchProcessor:
    def __init__(self, db_path="data/database.db"):
        self.db = Database(db_path)
        self.batch_size = 50  # Small batches for memory efficiency
        self.processed_count = 0
        self.error_count = 0
    
    def process_file_batch(self, file_paths):
        """Process a batch of files"""
        batch_processed = 0
        batch_errors = 0
        
        for file_path in file_paths:
            try:
                # Determine file type and process accordingly
                if file_path.endswith('.csv'):
                    success = self.process_csv_file(file_path)
                elif file_path.endswith('.xml'):
                    success = self.process_xml_file(file_path)
                else:
                    success = self.process_txt_file(file_path)
                
                if success:
                    batch_processed += 1
                else:
                    batch_errors += 1
                    
            except Exception as e:
                print(f"   ⚠️ Error processing {os.path.basename(file_path)}: {str(e)}")
                batch_errors += 1
                continue
        
        return batch_processed, batch_errors
    
    def process_csv_file(self, file_path):
        """Process a single CSV file"""
        try:
            import pandas as pd
            
            # Read CSV in chunks to manage memory
            chunk_size = 1000
            processed = 0
            
            for chunk in pd.read_csv(file_path, chunksize=chunk_size):
                for idx, row in chunk.iterrows():
                    # Find text column
                    text_col = None
                    for col in ['text', 'content', 'document', 'suspicious_text', 'original_text']:
                        if col in chunk.columns:
                            text_col = col
                            break
                    
                    if text_col and len(str(row[text_col]).strip()) > 50:
                        self.db.add_document(
                            title=f"PAN_2011_CSV_{processed}",
                            content=str(row[text_col]),
                            source="PAN_2011",
                            doc_type="reference"
                        )
                        processed += 1
                        
                        if processed % 100 == 0:
                            print(f"     Processed {processed} records from CSV...")
            
            return processed > 0
            
        except Exception as e:
            print(f"   ⚠️ CSV processing error: {str(e)}")
            return False
    
    def process_xml_file(self, file_path):
        """Process a single XML file"""
        try:
            import xml.etree.ElementTree as ET
            
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            processed = 0
            for doc in root.findall('.//document'):
                try:
                    # Find text content
                    text_elements = ['text', 'content', 'body', 'suspicious_text', 'original_text']
                    content = None
                    
                    for elem in text_elements:
                        text_elem = doc.find(elem)
                        if text_elem is not None and text_elem.text:
                            content = text_elem.text.strip()
                            break
                    
                    if content and len(content) > 50:
                        title = doc.get('id', f"PAN_2011_XML_{processed}")
                        self.db.add_document(
                            title=f"PAN_2011_{title}",
                            content=content,
                            source="PAN_2011",
                            doc_type="reference"
                        )
                        processed += 1
                        
                        if processed % 100 == 0:
                            print(f"     Processed {processed} records from XML...")
                            
                except Exception as e:
                    continue
            
            return processed > 0
            
        except Exception as e:
            print(f"   ⚠️ XML processing error: {str(e)}")
            return False
    
    def process_txt_file(self, file_path):
        """Process a single TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().strip()
            
            if len(content) > 50:
                filename = os.path.basename(file_path)
                self.db.add_document(
                    title=f"PAN_2011_{filename}",
                    content=content,
                    source="PAN_2011",
                    doc_type="reference"
                )
                return True
            
            return False
            
        except Exception as e:
            print(f"   ⚠️ TXT processing error: {str(e)}")
            return False
    
    def process_large_dataset(self, extract_dir):
        """Process large dataset in memory-efficient batches"""
        print(f"🔄 Starting memory-efficient batch processing...")
        print(f"📊 Batch size: {self.batch_size} files per batch")
        
        # Find all text files
        text_files = []
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                if file.lower().endswith(('.txt', '.xml', '.csv')):
                    text_files.append(os.path.join(root, file))
        
        print(f"📁 Found {len(text_files)} text files to process")
        
        # Process in batches
        total_batches = (len(text_files) + self.batch_size - 1) // self.batch_size
        print(f"📦 Will process in {total_batches} batches")
        
        start_time = time.time()
        
        for i in range(0, len(text_files), self.batch_size):
            batch_num = (i // self.batch_size) + 1
            batch_files = text_files[i:i + self.batch_size]
            
            print(f"\n🔄 Processing batch {batch_num}/{total_batches} ({len(batch_files)} files)...")
            
            # Process batch
            batch_processed, batch_errors = self.process_file_batch(batch_files)
            
            self.processed_count += batch_processed
            self.error_count += batch_errors
            
            print(f"   ✅ Batch {batch_num} complete: {batch_processed} processed, {batch_errors} errors")
            
            # Memory management
            gc.collect()  # Force garbage collection
            
            # Progress update
            if batch_num % 10 == 0:
                elapsed = time.time() - start_time
                rate = self.processed_count / elapsed if elapsed > 0 else 0
                print(f"   📊 Progress: {self.processed_count} files processed ({rate:.1f} files/sec)")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"\n🎉 Batch processing complete!")
        print(f"   ✅ Successfully processed: {self.processed_count} files")
        print(f"   ❌ Errors: {self.error_count} files")
        print(f"   ⏱️ Total time: {total_time:.1f} seconds")
        print(f"   📊 Average rate: {self.processed_count / total_time:.1f} files/sec")
        
        return self.processed_count

def main():
    """Main function"""
    print("🚀 Memory-Efficient PAN Dataset Processor")
    print("=" * 50)
    
    # Check if extraction directory exists
    extract_dir = "data/raw/pan_dataset_2011/extracted"
    
    if not os.path.exists(extract_dir):
        print(f"❌ Extraction directory not found: {extract_dir}")
        print("Please run the extraction script first:")
        print("   python process_large_pan_dataset.py")
        return
    
    # Initialize processor
    processor = BatchProcessor()
    
    # Process the dataset
    processed_count = processor.process_large_dataset(extract_dir)
    
    if processed_count > 0:
        print(f"\n🎯 Next steps:")
        print(f"   1. Run: python status.py (check system status)")
        print(f"   2. Run: python test_api.py (test plagiarism detection)")
        print(f"   3. Open: frontend/index.html (use web interface)")
    else:
        print("❌ No files were processed successfully")

if __name__ == "__main__":
    main()

