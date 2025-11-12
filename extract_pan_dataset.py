#!/usr/bin/env python3
"""
PAN Dataset 2011 WinRAR Extraction and Processing Script
"""

import os
import subprocess
import sys
from pathlib import Path

def check_winrar():
    """Check if WinRAR is available"""
    try:
        # Try to find WinRAR in common locations
        winrar_paths = [
            r"C:\Program Files\WinRAR\WinRAR.exe",
            r"C:\Program Files (x86)\WinRAR\WinRAR.exe",
            r"C:\Users\{}\AppData\Local\Microsoft\WindowsApps\WinRAR.exe".format(os.getenv('USERNAME', '')),
        ]
        
        for path in winrar_paths:
            if os.path.exists(path):
                return path
        
        # Try to find WinRAR in PATH
        result = subprocess.run(['where', 'winrar'], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip().split('\n')[0]
        
        return None
    except:
        return None

def extract_winrar_archive(archive_path, extract_to):
    """Extract WinRAR archive using WinRAR command line"""
    winrar_path = check_winrar()
    
    if not winrar_path:
        print("❌ WinRAR not found. Please install WinRAR or extract manually.")
        print("   Download from: https://www.winrar.com/")
        return False
    
    try:
        print(f"🔧 Using WinRAR: {winrar_path}")
        print(f"📦 Extracting: {archive_path}")
        print(f"📁 To: {extract_to}")
        
        # WinRAR command: winrar x archive.rar destination\
        cmd = [winrar_path, 'x', archive_path, extract_to + '\\']
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Extraction successful!")
            return True
        else:
            print(f"❌ Extraction failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error during extraction: {str(e)}")
        return False

def find_rar_files(directory):
    """Find RAR files in directory"""
    rar_files = []
    for file in os.listdir(directory):
        if file.lower().endswith(('.rar', '.part1.rar', '.part2.rar')):
            rar_files.append(os.path.join(directory, file))
    return sorted(rar_files)

def main():
    print("🚀 PAN Dataset 2011 - WinRAR Extraction")
    print("=" * 50)
    
    # Set paths
    pan_dir = "data/raw/pan_dataset_2011"
    extract_dir = "data/raw/pan_dataset_2011/extracted"
    
    # Create directories
    os.makedirs(pan_dir, exist_ok=True)
    os.makedirs(extract_dir, exist_ok=True)
    
    print(f"📁 PAN dataset directory: {pan_dir}")
    print(f"📁 Extraction directory: {extract_dir}")
    
    # Check if RAR files exist
    rar_files = find_rar_files(pan_dir)
    
    if not rar_files:
        print(f"\n❌ No RAR files found in {pan_dir}")
        print("\n📋 Please place your PAN dataset files here:")
        print(f"   {pan_dir}/pan_dataset_2011.part1.rar")
        print(f"   {pan_dir}/pan_dataset_2011.part2.rar")
        print("\nOr any other RAR files from the PAN dataset.")
        return
    
    print(f"\n📦 Found {len(rar_files)} RAR file(s):")
    for rar_file in rar_files:
        print(f"   {os.path.basename(rar_file)}")
    
    # Extract the first RAR file (should handle multi-part archives)
    main_rar = rar_files[0]
    print(f"\n🔧 Extracting: {os.path.basename(main_rar)}")
    
    success = extract_winrar_archive(main_rar, extract_dir)
    
    if success:
        print(f"\n✅ Extraction complete!")
        print(f"📁 Extracted files are in: {extract_dir}")
        
        # List extracted files
        extracted_files = os.listdir(extract_dir)
        print(f"\n📋 Extracted {len(extracted_files)} file(s):")
        for file in extracted_files[:10]:  # Show first 10 files
            print(f"   {file}")
        if len(extracted_files) > 10:
            print(f"   ... and {len(extracted_files) - 10} more files")
        
        print(f"\n🎯 Next steps:")
        print(f"   1. Check the extracted files in: {extract_dir}")
        print(f"   2. Run: python integrate_pan_dataset.py")
        print(f"   3. The system will auto-detect the format and process it")
        
    else:
        print(f"\n❌ Extraction failed. Please try manual extraction:")
        print(f"   1. Right-click on the RAR file")
        print(f"   2. Select 'Extract to pan_dataset_2011/extracted/'")
        print(f"   3. Run: python integrate_pan_dataset.py")

if __name__ == "__main__":
    main()

