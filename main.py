import asyncio
from playwright.async_api import async_playwright
import config
from google_sheets import GoogleSheetsManager
import csv
from datetime import datetime
import json
import os
import warnings
import logging
import sys

# Suppress subprocess cleanup warnings and logging
warnings.filterwarnings("ignore", category=ResourceWarning)
logging.getLogger('asyncio').setLevel(logging.CRITICAL)

# Suppress subprocess exceptions at exit
def suppress_subprocess_errors(exc_type, exc_value, exc_traceback):
    if exc_type == ValueError and "I/O operation on closed pipe" in str(exc_value):
        return
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

sys.excepthook = suppress_subprocess_errors

class IPOTrademarkScraper:
    def __init__(self, tm_form="TM-05"):
        self.browser = None
        self.page = None
        self.sheets_manager = GoogleSheetsManager()
        self.playwright = None
        self.tm_form = tm_form
        self.target_url = config.TM_FORMS[tm_form]["url"]
        self.sheet_name = config.TM_FORMS[tm_form]["sheet_name"]
        self.duplicate_column = config.TM_FORMS[tm_form]["duplicate_column"]
        self.sheets_manager.duplicate_key_column = self.duplicate_column

    async def init_browser(self):
        """Initialize Playwright browser"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=config.HEADLESS)
        self.page = await self.browser.new_page()
        self.page.set_default_timeout(config.TIMEOUT)
        print("✓ Browser initialized")

    async def load_cookies(self):
        """Load cookies from file if exists"""
        if os.path.exists(config.COOKIES_FILE):
            try:
                with open(config.COOKIES_FILE, 'r') as f:
                    cookies = json.load(f)
                await self.page.context.add_cookies(cookies)
                print(f"✓ Loaded {len(cookies)} cookies from {config.COOKIES_FILE}")
                return True
            except Exception as e:
                print(f"✗ Failed to load cookies: {e}")
                return False
        else:
            print("No saved cookies found")
            return False

    async def save_cookies(self):
        """Save cookies to file"""
        try:
            cookies = await self.page.context.cookies()
            with open(config.COOKIES_FILE, 'w') as f:
                json.dump(cookies, f)
            print(f"✓ Saved {len(cookies)} cookies to {config.COOKIES_FILE}")
            return True
        except Exception as e:
            print(f"✗ Failed to save cookies: {e}")
            return False

    async def check_login_status(self):
        """Check if user is already logged in"""
        try:
            await self.page.goto(config.TARGET_URL)
            await self.page.wait_for_load_state('networkidle')

            # Check if we're redirected to login page
            if 'login' in self.page.url.lower():
                print("Not logged in - login required")
                return False
            else:
                print("✓ Already logged in (using saved cookies)")
                return True
        except:
            return False

    async def close_browser(self):
        """Close the browser"""
        if self.browser:
            await self.browser.close()
            print("✓ Browser closed")

    async def manual_login(self):
        """Open login page and wait for user to manually login"""
        try:
            print(f"Navigating to login page: {config.LOGIN_URL}")
            await self.page.goto(config.LOGIN_URL)
            await self.page.wait_for_load_state('networkidle')

            print("\n" + "=" * 50)
            print("MANUAL LOGIN REQUIRED")
            print("=" * 50)
            print("Please login manually in the browser window.")
            print("After successful login, press ENTER in this terminal to continue...")
            print("=" * 50 + "\n")

            # Wait for user to press Enter
            input()

            # Check current URL for information
            current_url = self.page.url
            print(f"Current URL: {current_url}")

            # Save cookies after successful login
            await self.save_cookies()

            print("✓ Proceeding with automation")
            return True

        except Exception as e:
            print(f"✗ Manual login failed: {e}")
            return False

    async def navigate_to_target_page(self):
        """Navigate to the target page"""
        try:
            await self.page.goto(self.target_url, wait_until="networkidle")
            print(f"✓ Navigated to target page: {self.target_url}")
            return True
        except Exception as e:
            print(f"✗ Failed to navigate to target page: {e}")
            await self.page.screenshot(path="navigation_error.png")
            return False

    async def scrape_table_data(self):
        """Scrape table data from the page with pagination support"""
        try:
            print("Scraping table data...")

            # Wait for page to fully load
            await self.page.wait_for_load_state('networkidle')

            # Find all tables
            tables = await self.page.query_selector_all('table')
            print(f"Found {len(tables)} tables on page")

            if not tables:
                print("✗ No tables found")
                return [], []

            # Find the suitable table (with most rows)
            best_table = None
            max_rows = 0
            header_row = -1

            for table_idx, table in enumerate(tables):
                rows = await table.query_selector_all('tr')
                print(f"Table {table_idx}: {len(rows)} rows")

                if len(rows) > max_rows:
                    max_rows = len(rows)
                    best_table = table

                    # Find header row by looking for expected column names
                    for row_idx, row in enumerate(rows):
                        cells = await row.query_selector_all('td, th')
                        row_text = []
                        for cell in cells:
                            text = await cell.inner_text()
                            row_text.append(text.strip())

                        # Check if this row contains expected headers
                        expected_headers = ['Designated Office', 'Trademark Application No.', 'In Respect of',
                                          'Class No.', 'Business Type', 'Name of Applicant', 'Current Status',
                                          'Application Date Time', 'Edit']
                        if any(h in ' '.join(row_text) for h in expected_headers):
                            header_row = row_idx
                            print(f"Table {table_idx}, Row {row_idx} text: {row_text}")
                            break

            if not best_table:
                print("✗ No suitable table found")
                return [], []

            print(f"✓ Found suitable table (table {tables.index(best_table)}) with header at row {header_row}")

            # Extract headers
            rows = await best_table.query_selector_all('tr')
            if header_row < 0 or header_row >= len(rows):
                print("✗ Header row not found")
                return [], []

            header_cells = await rows[header_row].query_selector_all('td, th')
            headers = []
            for cell in header_cells:
                text = await cell.inner_text()
                headers.append(text.strip())

            print(f"✓ Headers: {headers}")

            # Auto-detect duplicate column based on headers
            if 'Trademark Application No.' in headers:
                self.duplicate_column = headers.index('Trademark Application No.')
                print(f"✓ Using Trademark Application No. (column {self.duplicate_column}) for duplicate checking")
            elif 'Application Date Time' in headers:
                self.duplicate_column = headers.index('Application Date Time')
                print(f"✓ Using Application Date Time (column {self.duplicate_column}) for duplicate checking")
            else:
                print(f"⚠ Using configured column {self.duplicate_column} for duplicate checking")

            # Update sheets manager with detected column
            self.sheets_manager.duplicate_key_column = self.duplicate_column

            # Extract data rows
            data = []
            for row in rows[header_row + 1:]:
                cells = await row.query_selector_all('td, th')
                row_data = []
                for cell in cells:
                    text = await cell.inner_text()
                    row_data.append(text.strip())

                # Only include rows that have data
                if row_data and len(row_data) > 1:
                    data.append(row_data)

            print(f"✓ Scraped {len(data)} data rows from page 1")

            # Take screenshot to see pagination UI
            await self.page.screenshot(path="pagination_debug.png")

            # Handle pagination - look for page numbers and next buttons
            page_num = 1
            max_pages = 3  # Limit to 3 pages for testing
            consecutive_no_data = 0
            max_consecutive_no_data = 2

            while page_num < max_pages:
                page_num += 1
                print(f"\nChecking for page {page_num}...")

                # Look for pagination controls
                pagination_found = False

                # Try multiple selectors for pagination
                pagination_selectors = [
                    'a[href*="page="]',
                    '.pagination a',
                    'table tr td a',
                    'a[onclick*="Page"]',
                    'a[onclick*="page"]',
                    'a:has-text("Next")',
                    'a:has-text("next")',
                    'a:has-text(">")',
                    'a:has-text("»")',
                    'button:has-text("Next")',
                    'button:has-text(">")',
                    '.pager a',
                    '#pagination a',
                    'td a',
                    'tr td a',
                    'a[title*="Next"]',
                    'a[title*="Pages"]',
                    'a span:has-text("...")'
                ]

                # Find all pagination links
                all_links = []
                for selector in pagination_selectors:
                    try:
                        links = await self.page.locator(selector).all()
                        for link in links:
                            try:
                                text = await link.inner_text()
                                href = await link.get_attribute('href')
                                title = await link.get_attribute('title')
                                is_visible = await link.is_visible()
                                is_enabled = await link.is_enabled()
                                all_links.append({
                                    'text': text.strip(),
                                    'href': href,
                                    'title': title,
                                    'visible': is_visible,
                                    'enabled': is_enabled,
                                    'selector': selector
                                })
                            except:
                                continue
                    except:
                        continue

                print(f"Found {len(all_links)} potential pagination links")
                for i, link in enumerate(all_links):  # Show ALL links
                    print(f"  Link {i}: text='{link['text']}', title='{link.get('title', '')}', visible={link['visible']}, enabled={link['enabled']}")

                # Try to find and click next page
                data_before = len(data)

                # Strategy 1: For pages 2-10, click directly. For pages 11+, first click "Next Pages"
                target_page = page_num
                if target_page <= 10:
                    # Click page number directly
                    for link in all_links:
                        if link['visible'] and link['enabled']:
                            if link['text'].strip().isdigit() and int(link['text'].strip()) == target_page:
                                try:
                                    print(f"Clicking page {target_page}")
                                    await self.page.locator(f"a:text-is('{target_page}')").click()
                                    await self.page.wait_for_load_state('networkidle')
                                    await self.page.wait_for_timeout(3000)
                                    pagination_found = True
                                    break
                                except:
                                    continue
                else:
                    # For pages 11+, first click "Next Pages" to reveal higher page numbers
                    print(f"Target page {target_page} is beyond 10 - clicking Next Pages first")
                    for link in all_links:
                        if link['visible'] and link['enabled']:
                            title = link.get('title', '')
                            if title == 'Next Pages' and link['text'] == '...':
                                try:
                                    print(f"Clicking 'Next Pages' link")
                                    await self.page.locator(f"a[title='Next Pages']").click()
                                    await self.page.wait_for_load_state('networkidle')
                                    await self.page.wait_for_timeout(3000)
                                    # Now look for the target page number
                                    for selector in pagination_selectors:
                                        try:
                                            links = await self.page.locator(selector).all()
                                            for link in links:
                                                try:
                                                    text = await link.inner_text()
                                                    if text.strip().isdigit() and int(text.strip()) == target_page:
                                                        try:
                                                            print(f"Clicking page {target_page}")
                                                            await self.page.locator(f"a:text-is('{target_page}')").click()
                                                            await self.page.wait_for_load_state('networkidle')
                                                            await self.page.wait_for_timeout(3000)
                                                            pagination_found = True
                                                            break
                                                        except:
                                                            continue
                                                except:
                                                    continue
                                            if pagination_found:
                                                break
                                        except:
                                            continue
                                    break
                                except:
                                    continue
                            if pagination_found:
                                break

                # Strategy 2: Look for "Next" or ">" text
                if not pagination_found:
                    for link in all_links:
                        if link['visible'] and link['enabled']:
                            text_lower = link['text'].lower()
                            if text_lower in ['next', '>', '»', 'next page']:
                                try:
                                    print(f"Clicking Next button with text: {link['text']}")
                                    await self.page.locator(f"a:text-is('{link['text']}')").click()
                                    await self.page.wait_for_load_state('networkidle')
                                    await self.page.wait_for_timeout(3000)
                                    pagination_found = True
                                    break
                                except:
                                    continue

                # Strategy 2: If no Next button, try to find page numbers and click next number
                if not pagination_found:
                    page_numbers = []
                    for link in all_links:
                        if link['visible'] and link['enabled']:
                            # Check if text is a number
                            text = link['text'].strip()
                            if text.isdigit():
                                page_numbers.append(int(text))

                    if page_numbers:
                        # We're currently on page 1, so try to click page 2
                        target_page = page_num
                        print(f"Trying to click page {target_page}")
                        # Try to find a link with the target page number
                        for link in all_links:
                            if link['visible'] and link['enabled']:
                                text = link['text'].strip()
                                if text.isdigit() and int(text) == target_page:
                                    try:
                                        print(f"Clicking page number: {text}")
                                        await self.page.locator(f"a:text-is('{text}')").click()
                                        await self.page.wait_for_load_state('networkidle')
                                        await self.page.wait_for_timeout(3000)
                                        pagination_found = True
                                        break
                                    except:
                                        continue

                if pagination_found:
                    # Scrape data from new page
                    tables = await self.page.locator('table').all()
                    for table in tables:
                        try:
                            if not await table.is_visible():
                                continue

                            table_rows = await table.locator('tr').all()

                            if len(table_rows) > header_row_idx:
                                # Process data rows
                                for i in range(header_row_idx + 1, len(table_rows)):
                                    try:
                                        cells = await table_rows[i].locator('td').all()
                                        row_data = []

                                        for cell in cells:
                                            text = await cell.inner_text()
                                            text = ' '.join(text.split())
                                            row_data.append(text)

                                        if row_data and len(row_data) > 1:
                                            data.append(row_data[:-1])
                                    except:
                                        continue
                        except:
                            continue

                    data_after = len(data)
                    if data_after > data_before:
                        print(f"✓ Scraped {data_after - data_before} rows from page {page_num}")
                        consecutive_no_data = 0
                    else:
                        print(f"No new data on page {page_num}")
                        consecutive_no_data += 1
                        if consecutive_no_data >= max_consecutive_no_data:
                            print(f"No new data for {max_consecutive_no_data} consecutive pages - stopping")
                            break
                else:
                    print(f"No pagination controls found - stopping")
                    break

            print(f"✓ Total scraped {len(data)} data rows from {page_num} pages")

            # Verification: Get total count from page counter
            try:
                # Look for total count text (e.g., "471 items in 19 pages")
                page_text = await self.page.inner_text('body')
                import re
                # Match patterns like "471 items", "471 items in 19 pages", etc.
                total_match = re.search(r'(\d+)\s+items', page_text, re.IGNORECASE)
                if total_match:
                    page_total = int(total_match.group(1))
                    print(f"✓ Page counter shows: {page_total} items")
                    print(f"✓ Scraped: {len(data)} items")
                    if page_total == len(data):
                        print("✓ VERIFICATION PASSED: Scraped count matches page counter")
                    else:
                        print(f"⚠ VERIFICATION WARNING: Scraped count ({len(data)}) != Page counter ({page_total})")
            except Exception as e:
                print(f"⚠ Could not verify with page counter: {e}")

            return headers, data

        except Exception as e:
            print(f"✗ Scraping failed: {e}")
            await self.page.screenshot(path="scraping_error.png")
            return [], []

    def save_to_csv(self, headers, data):
        """Save data to CSV file as fallback"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"trademark_data_{timestamp}.csv"

            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                writer.writerows(data)

            print(f"✓ Data saved to CSV: {filename}")
            return True
        except Exception as e:
            print(f"✗ Failed to save CSV: {e}")
            return False

    async def run(self):
        """Main execution flow"""
        print("=" * 50)
        print("IPO Pakistan Trademark Scraper")
        print("=" * 50)

        # Initialize browser
        await self.init_browser()

        # Try to load cookies and check if already logged in
        cookies_loaded = await self.load_cookies()
        if cookies_loaded:
            if await self.check_login_status():
                # Already logged in, proceed to target page
                print("✓ Using saved session - no login required")
            else:
                # Cookies expired, need manual login
                print("✗ Saved cookies expired - manual login required")
                if not await self.manual_login():
                    await self.close_browser()
                    return False
        else:
            # No saved cookies, need manual login
            print("No saved cookies - manual login required")
            if not await self.manual_login():
                await self.close_browser()
                return False

        # Navigate to target page
        if not await self.navigate_to_target_page():
            await self.close_browser()
            return False

        # Scrape table data
        headers, data = await self.scrape_table_data()

        if not data:
            print("✗ No data scraped")
            await self.close_browser()
            return False

        # Close browser
        await self.close_browser()

        # Save to CSV as fallback
        print("\n" + "=" * 50)
        print("Saving data to CSV...")
        print("=" * 50)
        self.save_to_csv(headers, data)

        # Try to upload to Google Sheets
        print("\n" + "=" * 50)
        print("Attempting to upload to Google Sheets...")
        print("=" * 50)

        if not self.sheets_manager.authenticate():
            print("✗ Google Sheets authentication failed - data saved to CSV instead")
            print("\n" + "=" * 50)
            print("✓ AUTOMATION COMPLETED (CSV ONLY)")
            print("=" * 50)
            print(f"Total rows: {len(data)}")
            print("Note: Update credentials.json to enable Google Sheets upload")
            print("=" * 50)
            return True

        if not self.sheets_manager.open_spreadsheet_by_id(config.SHEET_ID):
            print("✗ Failed to open spreadsheet by ID - data saved to CSV instead")
            print("\n" + "=" * 50)
            print("✓ AUTOMATION COMPLETED (CSV ONLY)")
            print("=" * 50)
            print(f"Total rows: {len(data)}")
            print("=" * 50)
            return True

        worksheet_created = self.sheets_manager.get_or_create_worksheet(self.sheet_name)
        if worksheet_created is None:
            print("✗ Failed to get/create worksheet - data saved to CSV instead")
            print("\n" + "=" * 50)
            print("✓ AUTOMATION COMPLETED (CSV ONLY)")
            print("=" * 50)
            print(f"Total rows: {len(data)}")
            print("=" * 50)
            return True

        # Get existing key values for duplicate checking
        existing_key_values = self.sheets_manager.get_existing_key_values()

        # Always write headers if worksheet was just created
        if worksheet_created:
            print("Newly created worksheet, writing headers...")
            if not self.sheets_manager.write_headers(headers):
                print("✗ Failed to write headers - data saved to CSV instead")
                print("\n" + "=" * 50)
                print("✓ AUTOMATION COMPLETED (CSV ONLY)")
                print("=" * 50)
                print(f"Total rows: {len(data)}")
                print("=" * 50)
                return True
        else:
            # Check if existing worksheet is empty, write headers if needed
            worksheet_data = self.sheets_manager.worksheet.get_all_values()
            if not worksheet_data:
                print("Existing worksheet is empty, writing headers...")
                if not self.sheets_manager.write_headers(headers):
                    print("✗ Failed to write headers - data saved to CSV instead")
                    print("\n" + "=" * 50)
                    print("✓ AUTOMATION COMPLETED (CSV ONLY)")
                    print("=" * 50)
                    print(f"Total rows: {len(data)}")
                    print("=" * 50)
                    return True
            else:
                print(f"Worksheet already has {len(worksheet_data)} rows, skipping headers")

        # Write new data (excluding duplicates)
        if not self.sheets_manager.write_new_data(data, existing_key_values):
            print("✗ Failed to write data - data saved to CSV instead")
            print("\n" + "=" * 50)
            print("✓ AUTOMATION COMPLETED (CSV ONLY)")
            print("=" * 50)
            print(f"Total rows: {len(data)}")
            print("=" * 50)
            return True

        # Apply formatting
        if not self.sheets_manager.apply_formatting():
            print("⚠ Warning: Failed to apply formatting (data still saved)")

        # Print success message with URL
        url = self.sheets_manager.get_spreadsheet_url()
        print("\n" + "=" * 50)
        print("✓ AUTOMATION COMPLETED SUCCESSFULLY")
        print("=" * 50)
        print(f"TM Form: {self.tm_form}")
        print(f"Data uploaded to: {url}")
        print(f"Worksheet: {self.sheet_name}")
        print("=" * 50)

        return True


def display_main_menu():
    """Display the main menu"""
    print("\n" + "=" * 60)
    print(" " * 15 + "IPO TRADEMARK SCRAPER")
    print("=" * 60)
    print("1. Number Check [PENDING]")
    print("2. Acknowledgements [PENDING]")
    print("3. Submission")
    print("0. Exit")
    print("=" * 60)
    choice = input("Select an option: ")
    return choice


def display_submission_menu():
    """Display the submission sub-menu in a bordered table format"""
    print("\n" + "=" * 100)
    print(" " * 30 + "SUBMISSION MENU")
    print("=" * 100)

    # Table header
    print("┌" + "─" * 4 + "┬" + "─" * 8 + "┬" + "─" * 60 + "┬" + "─" * 15 + "┐")
    print("│ No │ TM Form │ Description                                           │ Fee (PKR)    │")
    print("├" + "─" * 4 + "┼" + "─" * 8 + "┼" + "─" * 60 + "┼" + "─" * 15 + "┤")

    # Table rows - use TM number as selection key
    tm_list = sorted(config.TM_FORMS.keys())
    for tm in tm_list:
        form_info = config.TM_FORMS[tm]
        desc = form_info['description'][:57] + "..." if len(form_info['description']) > 57 else form_info['description']
        fee = str(form_info['fee'])
        tm_num = tm.split('-')[1]  # Extract number from TM-XX
        print(f"│ {tm_num:2} │ {tm:6} │ {desc:<57} │ {fee:<11} │")

    # Table footer
    print("├" + "─" * 4 + "┼" + "─" * 8 + "┼" + "─" * 60 + "┼" + "─" * 15 + "┤")
    print("│  0 │ Back    │ Return to Main Menu" + " " * 39 + "│              │")
    print("└" + "─" * 4 + "┴" + "─" * 8 + "┴" + "─" * 60 + "┴" + "─" * 15 + "┘")
    print("=" * 100)
    choice = input("Select TM Form (enter TM number, e.g., 11 for TM-11): ")
    return choice


async def run_scraper(tm_form):
    """Run the scraper for the selected TM form"""
    print("\n" + "=" * 60)
    print(f" " * 10 + f"SCRAPING {tm_form} DATA")
    print("=" * 60)
    
    scraper = IPOTrademarkScraper(tm_form)
    await scraper.run()


async def main():
    """Main function with menu system"""
    while True:
        choice = display_main_menu()

        if choice == "0":
            print("\nExiting...")
            break
        elif choice == "1":
            print("\n⚠ Number Check feature is pending implementation")
        elif choice == "2":
            print("\n⚠ Acknowledgements feature is pending implementation")
        elif choice == "3":
            while True:
                sub_choice = display_submission_menu()

                if sub_choice == "0":
                    break

                try:
                    # Convert TM number to TM-XX format
                    tm_num = sub_choice.zfill(2)  # Pad with zero if single digit
                    tm_form = f"TM-{tm_num}"

                    if tm_form in config.TM_FORMS:
                        await run_scraper(tm_form)
                    else:
                        print(f"\n⚠ Invalid TM number: {sub_choice}. Please try again.")
                except ValueError:
                    print("\n⚠ Invalid input. Please enter a TM number.")
        else:
            print("\n⚠ Invalid selection. Please try again.")


if __name__ == "__main__":
    asyncio.run(main())
