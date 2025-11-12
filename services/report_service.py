import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Tuple
import os

class ReportService:
    def __init__(self):
        """Initialize report generation service"""
        self.report_templates = {
            "detailed": self._generate_detailed_report,
            "summary": self._generate_summary_report,
            "blockchain": self._generate_blockchain_report
        }

    def generate_plagiarism_report(self, 
                                 uploaded_text: str,
                                 similarity_results: List[Dict],
                                 detection_methods: List[str],
                                 report_type: str = "detailed") -> Dict[str, Any]:
        """
        Generate comprehensive plagiarism report.
        
        Args:
            uploaded_text: Original uploaded document text
            similarity_results: List of similarity results from different methods
            detection_methods: List of detection methods used
            report_type: Type of report to generate (detailed, summary, blockchain)
            
        Returns:
            Comprehensive plagiarism report
        """
        # Calculate overall plagiarism score
        overall_score = self._calculate_overall_score(similarity_results)
        
        # Identify plagiarized sections
        plagiarized_sections = self._identify_plagiarized_sections(uploaded_text, similarity_results)
        
        # Generate sources analysis
        sources_analysis = self._analyze_sources(similarity_results)
        
        # Create base report structure
        report = {
            "report_id": self._generate_report_id(),
            "timestamp": datetime.now().isoformat(),
            "overall_score": overall_score,
            "plagiarism_level": self._classify_plagiarism_level(overall_score),
            "detection_methods": detection_methods,
            "total_sources_checked": len(similarity_results),
            "sources": sources_analysis,
            "plagiarized_sections": plagiarized_sections,
            "document_stats": self._analyze_document_stats(uploaded_text),
            "recommendations": self._generate_recommendations(overall_score, plagiarized_sections)
        }
        
        # Generate specific report type
        if report_type in self.report_templates:
            report = self.report_templates[report_type](report, similarity_results)
        
        return report

    def _calculate_overall_score(self, similarity_results: List[Dict]) -> float:
        """Calculate overall plagiarism score from all methods"""
        if not similarity_results:
            return 0.0
        
        # Weight different methods
        weights = {
            "tfidf": 0.4,
            "bert": 0.6
        }
        
        weighted_scores = []
        for result in similarity_results:
            method = result.get("method", "unknown")
            score = result.get("similarity", 0.0)
            weight = weights.get(method, 0.5)
            weighted_scores.append(score * weight)
        
        return sum(weighted_scores) / len(weighted_scores) if weighted_scores else 0.0

    def _identify_plagiarized_sections(self, text: str, similarity_results: List[Dict]) -> List[Dict]:
        """Identify specific sections that are plagiarized"""
        sections = []
        
        # Simple sentence-based analysis
        sentences = text.split('.')
        
        for i, sentence in enumerate(sentences):
            if len(sentence.strip()) < 10:  # Skip very short sentences
                continue
                
            # Check if this sentence appears in any source
            for result in similarity_results:
                if result.get("similarity", 0) > 0.7:  # High similarity threshold
                    source_text = result.get("content", "")
                    if sentence.strip().lower() in source_text.lower():
                        sections.append({
                            "sentence_index": i,
                            "sentence": sentence.strip(),
                            "similarity": result.get("similarity", 0),
                            "source": result.get("title", "Unknown"),
                            "source_id": result.get("doc_id", "unknown")
                        })
        
        return sections

    def _analyze_sources(self, similarity_results: List[Dict]) -> List[Dict]:
        """Analyze and rank sources by similarity"""
        # Sort by similarity score
        sorted_results = sorted(similarity_results, key=lambda x: x.get("similarity", 0), reverse=True)
        
        sources = []
        for result in sorted_results:
            if result.get("similarity", 0) > 0.3:  # Only include significant matches
                sources.append({
                    "title": result.get("title", "Unknown Source"),
                    "similarity": result.get("similarity", 0),
                    "method": result.get("method", "unknown"),
                    "doc_id": result.get("doc_id", "unknown"),
                    "risk_level": self._classify_risk_level(result.get("similarity", 0))
                })
        
        return sources

    def _analyze_document_stats(self, text: str) -> Dict[str, Any]:
        """Analyze document statistics"""
        words = text.split()
        sentences = text.split('.')
        
        return {
            "word_count": len(words),
            "sentence_count": len(sentences),
            "character_count": len(text),
            "average_words_per_sentence": len(words) / len(sentences) if sentences else 0,
            "reading_level": self._estimate_reading_level(text)
        }

    def _generate_recommendations(self, overall_score: float, plagiarized_sections: List[Dict]) -> List[str]:
        """Generate recommendations based on plagiarism analysis"""
        recommendations = []
        
        if overall_score > 0.8:
            recommendations.append("High plagiarism detected. Consider complete rewrite of affected sections.")
        elif overall_score > 0.5:
            recommendations.append("Moderate plagiarism detected. Review and paraphrase affected content.")
        elif overall_score > 0.2:
            recommendations.append("Low plagiarism detected. Ensure proper citations are added.")
        else:
            recommendations.append("No significant plagiarism detected. Document appears original.")
        
        if plagiarized_sections:
            recommendations.append(f"Pay special attention to {len(plagiarized_sections)} identified sections.")
        
        recommendations.append("Always cite sources properly when using external content.")
        recommendations.append("Consider using plagiarism detection tools before submission.")
        
        return recommendations

    def _classify_plagiarism_level(self, score: float) -> str:
        """Classify plagiarism level based on score"""
        if score >= 0.8:
            return "High"
        elif score >= 0.5:
            return "Moderate"
        elif score >= 0.2:
            return "Low"
        else:
            return "Minimal"

    def _classify_risk_level(self, similarity: float) -> str:
        """Classify risk level for individual sources"""
        if similarity >= 0.8:
            return "High Risk"
        elif similarity >= 0.5:
            return "Medium Risk"
        elif similarity >= 0.3:
            return "Low Risk"
        else:
            return "Safe"

    def _estimate_reading_level(self, text: str) -> str:
        """Estimate reading level of the document"""
        # Simple heuristic based on average word length and sentence length
        words = text.split()
        sentences = text.split('.')
        
        if not words or not sentences:
            return "Unknown"
        
        avg_word_length = sum(len(word) for word in words) / len(words)
        avg_sentence_length = len(words) / len(sentences)
        
        if avg_word_length > 6 and avg_sentence_length > 20:
            return "Advanced"
        elif avg_word_length > 4 and avg_sentence_length > 15:
            return "Intermediate"
        else:
            return "Basic"

    def _generate_report_id(self) -> str:
        """Generate unique report ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_part = hashlib.md5(timestamp.encode()).hexdigest()[:8]
        return f"PLAG_{timestamp}_{random_part}"

    def _generate_detailed_report(self, base_report: Dict, similarity_results: List[Dict]) -> Dict[str, Any]:
        """Generate detailed report with comprehensive analysis"""
        detailed_report = base_report.copy()
        
        # Add detailed analysis
        detailed_report["analysis"] = {
            "method_comparison": self._compare_detection_methods(similarity_results),
            "temporal_analysis": self._analyze_temporal_patterns(similarity_results),
            "confidence_scores": self._calculate_confidence_scores(similarity_results)
        }
        
        # Add visualizations data
        detailed_report["visualizations"] = {
            "similarity_distribution": self._generate_similarity_distribution(similarity_results),
            "source_breakdown": self._generate_source_breakdown(similarity_results)
        }
        
        return detailed_report

    def _generate_summary_report(self, base_report: Dict, similarity_results: List[Dict]) -> Dict[str, Any]:
        """Generate concise summary report"""
        summary_report = {
            "report_id": base_report["report_id"],
            "timestamp": base_report["timestamp"],
            "overall_score": base_report["overall_score"],
            "plagiarism_level": base_report["plagiarism_level"],
            "top_sources": base_report["sources"][:3],  # Top 3 sources only
            "key_recommendations": base_report["recommendations"][:2]  # Top 2 recommendations
        }
        
        return summary_report

    def _generate_blockchain_report(self, base_report: Dict, similarity_results: List[Dict]) -> Dict[str, Any]:
        """Generate report optimized for blockchain storage"""
        blockchain_report = {
            "report_id": base_report["report_id"],
            "timestamp": base_report["timestamp"],
            "overall_score": base_report["overall_score"],
            "plagiarism_level": base_report["plagiarism_level"],
            "detection_methods": base_report["detection_methods"],
            "total_sources": base_report["total_sources_checked"],
            "high_risk_sources": [s for s in base_report["sources"] if s["risk_level"] == "High Risk"],
            "document_hash": self._generate_document_hash(base_report),
            "verification_data": {
                "checksum": self._generate_checksum(base_report),
                "version": "1.0",
                "algorithm": "SHA-256"
            }
        }
        
        return blockchain_report

    def _compare_detection_methods(self, similarity_results: List[Dict]) -> Dict[str, Any]:
        """Compare performance of different detection methods"""
        methods = {}
        for result in similarity_results:
            method = result.get("method", "unknown")
            if method not in methods:
                methods[method] = []
            methods[method].append(result.get("similarity", 0))
        
        comparison = {}
        for method, scores in methods.items():
            comparison[method] = {
                "average_score": sum(scores) / len(scores),
                "max_score": max(scores),
                "min_score": min(scores),
                "count": len(scores)
            }
        
        return comparison

    def _analyze_temporal_patterns(self, similarity_results: List[Dict]) -> Dict[str, Any]:
        """Analyze temporal patterns in plagiarism detection"""
        # This would analyze when sources were published vs when document was created
        # For now, return basic structure
        return {
            "analysis_type": "temporal_patterns",
            "note": "Temporal analysis requires source publication dates"
        }

    def _calculate_confidence_scores(self, similarity_results: List[Dict]) -> List[Dict]:
        """Calculate confidence scores for each detection"""
        confidence_scores = []
        for result in similarity_results:
            similarity = result.get("similarity", 0)
            # Simple confidence calculation based on similarity score
            confidence = min(similarity * 1.2, 1.0)  # Cap at 1.0
            confidence_scores.append({
                "source": result.get("title", "Unknown"),
                "similarity": similarity,
                "confidence": confidence
            })
        
        return confidence_scores

    def _generate_similarity_distribution(self, similarity_results: List[Dict]) -> Dict[str, int]:
        """Generate similarity score distribution"""
        distribution = {"0-0.2": 0, "0.2-0.4": 0, "0.4-0.6": 0, "0.6-0.8": 0, "0.8-1.0": 0}
        
        for result in similarity_results:
            score = result.get("similarity", 0)
            if score < 0.2:
                distribution["0-0.2"] += 1
            elif score < 0.4:
                distribution["0.2-0.4"] += 1
            elif score < 0.6:
                distribution["0.4-0.6"] += 1
            elif score < 0.8:
                distribution["0.6-0.8"] += 1
            else:
                distribution["0.8-1.0"] += 1
        
        return distribution

    def _generate_source_breakdown(self, similarity_results: List[Dict]) -> Dict[str, int]:
        """Generate breakdown of sources by type"""
        breakdown = {}
        for result in similarity_results:
            source_type = result.get("source", "unknown")
            breakdown[source_type] = breakdown.get(source_type, 0) + 1
        
        return breakdown

    def _generate_document_hash(self, report: Dict) -> str:
        """Generate hash of the document for verification"""
        # This would hash the original document content
        # For now, return a placeholder
        return hashlib.sha256(str(report["report_id"]).encode()).hexdigest()

    def _generate_checksum(self, report: Dict) -> str:
        """Generate checksum of the report for integrity verification"""
        report_string = json.dumps(report, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(report_string.encode()).hexdigest()

    def save_report_to_file(self, report: Dict[str, Any], filename: str = None) -> str:
        """Save report to JSON file"""
        if not filename:
            filename = f"plagiarism_report_{report['report_id']}.json"
        
        # Ensure reports directory exists
        os.makedirs("reports", exist_ok=True)
        filepath = os.path.join("reports", filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return filepath

    def load_report_from_file(self, filepath: str) -> Dict[str, Any]:
        """Load report from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
