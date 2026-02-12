import json
import hashlib
from datetime import datetime
from web3 import Web3
from typing import Dict, Any, Optional
import os

from web3.middleware import geth_poa_middleware

class BlockchainService:
    def __init__(self, rpc_url: str = None, private_key: str = None, contract_address: str = None):
        """
        Initialize blockchain service for storing plagiarism reports.
        
        Args:
            rpc_url: Ethereum/Polygon RPC URL
            private_key: Private key for signing transactions
            contract_address: Deployed smart contract address
        """
        self.rpc_url = rpc_url or os.getenv('RPC_URL', 'https://polygon-rpc.com')
        self.private_key = private_key or os.getenv('PRIVATE_KEY')
        self.contract_address = contract_address or os.getenv('CONTRACT_ADDRESS')
        
        # Initialize Web3
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        # REQUIRED for Polygon / Amoy (Proof-of-Authority chain)
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

        # Contract ABI for plagiarism report storage.
        # IMPORTANT: This must exactly match contracts/PlagiarismReport.sol
        self.contract_abi = [
            {
                "inputs": [
                    {"internalType": "string", "name": "reportHash", "type": "string"},
                    {"internalType": "string", "name": "documentHash", "type": "string"},
                    {"internalType": "string", "name": "metadata", "type": "string"},
                ],
                "name": "storeReport",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function",
            },
            {
                "inputs": [
                    {"internalType": "string", "name": "reportHash", "type": "string"}
                ],
                "name": "getReport",
                "outputs": [
                    {"internalType": "string", "name": "documentHash", "type": "string"},
                    {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
                    {"internalType": "string", "name": "metadata", "type": "string"},
                    {"internalType": "bool", "name": "exists", "type": "bool"},
                ],
                "stateMutability": "view",
                "type": "function",
            },
            {
                "inputs": [
                    {"internalType": "string", "name": "reportHash", "type": "string"}
                ],
                "name": "verifyReport",
                "outputs": [
                    {"internalType": "bool", "name": "isValid", "type": "bool"}
                ],
                "stateMutability": "view",
                "type": "function",
            },
        ]
        
        if self.contract_address:
            self.contract = self.w3.eth.contract(
                address=self.contract_address,
                abi=self.contract_abi
            )
        else:
            self.contract = None

    def generate_report_hash(self, report_data: Dict[str, Any]) -> str:
        """
        Generate SHA-256 hash of the plagiarism report for blockchain storage.
        
        Args:
            report_data: Dictionary containing plagiarism report data
            
        Returns:
            SHA-256 hash string
        """
        # Create a deterministic string representation of the report
        report_string = json.dumps(report_data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(report_string.encode()).hexdigest()

    def generate_document_hash(self, document_content: str) -> str:
        """
        Generate SHA-256 hash of the document content.
        
        Args:
            document_content: Raw document text content
            
        Returns:
            SHA-256 hash string
        """
        return hashlib.sha256(document_content.encode('utf-8')).hexdigest()

    def store_report_on_blockchain(self, report_data: Dict[str, Any], document_content: str) -> Optional[Dict[str, Any]]:
        """
        Store plagiarism report on blockchain.
        
        Args:
            report_data: Plagiarism report data
            document_content: Original document content
            
        Returns:
            Transaction details or None if blockchain is not configured
        """
        if not self.contract or not self.private_key:
            print("[Blockchain] Not configured. Report will be stored locally only.")
            return None

        try:
            # Use the same identifier that we store in the database
            # (the human‑readable PLAG_... report_id) as the on‑chain key
            # so that `plagiarism_reports.report_hash` and the blockchain
            # reportHash match.
            report_hash = report_data.get("report_id")
            if not report_hash:
                # Fallback: if for some reason report_id is missing,
                # keep the previous behaviour and derive a deterministic hash
                report_hash = self.generate_report_hash(report_data)

            # Always hash the raw document content for integrity metadata
            document_hash = self.generate_document_hash(document_content)
            
            # Prepare metadata
            metadata = {
                "plagiarism_score": report_data.get("overall_score", 0),
                "detection_methods": report_data.get("detection_methods", []),
                "total_sources": len(report_data.get("sources", [])),
                "timestamp": datetime.now().isoformat()
            }
            
            # Prepare transaction
            account = self.w3.eth.account.from_key(self.private_key)
            nonce = self.w3.eth.get_transaction_count(account.address)
            
            print("REPORT HASH STORING ON BLOCKCHAIN: "+ report_hash)
            transaction = self.contract.functions.storeReport(
                report_hash,
                document_hash,
                json.dumps(metadata),
            ).build_transaction({
                'from': account.address,
                'nonce': nonce,
            })

            print(self.w3.eth.gas_price)
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for transaction receipt
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            success = tx_receipt.status == 1
            print("Transaction hash: "+tx_hash.hex())
            return {
                "transaction_hash": tx_hash.hex(),
                "block_number": tx_receipt.blockNumber,
                "report_hash": report_hash,
                "document_hash": document_hash,
                "status": "success" if success else "failed",
            }
            
        except Exception as e:
            print(f"[Blockchain] Error storing report on blockchain: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    def verify_report(self, report_hash: str) -> Dict[str, Any]:
        """
        Verify if a report exists on blockchain and get its details.
        
        Args:
            report_hash: Hash of the report to verify
            
        Returns:
            Verification result with report details
        """
        if not self.contract:
            return {"error": "Blockchain not configured"}
        # DEBUG PRINT: Check what string is actually being sent to the blockchain
        print(f"[Debug] Querying Blockchain with Hash: {report_hash}")
        try:
            result = self.contract.functions.getReport(report_hash).call()
            document_hash, timestamp, metadata, exists = result
            
            if exists:
                return {
                    "exists": True,
                    "document_hash": document_hash,
                    "timestamp": timestamp,
                    "metadata": json.loads(metadata) if metadata else {},
                    "verified": True
                }
            else:
                return {
                    "exists": False,
                    "verified": False
                }
                
        except Exception as e:
            return {
                "error": str(e),
                "verified": False
            }

    def get_blockchain_info(self) -> Dict[str, Any]:
        """
        Get current blockchain connection information.
        
        Returns:
            Dictionary with blockchain status and info
        """
        try:
            latest_block = self.w3.eth.get_block('latest')
            return {
                "connected": self.w3.is_connected(),
                "latest_block": latest_block.number,
                "network_id": self.w3.eth.chain_id,
                "contract_deployed": self.contract_address is not None
            }
        except Exception as e:
            return {
                "connected": False,
                "error": str(e)
            }
