import sqlite3
import time

print("🚀 Starting FTS5 index rebuild for 'database.db'...")
print("This may take a few minutes for 56,000 documents...")

start_time = time.time()

try:
    # Connect to the database
    conn = sqlite3.connect("data/database.db")
    cursor = conn.cursor()

    # 1. Ensure the 'documents_fts' table exists (from your data_service)
    fts_query = """
    CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
        title, 
        content, 
        source, 
        doc_type,
        content='documents', 
        content_rowid='id'
    );
    """
    cursor.execute(fts_query)

    # 2. Clear all existing data from the FTS table
    print("Clearing old index...")
    cursor.execute("DELETE FROM documents_fts;")

    # 3. Populate the FTS table from the main 'documents' table
    print("Populating FTS table... This is the slow part.")
    # This special command tells FTS5 to rebuild itself from its content table ('documents')
    cursor.execute("INSERT INTO documents_fts(rowid, title, content, source, doc_type) SELECT id, title, content, source, doc_type FROM documents;")

    # 4. Commit the changes
    conn.commit()

    end_time = time.time()
    print(f"\n🎉 FTS5 index rebuilt successfully!")
    print(f"Total time: {end_time - start_time:.2f} seconds")

    # 5. Test query
    print("\nRunning a quick test query...")
    test_query = "machine learning"
    cursor.execute("SELECT rowid, title FROM documents_fts WHERE content MATCH ? LIMIT 5", (test_query,))
    results = cursor.fetchall()

    if results:
        print(f"Test query for '{test_query}' found {len(results)} results:")
        for res in results:
            print(f"  - ID: {res[0]}, Title: {res[1]}")
    else:
        print("Test query returned no results, check your data.")

except Exception as e:
    print(f"\n❌ An error occurred: {e}")
finally:
    if conn:
        conn.close()