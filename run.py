#!/usr/bin/env python3
"""
Simple run script for the Plagiarism Detection System
"""

import os
import sys
import subprocess
import platform

def check_setup():
    """Check if the system is properly set up"""
    print("🔍 Checking system setup...")
    
    # Check if virtual environment exists
    if not os.path.exists("venv"):
        print("❌ Virtual environment not found!")
        print("Please run: python setup.py")
        return False
    
    # Check if database exists
    if not os.path.exists("data/database.db"):
        print("⚠️ Database not found. Initializing...")
        if platform.system() == "Windows":
            python_cmd = "venv\\Scripts\\python"
        else:
            python_cmd = "venv/bin/python"
        
        result = subprocess.run(f"{python_cmd} data_collector.py", shell=True)
        if result.returncode != 0:
            print("❌ Failed to initialize database")
            return False
    
    print("✅ System setup looks good!")
    return True

def start_application():
    """Start the Flask application"""
    print("🚀 Starting Plagiarism Detection System...")
    
    if platform.system() == "Windows":
        python_cmd = "venv\\Scripts\\python"
    else:
        python_cmd = "venv/bin/python"
    
    try:
        subprocess.run(f"{python_cmd} app.py", shell=True)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")

def main():
    """Main function"""
    print("🔍 Blockchain + AI Powered Plagiarism Detection System")
    print("=" * 60)
    
    if not check_setup():
        sys.exit(1)
    
    start_application()

if __name__ == "__main__":
    main()
