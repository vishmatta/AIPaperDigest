# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AIPaperDigest is an automated tool that fetches the latest AI papers from arXiv, summarizes them using OpenAI's GPT-4, and sends a daily email digest with bullet-point summaries. The system is designed to run automatically (e.g., via GitHub Actions or cron) to provide regular AI paper updates.

## Architecture

The application follows a simple pipeline architecture with four main modules:

1. **main.py** - Entry point and orchestration layer that coordinates the entire pipeline
2. **rss_parser.py** - Fetches latest papers from arXiv's cs.AI RSS feed (currently limited to 5 papers)
3. **summarizer.py** - Downloads full PDFs, extracts text, and generates summaries + tags using OpenAI GPT-4
4. **email_sender.py** - Formats papers into HTML and sends via Gmail SMTP, with PDF text extraction utilities

### Data Flow
```
arXiv RSS → rss_parser → summarizer (PDF extraction + GPT-4) → email_sender → Gmail
```

Each paper object contains: `title`, `summary` (original abstract), `link`, `gpt_summary`, and `tags`.

## Common Commands

### Setup and Development
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the main application
python main.py
```

### Testing Individual Components
```bash
# Test RSS parsing only
python -c "from rss_parser import test_fetch_latest_papers; test_fetch_latest_papers()"

# Test specific functions interactively
python -c "from rss_parser import fetch_latest_papers; papers = fetch_latest_papers(); print(f'Found {len(papers)} papers')"
```

## Environment Configuration

Required environment variables in `.env` file:
- `OPENAI_API_KEY` - OpenAI API key for GPT-4 summarization
- `GMAIL_ADDRESS` - Gmail address for sending emails
- `GMAIL_APP_PASSWORD` - Gmail app password (not regular password)
- `RECIPIENT_EMAIL` - Email address to receive the digest

## Key Implementation Details

### PDF Processing
- Downloads PDFs temporarily as "temp_paper.pdf" 
- Uses pdfplumber for text extraction
- Truncates content to 10,000 characters for API efficiency
- Suppresses pdfminer warnings in logging configuration

### OpenAI Integration
- Uses GPT-4 model with single API call for both summary and tags
- Temperature set to 0.5 for consistent but creative summaries
- Max tokens: 500 for summaries, 30 for tags
- Implements robust error handling with fallbacks

### Error Handling Strategy
- Each pipeline step has try-catch with graceful degradation
- Email module provides fallback console output if SMTP fails
- PDF extraction falls back to original abstract if download/parsing fails
- Main function continues processing even if individual steps fail

## Deployment Options

The system supports two scheduling approaches:
1. **GitHub Actions** - Cloud-based with secrets management (see README for full workflow)
2. **Local cron** - Server-based scheduling for self-hosted deployments

## Dependencies

Key packages:
- `openai` - GPT-4 API integration
- `feedparser` - RSS parsing for arXiv feeds  
- `pdfplumber` - PDF text extraction
- `python-dotenv` - Environment variable management
- `requests` - HTTP requests for PDF downloads
- Standard library: `smtplib`, `email` for Gmail integration