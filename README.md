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

#### Configure GitHub Secrets (Recommended)

Go to:

`GitHub repo -> Settings -> Secrets and variables -> Actions`

Add these secrets:

- **`GOOGLE_SERVICE_ACCOUNT_JSON`**
  - Value: the full JSON contents of your Google service account file (the same content as `credentials.json`).

Optional environment variables (if you use them later):

- **`IPO_LOGIN_MODE`**: `manual` or `auto`
- **`IPO_USERNAME`**
- **`IPO_PASSWORD`**

#### How to use secrets in the workflow

If you want CI to use Google Sheets credentials, you must write the secret into a file during the workflow run (never commit it):

Example step:

```yaml
- name: Create credentials.json from secret
  run: |
    echo "${{ secrets.GOOGLE_SERVICE_ACCOUNT_JSON }}" > credentials.json
```

#### CAPTCHA limitation

Even with secrets configured, authentication to IPO portal usually still fails in CI because CAPTCHA cannot be solved.

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

## Web Dashboard (React + Next.js)

A modern React dashboard has been created in the `web/` folder with:

- **Sidebar navigation**: All 17 TM forms with duplicate check indicators
- **Stats cards**: Application metrics with trend indicators
- **Data table**: Sortable, filterable trademark applications
- **Theme**: Sequence brand colors (teal primary, green accent)

### Local Development

```bash
cd web
npm install
npm run dev
```

### Build for Production

```bash
cd web
npm run build
```

## Vercel Deployment

### One-Click Deploy

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new)

### Manual Deploy

1. Push code to GitHub
2. Go to [vercel.com](https://vercel.com) and import your repo
3. Set root directory to `web/`
4. Deploy!

Or use Vercel CLI:

```bash
cd web
vercel --prod
```

### Environment Variables (Optional)

If connecting to live APIs later:

- `NEXT_PUBLIC_API_URL` - Backend API endpoint
- `NEXT_PUBLIC_SHEET_ID` - Google Sheets ID
