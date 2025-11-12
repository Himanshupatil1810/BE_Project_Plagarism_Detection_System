#!/usr/bin/env python3
"""
Simple API test script
"""

import requests
import os

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get("http://localhost:5000/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_plagiarism_check():
    """Test plagiarism check endpoint"""
    print("\nTesting plagiarism check...")
    try:
        # Check if test document exists
        if not os.path.exists("test_document.txt"):
            print("❌ Test document not found")
            return False
        
        # Prepare file upload
        with open("test_document.txt", "rb") as f:
            files = {"file": ("test_document.txt", f, "text/plain")}
            data = {"user_id": "test_user", "store_on_blockchain": "false"}
            
            response = requests.post("http://localhost:5000/check", files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Plagiarism check successful")
            print(f"Report ID: {result.get('report_id')}")
            print(f"Overall Score: {result.get('overall_score')}")
            print(f"Plagiarism Level: {result.get('plagiarism_level')}")
            print(f"Sources Checked: {result.get('total_sources_checked')}")
            return True
        else:
            print(f"❌ Plagiarism check failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Plagiarism check error: {e}")
        return False

def test_stats():
    """Test stats endpoint"""
    print("\nTesting stats endpoint...")
    try:
        response = requests.get("http://localhost:5000/stats")
        if response.status_code == 200:
            result = response.json()
            print("✅ Stats check successful")
            print(f"Total Reports: {result.get('statistics', {}).get('total_reports', 0)}")
            print(f"Total Submissions: {result.get('statistics', {}).get('total_submissions', 0)}")
            return True
        else:
            print(f"❌ Stats check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Stats check error: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Plagiarism Detection API")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health),
        ("Plagiarism Check", test_plagiarism_check),
        ("Stats Check", test_stats)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All API tests passed! System is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()

