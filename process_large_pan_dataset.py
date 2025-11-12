#!/usr/bin/env python3
"""
Large PAN Dataset 2011 Processor
Optimized for handling 1.7GB+ datasets with memory efficiency
"""

import os
import subprocess
import sys
import time
from pathlib import Path
from pan_dataset_processor import PANDatasetProcessor

class LargePANDatasetProcessor:
    def __init__(self, db_path="data/database.db"):
        self.db = Database(db_path)
        self.processor = PANDatasetProcessor(db_path)
        self.extract_dir = "data/raw/pan_dataset_2011/extracted"
        self.batch_size = 100  # Process in batches to manage memory
        
    def check_winrar(self):
        """Check if WinRAR is available"""
        try:
            winrar_paths = [
                r"C:\Program Files\WinRAR\WinRAR.exe",
                r"C:\Program Files (x86)\WinRAR\WinRAR.exe",
            ]
            
            for path in winrar_paths:
                if os.path.exists(path):
                    return path
            
            result = subprocess.run(['where', 'winrar'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
            
            return None
        except:
            return None
    
    def extract_large_archive(self, archive_path, extract_to):
        """Extract large WinRAR archive with progress monitoring"""
        winrar_path = self.check_winrar()
        
        if not winrar_path:
            print("❌ WinRAR not found. Please install WinRAR or extract manually.")
            print("   Download from: https://www.winrar.com/")
            return False
        
        try:
            print(f"🔧 Using WinRAR: {winrar_path}")
            print(f"📦 Extracting large archive: {os.path.basename(archive_path)}")
            print(f"📁 To: {extract_to}")
            print("⏳ This may take several minutes for 1.7GB dataset...")
            
            # Create extraction directory
            os.makedirs(extract_to, exist_ok=True)
            
            # WinRAR command with progress
            cmd = [winrar_path, 'x', '-y', archive_path, extract_to + '\\']
            
            print("🚀 Starting extraction...")
            start_time = time.time()
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            end_time = time.time()
            duration = end_time - start_time
            
            if result.returncode == 0:
                print(f"✅ Extraction successful! (took {duration:.1f} seconds)")
                return True
            else:
                print(f"❌ Extraction failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error during extraction: {str(e)}")
            return False
    
    def analyze_extracted_content(self, extract_dir):
        """Analyze the extracted content to understand the structure"""
        print(f"\n🔍 Analyzing extracted content in: {extract_dir}")
        
        if not os.path.exists(extract_dir):
            print("❌ Extraction directory not found")
            return None
        
        # Count files and analyze structure
        file_count = 0
        total_size = 0
        file_types = {}
        
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                file_path = os.path.join(root, file)
                file_count += 1
                total_size += os.path.getsize(file_path)
                
                ext = os.path.splitext(file)[1].lower()
                file_types[ext] = file_types.get(ext, 0) + 1
        
        print(f"📊 Analysis Results:")
        print(f"   Total files: {file_count:,}")
        print(f"   Total size: {total_size / (1024*1024*1024):.2f} GB")
        print(f"   File types: {dict(file_types)}")
        
        return {
            'file_count': file_count,
            'total_size': total_size,
            'file_types': file_types
        }
    
    def process_large_dataset_batch(self, extract_dir):
        """Process large dataset in batches to manage memory"""
        print(f"\n📊 Processing large dataset in batches...")
        
        # Find all text files
        text_files = []
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                if file.lower().endswith(('.txt', '.xml', '.csv')):
                    text_files.append(os.path.join(root, file))
        
        print(f"📁 Found {len(text_files)} text files to process")
        
        # Process in batches
        batch_count = 0
        total_processed = 0
        
        for i in range(0, len(text_files), self.batch_size):
            batch_count += 1
            batch_files = text_files[i:i + self.batch_size]
            
            print(f"\n🔄 Processing batch {batch_count} ({len(batch_files)} files)...")
            
            batch_processed = 0
            for file_path in batch_files:
                try:
                    # Process individual file
                    if file_path.endswith('.csv'):
                        success = self.processor.process_pan_dataset_csv(file_path)
                    elif file_path.endswith('.xml'):
                        success = self.processor.process_pan_dataset_xml(file_path)
                    else:
                        # Process as TXT
                        success = self.processor.process_pan_dataset_txt(os.path.dirname(file_path))
                    
                    if success:
                        batch_processed += 1
                        total_processed += 1
                        
                except Exception as e:
                    print(f"   ⚠️ Error processing {os.path.basename(file_path)}: {str(e)}")
                    continue
            
            print(f"   ✅ Batch {batch_count} complete: {batch_processed} files processed")
            
            # Memory management
            if batch_count % 10 == 0:
                print(f"   💾 Memory check: {total_processed} files processed so far")
        
        print(f"\n🎉 Large dataset processing complete!")
        print(f"   Total files processed: {total_processed}")
        return total_processed
    
    def get_processing_recommendations(self, analysis):
        """Get recommendations based on dataset analysis"""
        print(f"\n💡 Processing Recommendations:")
        
        if analysis['file_count'] > 10000:
            print(f"   ⚠️ Large dataset detected ({analysis['file_count']:,} files)")
            print(f"   💾 Consider processing in smaller batches")
            print(f"   ⏳ Estimated processing time: {analysis['file_count'] // 100} minutes")
        
        if analysis['total_size'] > 1024 * 1024 * 1024:  # > 1GB
            print(f"   📊 Large size detected ({analysis['total_size'] / (1024*1024*1024):.2f} GB)")
            print(f"   💾 Ensure sufficient disk space for processing")
        
        # Check available disk space
        try:
            import shutil
            free_space = shutil.disk_usage('.').free
            if free_space < analysis['total_size'] * 2:
                print(f"   ⚠️ Low disk space warning")
                print(f"   💾 Consider freeing up space before processing")
        except:
            pass
    
    def main(self):
        """Main processing workflow"""
        print("🚀 Large PAN Dataset 2011 Processor")
        print("=" * 60)
        print("📊 Dataset: PAN Plagiarism Corpus 2011")
        print("💾 Size: ~1.7GB (1GB + 700MB)")
        print("=" * 60)
        
        # Set paths
        pan_dir = "data/raw/pan_dataset_2011"
        extract_dir = self.extract_dir
        
        # Check if RAR files exist
        rar_files = []
        for file in os.listdir(pan_dir):
            if file.lower().endswith('.rar'):
                rar_files.append(os.path.join(pan_dir, file))
        
        if not rar_files:
            print(f"❌ No RAR files found in {pan_dir}")
            return
        
        print(f"📦 Found {len(rar_files)} RAR file(s):")
        for rar_file in rar_files:
            file_size = os.path.getsize(rar_file) / (1024*1024*1024)
            print(f"   {os.path.basename(rar_file)} ({file_size:.2f} GB)")
        
        # Extract the first RAR file (handles multi-part archives)
        main_rar = rar_files[0]
        print(f"\n🔧 Extracting: {os.path.basename(main_rar)}")
        
        success = self.extract_large_archive(main_rar, extract_dir)
        
        if not success:
            print("❌ Extraction failed. Please try manual extraction.")
            return
        
        # Analyze extracted content
        analysis = self.analyze_extracted_content(extract_dir)
        if not analysis:
            return
        
        # Get recommendations
        self.get_processing_recommendations(analysis)
        
        # Ask user if they want to proceed with processing
        print(f"\n❓ Do you want to process the dataset into the database?")
        print(f"   This will add {analysis['file_count']:,} files to the reference corpus.")
        print(f"   Estimated time: {analysis['file_count'] // 100} minutes")
        
        response = input("   Continue? (y/n): ").lower().strip()
        
        if response == 'y' or response == 'yes':
            # Process the dataset
            processed_count = self.process_large_dataset_batch(extract_dir)
            
            if processed_count > 0:
                print(f"\n🎉 Success! Processed {processed_count} files")
                
                # Show final statistics
                self.processor.get_dataset_stats()
                
                print(f"\n🚀 Next steps:")
                print(f"   1. Run: python status.py (check system status)")
                print(f"   2. Run: python test_api.py (test plagiarism detection)")
                print(f"   3. Open: frontend/index.html (use web interface)")
            else:
                print("❌ No files were processed successfully")
        else:
            print("⏸️ Processing cancelled. You can run this script again later.")

if __name__ == "__main__":
    from services.data_service import Database
    processor = LargePANDatasetProcessor()
    processor.main()

