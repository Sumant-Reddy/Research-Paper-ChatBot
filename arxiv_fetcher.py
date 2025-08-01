import arxiv
import os

def download_latest_papers(query="LLM", max_results=3, save_dir="data/papers"):
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )

    downloaded = []
    for result in search.results():
        paper_path = os.path.join(save_dir, f"{result.title[:50]}.pdf")
        result.download_pdf(filename=paper_path)
        downloaded.append(paper_path)
    return downloaded
