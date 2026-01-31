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
        
        # === START OF "THE BIG CHANGE" ===
        
        # Step 2: Get reference documents (Optimized with FTS5)
        if reference_files is None:
            # Use fresh connection for thread safety
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # --- NEW STAGE 1: CANDIDATE SELECTION ---
            print("[Detect] Stage 1: Running FTS query for candidates...")
            try:
                tokens = [token for token in cleaned_text.split() if token]
                # Preserve order but remove duplicates to keep the query compact
                seen = set()
                deduped_tokens = []
                for token in tokens:
                    if token not in seen:
                        deduped_tokens.append(token)
                        seen.add(token)

                if deduped_tokens:
                    # Use a manageable subset of tokens and OR them together so any match surfaces
                    query_tokens = deduped_tokens[:25]
                    fts_query = " OR ".join(f"{token}*" for token in query_tokens)

                    cursor.execute("""
                        SELECT t.rowid, d.title, d.content 
                        FROM documents_fts AS t
                        JOIN documents AS d ON t.rowid = d.id 
                        WHERE documents_fts MATCH ? 
                        ORDER BY rank 
                        LIMIT 100
                    """, (fts_query,))

                    candidate_docs = cursor.fetchall()
                    reference_files = [(doc[0], doc[1], doc[2]) for doc in candidate_docs]
                    print(f"[Detect] Stage 1: Found {len(reference_files)} potential matches using query tokens: {query_tokens}")
                else:
                    print("[Detect] Stage 1: No usable tokens extracted from document; skipping FTS query.")
                    reference_files = []

                if not reference_files:
                    print("[Detect] Stage 1: FTS returned no candidates, falling back to direct documents sample (LIMIT 100).")
                    cursor.execute("SELECT id, title, content FROM documents LIMIT 100")
                    reference_docs = cursor.fetchall()
                    reference_files = [(doc[0], doc[1], doc[2]) for doc in reference_docs]

            except Exception as e:
                print(f"[Detect] FTS query failed: {e}.")
                print("   Make sure you have run 'rebuild_fts_index.py' first.")
                print("   Falling back to slow method (LIMITED to 100 docs)...")
                
                # Fallback in case FTS fails (e.g., table not populated)
                # We limit to 100 to avoid the 1.5-hour wait
                cursor.execute("SELECT id, title, content FROM documents LIMIT 100")
                reference_docs = cursor.fetchall()
                reference_files = [(doc[0], doc[1], doc[2]) for doc in reference_docs]
            
            conn.close()
            # --- END OF NEW STAGE 1 ---
            
        else:
            # This path remains for testing (e.g., if user provides a small list)
            reference_files = [(i, f"ref_{i}", clean_text(read_file(f))) for i, f in enumerate(reference_files)]
        
        # === END OF "THE BIG CHANGE" ===

        # Step 3: Run plagiarism detection (Now on <100 docs, not 56k)
        # This is STAGE 2: RE-RANKING
        
        # === THIS IS THE ONE-LINE FIX ===
        similarity_results = self._run_detection_methods(uploaded_text, reference_files)
        # === END OF FIX ===
        
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
        """
        Run detection methods (TF-IDF and BERT) on the candidate list.
        This function now only processes a small number of candidates.
        """
        results = []
        
        # NOTE: This function now receives the RAW uploaded_text
        print(f"[Detect] Stage 2: Running TF-IDF and BERT on {len(reference_files)} candidates...")
        
        for doc_id, title, content in reference_files:
            # TF-IDF similarity (very fast)
            try:
                # Compares RAW text vs RAW text
                tfidf_score = self.tfidf_checker.calculate_similarity(uploaded_text, content)
                
                if tfidf_score > 0.1:  # Only store significant matches
                    results.append({
                        "doc_id": doc_id,
                        "title": title,
                        "content": content[:500] + "...", # Truncate content
                        "method": "tfidf",
                        "similarity": tfidf_score
                    })
                print(f"[Detect] TF-IDF score for doc {doc_id}: {tfidf_score}")
            except Exception as e:
                print(f"[Detect] Error during TF-IDF check for doc {doc_id}: {str(e)}")

            # BERT similarity (slower, but only on <100 docs)
            try:
                # Compares RAW text vs RAW text
                bert_score = self.bert_checker.calculate_similarity(uploaded_text, content)
                
                if bert_score > 0.1:  # Only store significant matches
                    results.append({
                        "doc_id": doc_id,
                        "title": title,
                        "content": content[:500] + "...", # Truncate content
                        "method": "bert",
                        "similarity": bert_score
                    })
                print(f"[Detect] BERT score for doc {doc_id}: {bert_score}")
            except Exception as e:
                 print(f"[Detect] Error during BERT check for doc {doc_id}: {str(e)}")
        
        print(f"[Detect] Stage 2 complete: Found {len(results)} total matches.")
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