# Step 1: Load env vars
# Step 2: Fetch latest papers
# Step 3: Summarize each
# Step 4: Send email
from rss_parser import fetch_latest_papers
from summarizer import summarize_papers
from email_sender import send_email
from email_sender import extract_text_from_arxiv_pdf

def main():
    try:
        # Step 1: Load env vars
        try:
            from dotenv import load_dotenv
            load_dotenv()
            print("[INFO] Environment variables loaded.")
        except Exception as e:
            print(f"[ERROR] Failed to load environment variables: {e}")

        # Step 2: Fetch latest papers
        try:
            papers = fetch_latest_papers()
            print(f"[INFO] Fetched {len(papers)} papers from arXiv.")
        except Exception as e:
            print(f"[ERROR] Failed to fetch latest papers: {e}")
            return

        # Step 3: Summarize each
        try:
            summarized_papers = summarize_papers(papers)
            print(f"[INFO] Summarized {len(summarized_papers)} papers using GPT-4.")
        except Exception as e:
            print(f"[ERROR] Failed to summarize papers: {e}")
            summarized_papers = papers  # Fallback to unsummarized papers

        # Step 4: Send email
        try:
            send_email(summarized_papers)
            print("[INFO] Email sending process completed.")
        except Exception as e:
            print(f"[ERROR] Failed to send email: {e}")

    except Exception as e:
        print(f"[FATAL] An unexpected error occurred in main: {e}")

if __name__ == "__main__":
    main()

