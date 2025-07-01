import logging
logging.getLogger("pdfminer").setLevel(logging.ERROR)

# summarize_text(text: str) -> str
import os
from openai import OpenAI
from dotenv import load_dotenv
from email_sender import extract_text_from_arxiv_pdf

def summarize_text(text: str) -> str:
    """
    Summarize the given text using OpenAI's GPT-4 model.

    Args:
        text (str): The text to summarize.

    Returns:
        str: The summary of the text.
    """
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables.")

    client = OpenAI(api_key=api_key)
    prompt = (
        "Summarize the following scientific paper as concise bullet points, "
        "focusing on the main contributions and findings. Use 2-5 bullet points:\n\n"
        f"{text}\n\nBullet point summary:"
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes scientific papers."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=400,
        temperature=0.5,
    )

    summary = response.choices[0].message.content.strip()
    return summary

def summarize_papers(papers):
    """
    Takes a list of paper dicts, adds a 'summary' field to each (using summarize_text on the 'summary' key),
    and returns the new list.

    Args:
        papers (List[dict]): List of papers, each with 'title', 'summary', and 'link'.

    Returns:
        List[dict]: List of papers with an added 'summary' field ('gpt_summary').
    """
    summarized_papers = []
    for paper in papers:
        try:
            full_text = extract_text_from_arxiv_pdf(paper.get("link", ""))
            # Truncate if too long for the model
            max_length = 10000  # or adjust as needed
            full_text = full_text[:max_length]
        except Exception as e:
            print(f"Failed to extract full text for {paper.get('title', 'No Title')}: {e}")
            full_text = paper.get("summary", "")
        gpt_summary = summarize_text(full_text)
        new_paper = paper.copy()
        new_paper["gpt_summary"] = gpt_summary
        summarized_papers.append(new_paper)
    return summarized_papers
