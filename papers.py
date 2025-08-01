import arxiv
import os
import time

# Create a directory to save the PDFs
download_dir = "./papers"
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

# Define a search query for papers with "machine learning" in the title
# We'll set a max_results to avoid downloading too many papers at once.
search = arxiv.Search(
    # Use the 'OR' operator to search for any of the keywords in the title.
    query='stealth materials',
    max_results=100,  # Limit to 5 papers for this example
    sort_by=arxiv.SortCriterion.SubmittedDate
)

# Get the client
client = arxiv.Client()

# Iterate through the search results and download each PDF
for paper in client.results(search):
    try:
        print(f"Downloading PDF for '{paper.title}'...")
        paper.download_pdf(dirpath=download_dir)
        print("Download successful.")
        
        # IMPORTANT: Respect the rate limit
        # The arxiv.py library's default client has a delay, but it's
        # good practice to add your own just in case.
        time.sleep(3) # Wait for 3 seconds before the next request
    except Exception as e:
        print(f"Could not download '{paper.title}': {e}")