#!/usr/bin/env python3
"""
Simple script to integrate PAN Dataset 2011
"""

import os
import sys
from pan_dataset_processor import PANDatasetProcessor

def main():
    print("🚀 PAN Dataset 2011 Integration")
    print("=" * 50)
    
    # Check if PAN dataset exists in common locations
    possible_paths = [
        "data/raw/pan_dataset_2011.csv",
        "data/raw/pan_dataset_2011.xml",
        "data/raw/pan_dataset_2011/",
        "pan_dataset_2011.csv",
        "pan_dataset_2011.xml",
        "pan_dataset_2011/"
    ]
    
    print("🔍 Looking for PAN dataset in common locations...")
    
    found_paths = []
    for path in possible_paths:
        if os.path.exists(path):
            found_paths.append(path)
            print(f"✅ Found: {path}")
    
    if not found_paths:
        print("\n❌ PAN dataset not found in common locations.")
        print("\n📁 Please place your PAN dataset in one of these locations:")
        print("   data/raw/pan_dataset_2011.csv")
        print("   data/raw/pan_dataset_2011.xml")
        print("   data/raw/pan_dataset_2011/")
        print("\nOr provide the path as an argument:")
        print("   python integrate_pan_dataset.py /path/to/your/dataset")
        return
    
    # Use the first found path
    dataset_path = found_paths[0]
    print(f"\n🎯 Using dataset: {dataset_path}")
    
    # Initialize processor
    processor = PANDatasetProcessor()
    
    # Process the dataset
    print("\n📊 Processing PAN dataset...")
    success = processor.auto_detect_and_process(dataset_path)
    
    if success:
        print("\n✅ PAN dataset integration successful!")
        
        # Show statistics
        processor.get_dataset_stats()
        
        print("\n🎉 Integration complete!")
        print("Your PAN dataset is now part of the plagiarism detection system.")
        print("\n🚀 Next steps:")
        print("   1. Run: python status.py (check system status)")
        print("   2. Run: python test_api.py (test plagiarism detection)")
        print("   3. Open: frontend/index.html (use web interface)")
    else:
        print("\n❌ PAN dataset integration failed.")
        print("Please check the dataset format and try again.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # User provided custom path
        custom_path = sys.argv[1]
        if os.path.exists(custom_path):
            processor = PANDatasetProcessor()
            success = processor.auto_detect_and_process(custom_path)
            if success:
                processor.get_dataset_stats()
            else:
                print("❌ Failed to process dataset at:", custom_path)
        else:
            print("❌ Path not found:", custom_path)
    else:
        main()

