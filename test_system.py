#!/usr/bin/env python3
"""
Simple test script to verify the system is working
"""

import os
import sys
import tempfile
import requests
import time
import subprocess
import platform

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        from services.plagiarism_service import PlagiarismService
        from services.data_service import Database
        from models.tfidf_checker import TFIDFChecker
        from models.bert_checker import BERTChecker
        from preprocessing.file_parser import read_file
        from preprocessing.text_cleaner import clean_text
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_database():
    """Test database operations"""
    print("🗄️ Testing database...")
    
    try:
        from services.data_service import Database
        
        # Create temporary database
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
            db_path = tmp.name
        
        db = Database(db_path)
        
        # Test adding document
        db.add_document("Test Doc", "Test content", "test")
        
        # Test fetching documents
        docs = db.fetch_all_documents()
        assert len(docs) > 0, "No documents found"
        
        db.close()
        os.unlink(db_path)
        
        print("✅ Database operations successful")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_plagiarism_detection():
    """Test plagiarism detection"""
    print("🔍 Testing plagiarism detection...")
    
    try:
        from models.tfidf_checker import TFIDFChecker
        from models.bert_checker import BERTChecker
        
        # Test TF-IDF
        tfidf = TFIDFChecker()
        doc1 = "This is about machine learning and artificial intelligence."
        doc2 = "Machine learning is a subset of artificial intelligence."
        
        similarity = tfidf.calculate_similarity(doc1, doc2)
        assert 0 <= similarity <= 1, f"Invalid similarity score: {similarity}"
        
        # Test BERT (this might take a moment to load the model)
        print("  Loading BERT model (this may take a moment)...")
        bert = BERTChecker()
        similarity = bert.calculate_similarity(doc1, doc2)
        assert 0 <= similarity <= 1, f"Invalid similarity score: {similarity}"
        
        print("✅ Plagiarism detection successful")
        return True
    except Exception as e:
        print(f"❌ Plagiarism detection error: {e}")
        return False

def test_file_processing():
    """Test file processing"""
    print("📄 Testing file processing...")
    
    try:
        from preprocessing.file_parser import read_file
        from preprocessing.text_cleaner import clean_text
        
        # Create temporary text file
        test_content = "This is a test document about artificial intelligence."
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(test_content)
            test_file = f.name
        
        # Test file reading
        content = read_file(test_file)
        assert content == test_content, "File content mismatch"
        
        # Test text cleaning
        cleaned = clean_text(content)
        assert isinstance(cleaned, str), "Cleaned text should be string"
        
        os.unlink(test_file)
        print("✅ File processing successful")
        return True
    except Exception as e:
        print(f"❌ File processing error: {e}")
        return False

def test_api_server():
    """Test if API server can start"""
    print("🌐 Testing API server...")
    
    try:
        # Check if server is already running
        try:
            response = requests.get("http://localhost:5000/health", timeout=5)
            if response.status_code == 200:
                print("✅ API server is already running")
                return True
        except:
            pass
        
        # Try to start server in background
        if platform.system() == "Windows":
            python_cmd = "venv\\Scripts\\python"
        else:
            python_cmd = "venv/bin/python"
        
        # Start server process
        process = subprocess.Popen(
            [python_cmd, "app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a bit for server to start
        time.sleep(5)
        
        # Test health endpoint
        try:
            response = requests.get("http://localhost:5000/health", timeout=5)
            if response.status_code == 200:
                print("✅ API server started successfully")
                process.terminate()
                return True
            else:
                print(f"❌ API server returned status {response.status_code}")
                process.terminate()
                return False
        except Exception as e:
            print(f"❌ API server test failed: {e}")
            process.terminate()
            return False
            
    except Exception as e:
        print(f"❌ API server error: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Blockchain + AI Powered Plagiarism Detection System")
    print("=" * 70)
    
    tests = [
        ("Import Test", test_imports),
        ("Database Test", test_database),
        ("File Processing Test", test_file_processing),
        ("Plagiarism Detection Test", test_plagiarism_detection),
        ("API Server Test", test_api_server)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 70)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        print("\n🚀 To start the system:")
        print("   python run.py")
        print("   OR")
        print("   python app.py")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        print("💡 Try running: python setup.py")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
