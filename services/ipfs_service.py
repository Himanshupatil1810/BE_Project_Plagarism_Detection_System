import json
import os
from typing import Dict, Any, Optional
import ipfshttpclient

class IPFSService:
    def __init__(self, ipfs_url: str = None):
        """
        Initialize IPFS service for storing large documents and reports.
        
        Args:
            ipfs_url: IPFS node URL (default: localhost:5001)
        """
        self.ipfs_url = ipfs_url or os.getenv('IPFS_URL', '/ip4/127.0.0.1/tcp/5001')
        self.client = None
        self._connect()

    def _connect(self):
        """Establish connection to IPFS node."""
        try:
            self.client = ipfshttpclient.connect(self.ipfs_url)
            # Keep console output ASCII-safe on Windows terminals
            print("[IPFS] Connected to IPFS node")
        except Exception as e:
            # Keep console output ASCII-safe on Windows terminals
            print(f"[IPFS] Could not connect to IPFS node: {str(e)}")
            print("[IPFS] Reports will be stored locally only")
            self.client = None

    def store_document(self, content: str, filename: str = None) -> Optional[Dict[str, Any]]:
        """
        Store document content in IPFS.
        
        Args:
            content: Document content to store
            filename: Optional filename for the document
            
        Returns:
            IPFS hash and metadata or None if IPFS not available
        """
        if not self.client:
            return None

        try:
            # Create temporary file
            temp_filename = filename or f"document_{hash(content) % 10000}.txt"
            temp_path = f"temp/{temp_filename}"
            
            # Ensure temp directory exists
            os.makedirs("temp", exist_ok=True)
            
            # Write content to temporary file
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Add to IPFS
            result = self.client.add(temp_path)
            ipfs_hash = result['Hash']
            
            # Clean up temporary file
            os.remove(temp_path)
            
            return {
                "ipfs_hash": ipfs_hash,
                "size": result['Size'],
                "filename": temp_filename,
                "status": "success"
            }
            
        except Exception as e:
            print(f"[IPFS] Error storing document in IPFS: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    def store_report(self, report_data: Dict[str, Any], filename: str = None) -> Optional[Dict[str, Any]]:
        """
        Store plagiarism report in IPFS.
        
        Args:
            report_data: Plagiarism report data
            filename: Optional filename for the report
            
        Returns:
            IPFS hash and metadata or None if IPFS not available
        """
        if not self.client:
            return None

        try:
            # Convert report to JSON
            report_json = json.dumps(report_data, indent=2, ensure_ascii=False)
            
            # Create temporary file
            temp_filename = filename or f"report_{hash(str(report_data)) % 10000}.json"
            temp_path = f"temp/{temp_filename}"
            
            # Ensure temp directory exists
            os.makedirs("temp", exist_ok=True)
            
            # Write report to temporary file
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(report_json)
            
            # Add to IPFS
            result = self.client.add(temp_path)
            ipfs_hash = result['Hash']
            print(ipfs_hash)
            # Clean up temporary file
            os.remove(temp_path)
            
            return {
                "ipfs_hash": ipfs_hash,
                "size": result['Size'],
                "filename": temp_filename,
                "status": "success"
            }
            
        except Exception as e:
            print(f"[IPFS] Error storing report in IPFS: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    def retrieve_document(self, ipfs_hash: str) -> Optional[str]:
        """
        Retrieve document content from IPFS.
        
        Args:
            ipfs_hash: IPFS hash of the document
            
        Returns:
            Document content or None if not found
        """
        if not self.client:
            return None

        try:
            # Get content from IPFS
            content = self.client.cat(ipfs_hash)
            return content.decode('utf-8')
            
        except Exception as e:
            print(f"[IPFS] Error retrieving document from IPFS: {str(e)}")
            return None

    def retrieve_report(self, ipfs_hash: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve plagiarism report from IPFS.
        
        Args:
            ipfs_hash: IPFS hash of the report
            
        Returns:
            Report data or None if not found
        """
        if not self.client:
            return None

        try:
            # Get content from IPFS
            content = self.client.cat(ipfs_hash)
            report_data = json.loads(content.decode('utf-8'))
            return report_data
            
        except Exception as e:
            print(f"[IPFS] Error retrieving report from IPFS: {str(e)}")
            return None

    def pin_content(self, ipfs_hash: str) -> bool:
        """
        Pin content in IPFS to prevent garbage collection.
        
        Args:
            ipfs_hash: IPFS hash to pin
            
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            return False

        try:
            self.client.pin.add(ipfs_hash)
            return True
        except Exception as e:
            print(f"[IPFS] Error pinning content in IPFS: {str(e)}")
            return False

    def get_ipfs_info(self) -> Dict[str, Any]:
        """
        Get IPFS node information.
        
        Returns:
            Dictionary with IPFS status and info
        """
        if not self.client:
            return {
                "connected": False,
                "error": "IPFS client not initialized"
            }

        try:
            # Get node info
            node_info = self.client.id()
            return {
                "connected": True,
                "node_id": node_info['ID'],
                "version": node_info['AgentVersion'],
                "addresses": node_info['Addresses']
            }
        except Exception as e:
            return {
                "connected": False,
                "error": str(e)
            }
