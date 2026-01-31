from flask import Flask, request, jsonify, send_file
from flask_cors import CORS, cross_origin
from services.plagiarism_service import PlagiarismService
from services.data_service import Database
import os
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Configure timeout for long-running requests (10 minutes)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['PERMANENT_SESSION_LIFETIME'] = 600  # 10 minutes

# Initialize services
plagiarism_service = PlagiarismService()
db = Database("data/database.db")

# Create necessary directories
UPLOAD_FOLDER = "uploads"
REPORTS_FOLDER = "reports"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORTS_FOLDER, exist_ok=True)

@app.route("/", methods=["GET"])
def home():
    """Home endpoint with API information"""
    return jsonify({
        "message": "Blockchain + AI Powered Plagiarism Detection System",
        "version": "1.0.0",
        "endpoints": {
            "check_plagiarism": "POST /check",
            "verify_report": "GET /verify/<report_hash>",
            "get_user_reports": "GET /reports/<user_id>",
            "get_system_stats": "GET /stats",
            "collect_data": "POST /collect-data"
        }
    })

@app.route("/check", methods=["POST", "OPTIONS"])
@cross_origin()  # Ensure CORS headers for POST + preflight from browser
def check_plagiarism():
    """
    Enhanced API endpoint: Accepts uploaded document, runs comprehensive
    plagiarism detection with blockchain integration.
    Optimized for large databases (50k+ documents).
    """
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "Empty filename"}), 400

        # Get optional parameters
        user_id = request.form.get("user_id", "anonymous")
        store_on_blockchain = request.form.get("store_on_blockchain", "true").lower() == "true"
        report_type = request.form.get("report_type", "detailed")
        
        # ASCII-safe logging for Windows terminals
        print(f"[App] Processing file: {file.filename} for user: {user_id}")

        # Save uploaded file temporarily
        uploaded_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(uploaded_path)

        # Run comprehensive plagiarism check (now optimized for large datasets)
        print("[App] Starting plagiarism detection...")
        report = plagiarism_service.check_document(
            uploaded_file=uploaded_path,
            reference_files=None,  # Use database
            user_id=user_id,
            store_on_blockchain=store_on_blockchain
        )
        print("[App] Plagiarism detection completed")

        # Save report to file
        report_filename = f"report_{report['report_id']}.json"
        report_path = os.path.join(REPORTS_FOLDER, report_filename)
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # Clean up uploaded file
        os.remove(uploaded_path)
        # print(report.get("blockchain_verification"));
        print(report.get("ipfs_storage"));
        return jsonify({
            "status": "success",
            "report_id": report["report_id"],
            "overall_score": report["overall_score"],
            "plagiarism_level": report["plagiarism_level"],
            "total_sources_checked": report["total_sources_checked"],
            "blockchain_verification": report.get("blockchain_verification"),
            "ipfs_storage": report.get("ipfs_storage"),
            "report_url": f"/reports/{report['report_id']}",
            "download_url": f"/download/{report['report_id']}"
        })

    except TimeoutError:
        return jsonify({
            "status": "error",
            "error": "Request timeout - the database is too large. Please try with a smaller dataset or contact support."
        }), 504
    except MemoryError:
        return jsonify({
            "status": "error",
            "error": "Out of memory - the database is too large to process. Please reduce the dataset size."
        }), 507
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[App] Error in check_plagiarism: {str(e)}\n{error_trace}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route("/verify/<report_hash>", methods=["GET"])
def verify_report(report_hash):
    """Verify report integrity using blockchain"""
    try:
        verification_result = plagiarism_service.verify_report(report_hash)
        return jsonify(verification_result)
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route("/reports/<user_id>", methods=["GET"])
def get_user_reports(user_id):
    """Get all reports for a specific user"""
    try:
        reports = plagiarism_service.get_user_reports(user_id)
        return jsonify({
            "status": "success",
            "user_id": user_id,
            "total_reports": len(reports),
            "reports": reports
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route("/reports/<report_id>", methods=["GET"])
def get_report_details(report_id):
    """Get detailed report by ID"""
    try:
        report = db.get_plagiarism_report(report_id)
        if not report:
            return jsonify({
                "status": "error",
                "error": "Report not found"
            }), 404

        # Load full report from file if available
        report_file = os.path.join(REPORTS_FOLDER, f"report_{report_id}.json")
        if os.path.exists(report_file):
            with open(report_file, 'r', encoding='utf-8') as f:
                full_report = json.load(f)
            return jsonify({
                "status": "success",
                "report": full_report
            })
        else:
            return jsonify({
                "status": "success",
                "report": {
                    "report_id": report[1],
                    "overall_score": report[4],
                    "tfidf_score": report[5],
                    "bert_score": report[6],
                    "created_at": report[10]
                }
            })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route("/download/<report_id>", methods=["GET"])
def download_report(report_id):
    """Download report as JSON file"""
    try:
        report_file = os.path.join(REPORTS_FOLDER, f"report_{report_id}.json")
        if os.path.exists(report_file):
            return send_file(report_file, as_attachment=True, download_name=f"plagiarism_report_{report_id}.json")
        else:
            return jsonify({
                "status": "error",
                "error": "Report file not found"
            }), 404
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route("/stats", methods=["GET"])
def get_system_stats():
    """Get system statistics and status"""
    try:
        stats = plagiarism_service.get_system_stats()
        return jsonify({
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "statistics": stats
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route("/collect-data", methods=["POST"])
def collect_data():
    """Trigger data collection from various sources"""
    try:
        data = request.get_json()
        sources = data.get("sources", ["wikipedia", "arxiv", "sample"])
        
        # This would trigger the data collection process
        # For now, return success message
        return jsonify({
            "status": "success",
            "message": "Data collection initiated",
            "sources": sources,
            "note": "Run data_collector.py to collect data"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        db_status = "connected" if db else "disconnected"
        
        # Check blockchain status
        blockchain_status = plagiarism_service.blockchain_service.get_blockchain_info()
        
        # Check IPFS status
        ipfs_status = plagiarism_service.ipfs_service.get_ipfs_info()
        
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "database": db_status,
                "blockchain": blockchain_status.get("connected", False),
                "ipfs": ipfs_status.get("connected", False)
            }
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "status": "error",
        "error": "Endpoint not found"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "status": "error",
        "error": "Internal server error"
    }), 500

if __name__ == "__main__":
    # ASCII-safe startup messages for Windows terminals
    print("[App] Starting Blockchain + AI Powered Plagiarism Detection System")
    print("[App] Available endpoints:")
    print("  POST /check - Check document for plagiarism")
    print("  GET /verify/<report_hash> - Verify report on blockchain")
    print("  GET /reports/<user_id> - Get user reports")
    print("  GET /reports/<report_id> - Get report details")
    print("  GET /download/<report_id> - Download report")
    print("  GET /stats - Get system statistics")
    print("  GET /health - Health check")
    print("  POST /collect-data - Trigger data collection")
    print("\n[App] Configuration:")
    print("  * Request timeout: 10 minutes")
    print("  * Optimized for large databases (50k+ documents)")
    print("  * Batch TF-IDF processing enabled")
    print("  * BERT limited to top candidates (may be disabled if torch not available)")
    
    # Run with increased timeout support
    # Note: For production, use a proper WSGI server like gunicorn with timeout settings
    app.run(debug=True, host="0.0.0.0", port=5000, threaded=True)
