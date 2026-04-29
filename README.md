# IPO Pakistan Trademark Scraper

Automated web scraper to extract trademark application data from IPO Pakistan portal.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Run scraper
python main.py
```

## Features

- **Manual Login**: Secure manual authentication (no hardcoded credentials)
- **Session Persistence**: Cookies saved to avoid repeated logins
- **Pagination**: Auto-scrapes all pages of data
- **Data Export**: CSV export to `export/` folder
- **Google Sheets**: Optional cloud upload with service account

## Project Structure

```
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

## Usage

1. **First Run**: Browser opens → Login manually → Press ENTER → Session saved
2. **Subsequent Runs**: Auto-login with saved cookies
3. **Output**: CSV files saved to `export/` folder

## Requirements

- Python 3.8+
- Playwright
- Google Cloud credentials (optional, for Sheets upload)

## Notes

- `export/` folder is gitignored (keeps data private)
- `credentials.json` is gitignored (keep service account secure)
- Delete `cookies.json` to force re-login
