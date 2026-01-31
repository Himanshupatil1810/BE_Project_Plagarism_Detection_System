#!/usr/bin/env python
"""
Simple connectivity test for IPFS and Blockchain services.

Run this after configuring your .env file and deploying the smart contract.
"""

from dotenv import load_dotenv

# Load environment variables from .env in the project root
load_dotenv()

from services.ipfs_service import IPFSService
from services.blockchain_service import BlockchainService


def main():
    print("=== Testing IPFS connection ===")
    ipfs = IPFSService()
    ipfs_info = ipfs.get_ipfs_info()
    print(ipfs_info)

    print("\n=== Testing Blockchain connection ===")
    blockchain = BlockchainService()
    bc_info = blockchain.get_blockchain_info()
    print(bc_info)


if __name__ == "__main__":
    main()


