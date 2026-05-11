# IPO Pakistan Trademark Scraper

Automated web scraper to extract trademark application data from IPO Pakistan portal.

Version: 1.0.0

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Run scraper
python main.py

# Run all configured TM forms and exit (for hourly automation)
python main.py --all
```

## Features

- **Manual Login**: Secure manual authentication (no hardcoded credentials)
- **Session Persistence**: Cookies saved to avoid repeated logins
- **Pagination**: Auto-scrapes all pages of data
- **Data Export**: CSV export to `export/` folder
- **Google Sheets**: Optional cloud upload with service account
- **Run All Mode**: Runs all configured TM forms and exits (for Task Scheduler)
- **Graceful Stop**: Press `CTRL + C` to stop safely

## Project Structure

```text
├── main.py              # Main scraper script
├── config.py            # Configuration settings
├── google_sheets.py     # Google Sheets integration
├── export/              # CSV export data (gitignored)
├── cookies.json         # Session persistence
└── credentials.json     # Google Sheets service account (not in repo)
```

## Configuration

Edit `config.py`:

- `LOGIN_URL` / `TARGET_URL` - Portal URLs
- `SPREADSHEET_NAME` - Google Sheet name
- `HEADLESS` - Run browser headless (True/False)
- `TM_RUN_FORMS` - Which TM forms are included in `--all` mode

## Usage

1. **First Run**: Browser opens → Login manually → Press ENTER → Session saved
2. **Subsequent Runs**: Auto-login with saved cookies
3. **Output**: CSV files saved to `export/` folder

### Menu

- Use `Submission` to run a single TM.
- Use `Run All (Configured TM List) and Exit` to run everything in `TM_RUN_FORMS`.

### Hourly Workflow (Windows Task Scheduler)

Create a scheduled task that runs every hour:

```bash
python main.py --all
```

Make sure your first run has completed manual login and created `cookies.json`.

### GitHub Actions (Hourly)

This repo includes a GitHub Actions workflow at `.github/workflows/hourly.yml` that runs every hour.

Notes:

- The IPO portal uses CAPTCHA. A headless CI runner cannot complete CAPTCHA/manual login.
- If you still enable the workflow, expect it to fail when authentication is required.
- Do not commit `credentials.json` or `cookies.json`. Use GitHub Secrets instead.

## Requirements

- Python 3.8+
- Playwright
- Google Cloud credentials (optional, for Sheets upload)

## Notes

- `export/` folder is gitignored (keeps data private)
- `credentials.json` is gitignored (keep service account secure)
- Delete `cookies.json` to force re-login

### DO NOT CHANGE SCRAPING LOGIC

Do not refactor or change selectors/scraping logic unless you are intentionally updating the scraper.

## Deployment (Next Task)

Planned next step: build a React UI and deploy to Vercel.
