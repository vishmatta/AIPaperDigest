# AIPaperDigest

AIPaperDigest is an automated tool that fetches the latest AI papers from arXiv, summarizes them using OpenAI's GPT-4, and sends a daily email digest with bullet-point summaries.

## Features
- Fetches the latest AI papers from arXiv's cs.AI feed
- Downloads and extracts text from the full paper PDFs
- Summarizes papers as bullet points using GPT-4
- Sends a formatted HTML email with the summaries
- Can be scheduled to run automatically (e.g., every morning)

## Setup

### 1. Clone the Repository
```bash
git clone https://github.com/vishmatta/AIPaperDigest.git
cd AIPaperDigest
```

### 2. Create and Activate a Virtual Environment (Recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project root with the following content:
```env
OPENAI_API_KEY=sk-...           # Your OpenAI API key
GMAIL_ADDRESS=your.email@gmail.com
GMAIL_APP_PASSWORD=your-app-password  # Gmail app password (not your regular password)
RECIPIENT_EMAIL=recipient@example.com
```
- **Do NOT commit your `.env` file to GitHub.**
- [How to get a Gmail app password](https://support.google.com/accounts/answer/185833?hl=en)
- [How to get an OpenAI API key](https://platform.openai.com/account/api-keys)

## Usage

To run the script manually:
```bash
python main.py
```

## Scheduling

### Option 1: GitHub Actions (Cloud Scheduling)
You can automate daily runs using GitHub Actions. Add a workflow file at `.github/workflows/run.yml`:

```yaml
name: Run AI Paper Digest

on:
  schedule:
    - cron: '0 7 * * *'  # Runs at 7:00 UTC every day
  workflow_dispatch:

jobs:
  run-script:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Set up environment variables
        run: |
          echo "OPENAI_API_KEY=${{ secrets.OPENAI_API_KEY }}" >> .env
          echo "GMAIL_ADDRESS=${{ secrets.GMAIL_ADDRESS }}" >> .env
          echo "GMAIL_APP_PASSWORD=${{ secrets.GMAIL_APP_PASSWORD }}" >> .env
          echo "RECIPIENT_EMAIL=${{ secrets.RECIPIENT_EMAIL }}" >> .env
      - name: Run script
        run: python main.py
```

- Add your secrets in your GitHub repo under **Settings > Secrets and variables > Actions**.

### Option 2: Local Scheduling (cron)
On your own machine or server, add a cron job:
```cron
0 7 * * * cd /path/to/AIPaperDigest && /path/to/venv/bin/python main.py
```

## Notes
- The script summarizes the full paper PDF (not just the abstract), but may truncate long papers for efficiency.
- Summaries are formatted as bullet points in the email.
- Suppresses non-critical PDF parsing warnings for cleaner logs.

## Troubleshooting
- If you see warnings like `Cannot set gray stroke color...`, they are harmless and can be ignored.
- If emails are not received, check your spam folder and verify your Gmail app password and recipient address.
- If summaries are cut off, increase the `max_tokens` parameter in `summarizer.py`.

## License
MIT