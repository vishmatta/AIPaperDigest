import logging
logging.getLogger("pdfminer").setLevel(logging.ERROR)

# summarize_text(text: str) -> str
import os
from typing import List, Tuple
from openai import OpenAI
from dotenv import load_dotenv
from email_sender import extract_text_from_arxiv_pdf

def _get_openai_client() -> OpenAI:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables.")
    return OpenAI(api_key=api_key)

def summarize_and_tag_text(text: str) -> Tuple[str, List[str]]:
    """
    Use a single OpenAI API call to generate a simple summary and relevant tags for the given text.
    Returns (summary, tags)
    """
    client = _get_openai_client()
    max_length = 10000
    text = text[:max_length]
    prompt = (
        "Analyze the following scientific paper and provide:\n"
        "1. A summary in 2-5 simple bullet points (avoid jargon, explain as if to a high school student)\n"
        "2. 2-5 relevant tags or keywords\n\n"
        "Format your response as:\n"
        "SUMMARY:\n[bullet points]\n\nTAGS:\n[comma-separated tags]\n\n"
        f"{text}"
    )
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes scientific papers and generates relevant tags."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.5,
    )
    content = response.choices[0].message.content.strip()
    # Parse the response
    summary = ""
    tags = []
    if "SUMMARY:" in content and "TAGS:" in content:
        parts = content.split("TAGS:")
        summary_part = parts[0].replace("SUMMARY:", "").strip()
        tags_part = parts[1].strip()
        summary = summary_part
        tags = [tag.strip() for tag in tags_part.split(",") if tag.strip()]
    else:
        # Fallback: try to split by double newlines
        sections = content.split("\n\n")
        if len(sections) >= 2:
            summary = sections[0].replace("SUMMARY:", "").strip()
            tags = [tag.strip() for tag in sections[1].replace("TAGS:", "").split(",") if tag.strip()]
        else:
            summary = content
            tags = []
    return summary, tags

def summarize_papers(papers):
    """
    For each paper, extract the full text, generate a summary and tags in a single API call,
    and add them to the paper dict. Also, add a 'summary_source' field indicating PDF or abstract.
    """
    summarized_papers = []
    for paper in papers:
        used_pdf = True
        try:
            full_text = extract_text_from_arxiv_pdf(paper.get("link", ""))
            max_length = 10000
            full_text = full_text[:max_length]
        except Exception as e:
            print(f"[ERROR] Failed to extract full text for {paper.get('title', 'No Title')}: {e}")
            full_text = paper.get("summary", "")
            used_pdf = False
        gpt_summary, tags = summarize_and_tag_text(full_text)
        new_paper = paper.copy()
        new_paper["gpt_summary"] = gpt_summary
        new_paper["tags"] = tags
        new_paper["summary_source"] = "PDF" if used_pdf else "Abstract"
        summarized_papers.append(new_paper)
    return summarized_papers

def generate_tags(text: str) -> list:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables.")

    client = OpenAI(api_key=api_key)
    prompt = (
        "Read the following scientific paper and suggest 2-5 relevant, simple tags or keywords "
        "that describe its main topics. Return only a comma-separated list of tags.\n\n"
        f"{text}\n\nTags:"
    )
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates tags for scientific papers."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=30,
        temperature=0.3,
    )
    tags = response.choices[0].message.content.strip()
    return [tag.strip() for tag in tags.split(",") if tag.strip()]
