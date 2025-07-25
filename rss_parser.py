# fetch_latest_papers(): pulls latest AI papers from arXiv's cs.AI feed
import feedparser

def fetch_latest_papers():
    """
    Fetch the latest 5 papers from the arXiv cs.AI RSS feed.

    Returns:
        List[dict]: A list of dictionaries, each containing 'title', 'summary', 'link', and 'tags' keys.
    """
    feed_url = "http://export.arxiv.org/rss/cs.AI"
    feed = feedparser.parse(feed_url)
    papers = []
    for entry in feed.entries[:5]:
        # Extract tags/subjects if present
        tags = []
        if 'tags' in entry:
            tags = [t['term'] for t in entry['tags'] if 'term' in t]
        paper = {
            "title": entry.get("title", "").strip(),
            "summary": entry.get("summary", "").strip(),
            "link": entry.get("link", ""),
            "tags": tags
        }
        papers.append(paper)
    return papers

def test_fetch_latest_papers():
    papers = fetch_latest_papers()
    print("Titles of the first 3 papers:")
    for paper in papers[:3]:
        print(paper["title"])

