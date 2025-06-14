# Import the 'arxiv' and 'csv' libraries
import arxiv
import csv
import datetime

# --- Search Configuration ---
print("Connecting to arXiv and fetching recent papers...")

search = arxiv.Search(
  query = "cat:cond-mat.supr-con",
  max_results = 50,
  sort_by = arxiv.SortCriterion.SubmittedDate
)

# --- Data Extraction ---

## UPDATED ##
# The new best practice is to use a Client object to run the search.
client = arxiv.Client()
papers_data = []

# Instead of 'search.results()', we now use 'client.results(search)'.
for result in client.results(search):
  first_author = result.authors[0].name if result.authors else "N/A"
  title = result.title
  summary = result.summary.replace('\n', ' ')
  paper_id = result.entry_id.split('/')[-1]
  published_date = result.published.strftime('%Y-%m-%d')
  pdf_url = result.pdf_url
  
  papers_data.append({
      'id': paper_id,
      'title': title,
      'author': first_author,
      'published_date': published_date,
      'summary': summary,
      'pdf_url': pdf_url
  })

print(f"Successfully fetched {len(papers_data)} papers.")

# --- File Saving ---
today_str = datetime.date.today().strftime('%Y-%m-%d')
filename = f"arxiv_papers_{today_str}.csv"
headers = ['id', 'title', 'author', 'published_date', 'summary', 'pdf_url']

try:
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(papers_data)
        
    print(f"Data successfully saved to '{filename}'")

except IOError:
    print("Error: Could not write to the file.")
