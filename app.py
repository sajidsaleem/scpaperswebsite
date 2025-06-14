from flask import Flask, render_template, request
import psycopg
import math
import os # Import the 'os' library
from dotenv import load_dotenv # Import load_dotenv

load_dotenv() # Load variables from the .env file

# --- App Configuration ---
PAPERS_PER_PAGE = 10

# --- Database Connection Details ---
# Securely load the database URL from the environment
DATABASE_URL = os.environ.get('DATABASE_URL')

# --- Initialize the Flask App ---
app = Flask(__name__)

# --- Define the main page route ---
@app.route('/', methods=['GET', 'POST'])
def index():
    papers = []
    query = ""
    
    page = request.args.get('page', 1, type=int)

    if request.method == 'POST':
        query = request.form.get('query', '')
        page = 1
    else:
        query = request.args.get('query', '')

    offset = (page - 1) * PAPERS_PER_PAGE
    total_papers = 0
    try:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                
                base_query = "FROM papers"
                count_query = "SELECT COUNT(*) " + base_query
                main_query = "SELECT id, title, author, published_date, summary, pdf_url " + base_query
                
                params = []
                where_clauses = []

                if query:
                    where_clauses.append("(title ILIKE %s OR summary ILIKE %s)")
                    search_term = f"%{query}%"
                    params.extend([search_term, search_term])
                
                if where_clauses:
                    main_query += " WHERE " + " AND ".join(where_clauses)
                    count_query += " WHERE " + " AND ".join(where_clauses)
                
                cur.execute(count_query, params)
                total_papers = cur.fetchone()[0]

                main_query += " ORDER BY published_date DESC LIMIT %s OFFSET %s"
                params.extend([PAPERS_PER_PAGE, offset])
                
                # === START CORRECTED DEBUGGING SECTION ===
                print("--- DEBUG: CHECKING DATABASE QUERY ---")
                print(f"DEBUG SQL Template: {main_query}")
                print(f"DEBUG SQL Params: {params}")

                cur.execute(main_query, params)
                db_papers = cur.fetchall()
                
                print(f"DEBUG: Rows fetched from DB: {len(db_papers)}")
                if db_papers:
                    print(f"DEBUG: First row data: {db_papers[0]}")
                # === END CORRECTED DEBUGGING SECTION ===
                
                for paper in db_papers:
                    papers.append({
                        'id': paper[0],
                        'title': paper[1],
                        'author': paper[2],
                        'published_date': paper[3].strftime('%B %d, %Y'),
                        'summary': paper[4],
                        'pdf_url': paper[5]
                    })
    except psycopg.Error as e:
        print(f"Database error: {e}")

    total_pages = math.ceil(total_papers / PAPERS_PER_PAGE)

    return render_template('index.html', 
                           papers=papers, 
                           query=query,
                           page=page,
                           total_pages=total_pages)
