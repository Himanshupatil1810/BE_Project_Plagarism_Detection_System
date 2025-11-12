#!/usr/bin/env python3
"""
Simple database initialization script
"""

import os
import sys
from services.data_service import Database, DataCollector

def init_database_simple():
    """Initialize database with sample data only (no external APIs)"""
    print("Initializing database with sample data...")
    
    try:
        # Initialize database
        db = Database("data/database.db")
        collector = DataCollector(db)
        
        # Add sample academic papers (no external API calls)
        print("Adding sample academic papers...")
        collector.add_sample_academic_papers()
        
        # Get document count
        docs = db.fetch_all_documents()
        print(f"Database initialized with {len(docs)} documents")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"Database initialization failed: {str(e)}")
        return False

def init_database_full():
    """Initialize database with full data collection (includes external APIs)"""
    print("Initializing database with full data collection...")
    
    try:
        # Import and run the full data collector
        from data_collector import collect_comprehensive_dataset
        collect_comprehensive_dataset()
        return True
        
    except Exception as e:
        print(f"Full database initialization failed: {str(e)}")
        return False

def main():
    """Main function"""
    print("Database Initialization")
    print("=" * 40)
    
    # Check if database already exists
    if os.path.exists("data/database.db"):
        print("Database already exists. Skipping initialization.")
        return
    
    # Try simple initialization first
    if init_database_simple():
        print("Simple database initialization completed!")
        print("To add more data (Wikipedia, arXiv), run: python data_collector.py")
    else:
        print("Database initialization failed")

if __name__ == "__main__":
    main()
