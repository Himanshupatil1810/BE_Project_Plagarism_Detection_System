import sqlite3
import os

def create_arxiv_test_file():
    db_path = "data/database.db"
    output_file = "arxiv_high_risk_test.txt"
    
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Query specifically for arXiv content
        # We order by length to ensure we get a substantial piece of text
        query = """
            SELECT title, content 
            FROM documents 
            WHERE source = 'arxiv' 
            ORDER BY LENGTH(content) DESC 
            LIMIT 1
        """
        cursor.execute(query)
        row = cursor.fetchone()
        
        if row:
            title, content = row
            
            # Save the exact content string to a text file
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)
            
            print(f"✅ Success! ArXiv test file created: {output_file}")
            print(f"📄 Based on Paper: {title}")
            print("💡 Upload this to your portal to trigger a 'Flagged' (80%+) status.")
        else:
            print("No arXiv papers found. Please run 'python data_collector.py' first.")
            
        conn.close()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    create_arxiv_test_file()