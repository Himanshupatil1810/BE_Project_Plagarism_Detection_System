import unittest
import os
import tempfile
import json
from services.plagiarism_service import PlagiarismService
from services.data_service import Database
from services.report_service import ReportService
from services.blockchain_service import BlockchainService
from services.ipfs_service import IPFSService

class TestPlagiarismDetection(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        # Create temporary database
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Initialize services
        self.db = Database(self.temp_db.name)
        self.plagiarism_service = PlagiarismService(self.temp_db.name)
        self.report_service = ReportService()
        
        # Create test documents
        self.test_documents = [
            {
                "title": "Test Document 1",
                "content": "This is a test document about artificial intelligence and machine learning.",
                "source": "test"
            },
            {
                "title": "Test Document 2", 
                "content": "Machine learning is a subset of artificial intelligence that focuses on algorithms.",
                "source": "test"
            }
        ]
        
        # Add test documents to database
        for doc in self.test_documents:
            self.db.add_document(doc["title"], doc["content"], doc["source"])

    def tearDown(self):
        """Clean up test environment"""
        self.db.close()
        os.unlink(self.temp_db.name)

    def test_database_operations(self):
        """Test database operations"""
        # Test adding document
        self.db.add_document("Test Doc", "Test content", "test")
        
        # Test fetching documents
        docs = self.db.fetch_all_documents()
        self.assertGreater(len(docs), 0)
        
        # Test adding plagiarism report
        self.db.add_plagiarism_report(
            report_hash="test_hash",
            document_hash="doc_hash",
            document_content="content",
            overall_score=0.5,
            tfidf_score=0.3,
            bert_score=0.7,
            sources="[]",
            metadata="{}"
        )
        
        # Test fetching report
        report = self.db.get_plagiarism_report("test_hash")
        self.assertIsNotNone(report)
        self.assertEqual(report[1], "test_hash")

    def test_tfidf_checker(self):
        """Test TF-IDF plagiarism detection"""
        from models.tfidf_checker import TFIDFChecker
        
        checker = TFIDFChecker()
        
        # Test similar documents
        doc1 = "This is about machine learning and artificial intelligence."
        doc2 = "Machine learning is a subset of artificial intelligence."
        
        similarity = checker.calculate_similarity(doc1, doc2)
        self.assertGreater(similarity, 0.5)
        
        # Test different documents
        doc3 = "This is about cooking and recipes."
        similarity = checker.calculate_similarity(doc1, doc3)
        self.assertLess(similarity, 0.5)

    def test_bert_checker(self):
        """Test BERT plagiarism detection"""
        from models.bert_checker import BERTChecker
        
        checker = BERTChecker()
        
        # Test similar documents
        doc1 = "This is about machine learning and artificial intelligence."
        doc2 = "Machine learning is a subset of artificial intelligence."
        
        similarity = checker.calculate_similarity(doc1, doc2)
        self.assertGreater(similarity, 0.3)
        
        # Test different documents
        doc3 = "This is about cooking and recipes."
        similarity = checker.calculate_similarity(doc1, doc3)
        self.assertLess(similarity, 0.5)

    def test_report_generation(self):
        """Test report generation service"""
        # Create mock similarity results
        similarity_results = [
            {
                "doc_id": 1,
                "title": "Test Source",
                "content": "Machine learning content",
                "method": "tfidf",
                "similarity": 0.8
            },
            {
                "doc_id": 1,
                "title": "Test Source",
                "content": "Machine learning content",
                "method": "bert",
                "similarity": 0.7
            }
        ]
        
        # Generate report
        report = self.report_service.generate_plagiarism_report(
            uploaded_text="This is about machine learning.",
            similarity_results=similarity_results,
            detection_methods=["TF-IDF", "BERT"],
            report_type="detailed"
        )
        
        # Verify report structure
        self.assertIn("report_id", report)
        self.assertIn("overall_score", report)
        self.assertIn("plagiarism_level", report)
        self.assertIn("sources", report)
        self.assertIn("recommendations", report)
        
        # Verify scores
        self.assertGreater(report["overall_score"], 0)
        self.assertLessEqual(report["overall_score"], 1)

    def test_plagiarism_service_integration(self):
        """Test integrated plagiarism detection service"""
        # Create temporary test file
        test_content = "This is a test document about machine learning and artificial intelligence."
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(test_content)
            test_file = f.name
        
        try:
            # Run plagiarism detection
            report = self.plagiarism_service.check_document(
                uploaded_file=test_file,
                user_id="test_user",
                store_on_blockchain=False
            )
            
            # Verify report structure
            self.assertIn("report_id", report)
            self.assertIn("overall_score", report)
            self.assertIn("plagiarism_level", report)
            
            # Verify database storage
            db_report = self.db.get_plagiarism_report(report["report_id"])
            self.assertIsNotNone(db_report)
            
        finally:
            os.unlink(test_file)

    def test_blockchain_service(self):
        """Test blockchain service (without actual blockchain connection)"""
        blockchain_service = BlockchainService()
        
        # Test report hash generation
        test_data = {"test": "data", "score": 0.5}
        report_hash = blockchain_service.generate_report_hash(test_data)
        self.assertIsInstance(report_hash, str)
        self.assertEqual(len(report_hash), 64)  # SHA-256 hash length
        
        # Test document hash generation
        test_content = "Test document content"
        doc_hash = blockchain_service.generate_document_hash(test_content)
        self.assertIsInstance(doc_hash, str)
        self.assertEqual(len(doc_hash), 64)
        
        # Test blockchain info (should work even without connection)
        info = blockchain_service.get_blockchain_info()
        self.assertIn("connected", info)

    def test_ipfs_service(self):
        """Test IPFS service (without actual IPFS connection)"""
        ipfs_service = IPFSService()
        
        # Test IPFS info (should work even without connection)
        info = ipfs_service.get_ipfs_info()
        self.assertIn("connected", info)

    def test_file_parsing(self):
        """Test file parsing functionality"""
        from preprocessing.file_parser import read_file
        
        # Test text file parsing
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Test content for file parsing")
            test_file = f.name
        
        try:
            content = read_file(test_file)
            self.assertEqual(content, "Test content for file parsing")
        finally:
            os.unlink(test_file)

    def test_text_cleaning(self):
        """Test text cleaning functionality"""
        from preprocessing.text_cleaner import clean_text
        
        # Test text cleaning
        dirty_text = "This is a TEST document with special characters! @#$%"
        cleaned = clean_text(dirty_text)
        
        # Should be lowercase and without special characters
        self.assertNotIn("!", cleaned)
        self.assertNotIn("@", cleaned)
        self.assertIn("test", cleaned)

if __name__ == '__main__':
    unittest.main()
