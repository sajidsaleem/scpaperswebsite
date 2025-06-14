import psycopg
import csv

# --- Database Connection Details ---
# IMPORTANT: Replace 'your_username' with your actual macOS username.
db_params = {
    'dbname': 'superconductivity_db',
    'user': 'sajidsaleem',  # <--- CHANGE THIS
    'password': '',           # Leave empty if you did not set a password
    'host': 'localhost',      # Or '127.0.0.1'
    'port': '5432'
}

# --- The CSV file to load ---
csv_filename = 'arxiv_papers_2025-06-15.csv'

# --- The Main Logic ---
inserted_count = 0
try:
    print("Connecting to the PostgreSQL database...")
    with psycopg.connect(**db_params) as conn:
        with conn.cursor() as cur:
            print(f"Reading data from '{csv_filename}'...")
            with open(csv_filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    # Execute the INSERT statement using placeholders
                    cur.execute(
                        """
                        INSERT INTO papers (id, title, author, published_date, summary, pdf_url)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO NOTHING;
                        """,
                        (
                            row['id'],
                            row['title'],
                            row['author'], # Pass the author string directly
                            row['published_date'],
                            row['summary'],
                            row['pdf_url']
                        )
                    )
                    inserted_count += cur.rowcount

            conn.commit()
            print("\nTransaction committed.")

    print(f"Successfully inserted {inserted_count} new papers into the database.")

except psycopg.Error as e:
    print(f"\nDatabase error: {e}")
except IOError as e:
    print(f"\nFile error: {e}")
    print(f"Please make sure the file '{csv_filename}' is in the same directory.")
