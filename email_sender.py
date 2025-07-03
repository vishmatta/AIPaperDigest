# send_email(papers: list)

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import requests
import pdfplumber
import warnings

warnings.filterwarnings("ignore")

def format_papers_html(papers):
    """
    Formats a list of papers into an HTML string for email.
    Each paper should have 'title', 'gpt_summary' (or 'summary'), and 'link'.
    """
    html = "<h2>Latest AI Papers from arXiv</h2><ul>"
    for paper in papers:
        title = paper.get("title", "No Title")
        summary = paper.get("gpt_summary") or paper.get("summary", "No Summary")
        link = paper.get("link", "#")
        tags = paper.get("tags", [])
        tags_str = ", ".join(tags) if tags else "No tags"
        # Split summary into lines for bullet points
        bullets = ""
        for line in summary.splitlines():
            line = line.strip()
            if line.startswith("-"):
                line = line[1:].strip()
            if line:
                bullets += f"<li>{line}</li>"
        html += f"""
        <li>
            <strong>{title}</strong><br>
            <em>Tags: {tags_str}</em><br>
            <ul>{bullets}</ul>
            <a href="{link}">Read more</a>
        </li>
        <br>
        """
    html += "</ul>"
    return html

def send_email(papers: list):
    """
    Sends an HTML email with the list of papers using Gmail SMTP.
    Credentials and recipient are loaded from .env file.
    Adds basic error handling and prints a fallback message if email fails to send.
    """
    try:
        load_dotenv()
        sender_email = os.getenv("GMAIL_ADDRESS")
        sender_password = os.getenv("GMAIL_APP_PASSWORD")
        recipient_email = os.getenv("RECIPIENT_EMAIL")

        if not sender_email or not sender_password or not recipient_email:
            raise ValueError("GMAIL_ADDRESS, GMAIL_APP_PASSWORD, or RECIPIENT_EMAIL not set in .env")

        subject = "Latest AI Papers from arXiv"
        html_content = format_papers_html(papers)

        # Create the email
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = recipient_email

        part = MIMEText(html_content, "html")
        msg.attach(part)

        # Send the email via Gmail SMTP
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, recipient_email, msg.as_string())
            print("Email sent successfully.")
        except Exception as e:
            print(f"Failed to send email: {e}")
            print("\n--- Fallback: Here is the email content you can send manually ---\n")
            print(f"To: {recipient_email}")
            print(f"Subject: {subject}")
            print("Body (HTML):\n")
            print(html_content)
    except Exception as outer_e:
        print(f"An error occurred in send_email: {outer_e}")
        print("\n--- Fallback: Unable to send email. Please check your configuration. ---")
        if papers:
            print("Here are the papers you wanted to send:\n")
            for paper in papers:
                print(f"Title: {paper.get('title', 'No Title')}")
                print(f"Summary: {paper.get('gpt_summary') or paper.get('summary', 'No Summary')}")
                print(f"Link: {paper.get('link', '#')}")
                print("-" * 40)
        else:
            print("No papers to display.")

def extract_text_from_arxiv_pdf(arxiv_url):
    # Convert abstract URL to PDF URL
    pdf_url = arxiv_url.replace('/abs/', '/pdf/') + '.pdf'
    response = requests.get(pdf_url)
    if response.status_code != 200:
        raise Exception(f"Failed to download PDF: {pdf_url}")
    with open("temp_paper.pdf", "wb") as f:
        f.write(response.content)
    text = ""
    with pdfplumber.open("temp_paper.pdf") as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    os.remove("temp_paper.pdf")
    return text
