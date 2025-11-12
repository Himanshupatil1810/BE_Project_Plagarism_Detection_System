import os
import hashlib
from preprocessing.file_parser import read_file
from preprocessing.text_cleaner import clean_text
from models.tfidf_checker import TFIDFChecker
from models.bert_checker import BERTChecker
from services.report_service import ReportService
from services.blockchain_service import BlockchainService
from services.ipfs_service import IPFSService
from services.data_service import Database

class PlagiarismService:
    def __init__(self, db_path="data/database.db"):
        self.tfidf_checker = TFIDFChecker()
        self.bert_checker = BERTChecker()
        self.report_service = ReportService()
        self.blockchain_service = BlockchainService()
        self.ipfs_service = IPFSService()
        self.db = Database(db_path)

    def check_document(self, uploaded_file, reference_files=None, user_id=None, store_on_blockchain=True):
        """
        Comprehensive plagiarism detection with blockchain integration.
        
        Args:
            uploaded_file: Path to uploaded document
            reference_files: List of reference files (if None, uses database)
            user_id: User ID for tracking
            store_on_blockchain: Whether to store report on blockchain
            
        Returns:
            Comprehensive plagiarism report with blockchain verification
        """
        # Step 1: Parse and clean uploaded document
        uploaded_text = read_file(uploaded_file)
        cleaned_text = clean_text(uploaded_text)
        
        # Generate document hash
        document_hash = hashlib.sha256(uploaded_text.encode('utf-8')).hexdigest()
        
        # Step 2: Get reference documents
        if reference_files is None:
            # Use fresh connection for thread safety
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, content FROM documents")
            reference_docs = cursor.fetchall()
            conn.close()
            reference_files = [(doc[0], doc[1], doc[2]) for doc in reference_docs]  # (id, title, content)
        else:
            reference_files = [(i, f"ref_{i}", clean_text(read_file(f))) for i, f in enumerate(reference_files)]

        # Step 3: Run plagiarism detection
        similarity_results = self._run_detection_methods(cleaned_text, reference_files)
        
        # Step 4: Generate comprehensive report
        report = self.report_service.generate_plagiarism_report(
            uploaded_text=uploaded_text,
            similarity_results=similarity_results,
            detection_methods=["TF-IDF", "BERT"],
            report_type="detailed"
        )
        
        # Step 5: Store in database
        self._store_report_in_database(report, document_hash, similarity_results)
        
        # Step 6: Store on blockchain if enabled
        if store_on_blockchain:
            blockchain_result = self.blockchain_service.store_report_on_blockchain(report, uploaded_text)
            if blockchain_result and blockchain_result.get("status") == "success":
                report["blockchain_verification"] = blockchain_result
                # Update database with blockchain info
                self._update_report_with_blockchain_info(report["report_id"], blockchain_result)
        
        # Step 7: Store in IPFS
        ipfs_result = self.ipfs_service.store_report(report)
        if ipfs_result and ipfs_result.get("status") == "success":
            report["ipfs_storage"] = ipfs_result
            # Update database with IPFS info
            self._update_report_with_ipfs_info(report["report_id"], ipfs_result)
        
        # Step 8: Track user submission
        if user_id:
            self._track_user_submission(uploaded_file, document_hash, user_id, report["report_id"])
        
        return report

    def _run_detection_methods(self, uploaded_text, reference_files):
        """Run all detection methods on the uploaded text"""
        results = []
        
        for doc_id, title, content in reference_files:
            # TF-IDF similarity
            tfidf_score = self.tfidf_checker.calculate_similarity(uploaded_text, content)
            
            # BERT similarity
            bert_score = self.bert_checker.calculate_similarity(uploaded_text, content)
            
            # Only include results with significant similarity
            if tfidf_score > 0.1 or bert_score > 0.1:
                results.append({
                    "doc_id": doc_id,
                    "title": title,
                    "content": content,
                    "method": "tfidf",
                    "similarity": tfidf_score
                })
                
                results.append({
                    "doc_id": doc_id,
                    "title": title,
                    "content": content,
                    "method": "bert",
                    "similarity": bert_score
                })
        
        return results

    def _store_report_in_database(self, report, document_hash, similarity_results):
        """Store plagiarism report in database"""
        # Calculate average scores
        tfidf_scores = [r["similarity"] for r in similarity_results if r["method"] == "tfidf"]
        bert_scores = [r["similarity"] for r in similarity_results if r["method"] == "bert"]
        
        avg_tfidf = sum(tfidf_scores) / len(tfidf_scores) if tfidf_scores else 0
        avg_bert = sum(bert_scores) / len(bert_scores) if bert_scores else 0
        
        # Prepare data for database
        sources_json = str(report.get("sources", []))
        metadata_json = str({
            "plagiarized_sections": report.get("plagiarized_sections", []),
            "document_stats": report.get("document_stats", {}),
            "recommendations": report.get("recommendations", [])
        })
        
        self.db.add_plagiarism_report(
            report_hash=report["report_id"],
            document_hash=document_hash,
            document_content="",  # Don't store full content in DB
            overall_score=report["overall_score"],
            tfidf_score=avg_tfidf,
            bert_score=avg_bert,
            sources=sources_json,
            metadata=metadata_json
        )

    def _update_report_with_blockchain_info(self, report_id, blockchain_result):
        """Update report with blockchain transaction info"""
        # This would update the database with blockchain transaction hash
        # Implementation depends on your database schema
        pass

    def _update_report_with_ipfs_info(self, report_id, ipfs_result):
        """Update report with IPFS storage info"""
        # This would update the database with IPFS hash
        # Implementation depends on your database schema
        pass

    def _track_user_submission(self, file_path, document_hash, user_id, report_id):
        """Track user submission in database"""
        filename = os.path.basename(file_path)
        self.db.add_user_submission(
            filename=filename,
            file_path=file_path,
            file_hash=document_hash,
            user_id=user_id,
            report_id=report_id,
            status="completed"
        )

    def verify_report(self, report_hash):
        """Verify report integrity using blockchain"""
        # Get report from database
        report = self.db.get_plagiarism_report(report_hash)
        if not report:
            return {"error": "Report not found"}
        
        # Verify on blockchain
        blockchain_verification = self.blockchain_service.verify_report(report_hash)
        
        return {
            "report_found": True,
            "blockchain_verification": blockchain_verification,
            "report_data": report
        }

    def get_user_reports(self, user_id):
        """Get all reports for a specific user"""
        # Use fresh connection for thread safety
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Get user submissions
        cursor.execute("SELECT * FROM user_submissions WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
        submissions = cursor.fetchall()
        
        reports = []
        for submission in submissions:
            if submission[5]:  # report_id exists
                cursor.execute("SELECT * FROM plagiarism_reports WHERE id = ?", (submission[5],))
                report = cursor.fetchone()
                if report:
                    reports.append({
                        "submission": submission,
                        "report": report
                    })
        
        conn.close()
        return reports

    def get_system_stats(self):
        """Get system statistics"""
        # Use fresh connection for thread safety
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Get reports count
        cursor.execute("SELECT COUNT(*) FROM plagiarism_reports")
        total_reports = cursor.fetchone()[0]
        
        # Get submissions count
        cursor.execute("SELECT COUNT(*) FROM user_submissions")
        total_submissions = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_reports": total_reports,
            "total_submissions": total_submissions,
            "blockchain_status": self.blockchain_service.get_blockchain_info(),
            "ipfs_status": self.ipfs_service.get_ipfs_info()
        }
