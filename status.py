#!/usr/bin/env python3
"""
Project Status Dashboard
Shows current status of all system components
"""

import os
import sys
import sqlite3
import requests
from datetime import datetime

def check_database():
    """Check database status"""
    try:
        if os.path.exists("data/database.db"):
            conn = sqlite3.connect("data/database.db")
            cursor = conn.cursor()
            
            # Count documents
            cursor.execute("SELECT COUNT(*) FROM documents")
            doc_count = cursor.fetchone()[0]
            
            # Count reports
            cursor.execute("SELECT COUNT(*) FROM plagiarism_reports")
            report_count = cursor.fetchone()[0]
            
            # Count submissions
            cursor.execute("SELECT COUNT(*) FROM user_submissions")
            submission_count = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "status": "✅ Active",
                "documents": doc_count,
                "reports": report_count,
                "submissions": submission_count
            }
        else:
            return {"status": "❌ Not Found", "documents": 0, "reports": 0, "submissions": 0}
    except Exception as e:
        return {"status": f"❌ Error: {str(e)}", "documents": 0, "reports": 0, "submissions": 0}

def check_api_server():
    """Check API server status"""
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                "status": "✅ Running",
                "url": "http://localhost:5000",
                "services": data.get("services", {}),
                "timestamp": data.get("timestamp", "Unknown")
            }
        else:
            return {"status": f"❌ Error: {response.status_code}", "url": "http://localhost:5000"}
    except Exception as e:
        return {"status": "❌ Not Running", "url": "http://localhost:5000", "error": str(e)}

def check_virtual_environment():
    """Check virtual environment status"""
    if os.path.exists("venv"):
        return {"status": "✅ Created", "path": "venv/"}
    else:
        return {"status": "❌ Not Found", "path": "venv/"}

def check_dependencies():
    """Check if key dependencies are installed"""
    try:
        import flask
        import sklearn
        import nltk
        import transformers
        import sentence_transformers
        import pdfplumber
        import docx
        return {"status": "✅ Installed", "count": 7}
    except ImportError as e:
        return {"status": f"❌ Missing: {str(e)}", "count": 0}

def check_files():
    """Check if key files exist"""
    key_files = [
        "app.py",
        "requirements.txt",
        "frontend/index.html",
        "models/bert_checker.py",
        "models/tfidf_checker.py",
        "services/plagiarism_service.py",
        "services/data_service.py",
        "contracts/PlagiarismReport.sol"
    ]
    
    existing = []
    missing = []
    
    for file in key_files:
        if os.path.exists(file):
            existing.append(file)
        else:
            missing.append(file)
    
    return {
        "status": f"✅ {len(existing)}/{len(key_files)} files found",
        "existing": existing,
        "missing": missing
    }

def main():
    """Main status check function"""
    print("🔍 Blockchain + AI Powered Plagiarism Detection System")
    print("=" * 70)
    print(f"📅 Status Check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check components
    components = [
        ("Virtual Environment", check_virtual_environment()),
        ("Dependencies", check_dependencies()),
        ("Key Files", check_files()),
        ("Database", check_database()),
        ("API Server", check_api_server())
    ]
    
    # Display status
    for name, status in components:
        print(f"📋 {name}:")
        if isinstance(status, dict):
            for key, value in status.items():
                if key != "status":
                    print(f"   {key}: {value}")
            print(f"   Status: {status.get('status', 'Unknown')}")
        else:
            print(f"   Status: {status}")
        print()
    
    # Overall status
    all_good = all(
        "✅" in str(status.get("status", "")) or "✅" in str(status)
        for _, status in components
    )
    
    print("=" * 70)
    if all_good:
        print("🎉 SYSTEM STATUS: FULLY OPERATIONAL")
        print("✅ All components are working correctly")
        print("\n🚀 Ready to use:")
        print("   • Web Interface: frontend/index.html")
        print("   • API Server: http://localhost:5000")
        print("   • Test Document: test_document.txt")
    else:
        print("⚠️ SYSTEM STATUS: ISSUES DETECTED")
        print("❌ Some components need attention")
        print("\n💡 Try running: python setup.py")
    
    print("\n📊 Quick Commands:")
    print("   • Start: python run.py")
    print("   • Test: python test_system.py")
    print("   • API Test: python test_api.py")

if __name__ == "__main__":
    main()

