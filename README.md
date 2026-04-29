# IPO Pakistan Trademark Scraper

Automated web scraper to extract trademark application data from the IPO Pakistan portal and upload it to Google Sheets or CSV.

## Features

- **Manual Login**: Login manually in the browser (no hardcoded credentials)
- **Cookie Persistence**: Saves login session to avoid repeated logins
- **Pagination Support**: Automatically scrapes all pages of data
- **CSV Fallback**: Saves data to CSV if Google Sheets fails
- **Google Sheets Upload**: Uploads scraped data to Google Sheets

## Prerequisites

1. Python 3.8 or higher installed
2. Google Cloud Project with Google Sheets API enabled (optional, for Google Sheets upload)
3. Service account credentials JSON file (credentials.json) - optional
4. Google Sheet shared with the service account email (optional)

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:
```bash
playwright install chromium
```

3. (Optional) Ensure `credentials.json` is in the project directory for Google Sheets upload

4. Update `config.py` if needed (URLs, spreadsheet name, browser settings)

## Usage

Run the scraper:
```bash
python main.py
```

The script will:
1. Open the browser (visible mode by default)
2. Check for saved cookies - if valid, skip login
3. If no valid cookies, prompt for manual login
4. Save cookies after successful login
5. Navigate to the trademark applications page
6. Scrape all table data from all pages
7. Save data to CSV file (always)
8. Attempt to upload to Google Sheets (if credentials available)
9. Display results

## First Run

On the first run (or when cookies expire):
1. Browser opens and navigates to login page
2. Login manually in the browser
3. Press ENTER in the terminal when done
4. Cookies are saved for future runs

## Subsequent Runs

On subsequent runs:
- Cookies are automatically loaded
- If cookies are valid, login is skipped
- If cookies are expired, you'll be prompted to login again

## Configuration

Edit `config.py` to customize:
- LOGIN_URL: Login page URL
- TARGET_URL: Target page to scrape
- CREDENTIALS_FILE: Google Sheets credentials file
- SPREADSHEET_NAME: Name of Google Sheet
- HEADLESS: Set to True for headless browser mode
- COOKIES_FILE: File to save/load cookies

## Output

- **CSV File**: Always created with timestamp (e.g., `trademark_data_20240426_023000.csv`)
- **Google Sheets**: Created/updated if valid credentials provided

## Troubleshooting

- If login fails, check `login_error.png` for screenshot
- If navigation fails, check `navigation_error.png`
- If scraping fails, check `scraping_error.png`
- Ensure credentials.json has correct permissions for Google Sheets API
- To force re-login, delete `cookies.json` file
