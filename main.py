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
import re
import argparse
import signal


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
        self.session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.export_root = getattr(config, 'EXPORT_ROOT', 'export')
        self.session_dir = os.path.join(self.export_root, 'sessions', self.session_timestamp, self.tm_form)
        self.tm_export_dir = os.path.join(self.export_root, self.tm_form)
        os.makedirs(self.session_dir, exist_ok=True)
        os.makedirs(self.tm_export_dir, exist_ok=True)
        self.session_stats = {
            'tm_form': self.tm_form,
            'session_timestamp': self.session_timestamp,
            'scraped_total': 0,
            'duplicates_skipped': 0,
            'new_rows_written': 0,
        }

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
        try:
            if self.page:
                try:
                    await self.page.close()
                except:
                    pass
            if self.browser:
                try:
                    await self.browser.close()
                except:
                    pass
            if self.playwright:
                try:
                    await self.playwright.stop()
                except:
                    pass
        finally:
            self.page = None
            self.browser = None
            self.playwright = None
            print("✓ Browser closed")

    async def automated_login(self):
        try:
            print(f"Navigating to login page: {config.LOGIN_URL}")
            await self.page.goto(config.LOGIN_URL)
            await self.page.wait_for_load_state('networkidle')

            username_selector = "#ctl00_ContentPlaceHolder1_txtUsername"
            await self.page.wait_for_selector(username_selector, state='visible')
            username = getattr(config, 'USERNAME', '')
            password = getattr(config, 'PASSWORD', '')

            await self.page.locator(username_selector).click()
            await self.page.keyboard.press('Control+A')
            await self.page.keyboard.press('Backspace')
            await self.page.keyboard.type(str(username), delay=80)

            try:
                current_val = await self.page.locator(username_selector).input_value()
            except:
                current_val = ""

            digits_in_val = re.sub(r"\D", "", current_val or "")
            if digits_in_val != re.sub(r"\D", "", str(username)):
                await self.page.evaluate(
                    """(args) => {
                        const [sel, val] = args;
                        const el = document.querySelector(sel);
                        if (!el) return false;
                        el.focus();
                        el.value = val;
                        el.dispatchEvent(new Event('input', { bubbles: true }));
                        el.dispatchEvent(new Event('change', { bubbles: true }));
                        return true;
                    }""",
                    [username_selector, str(username)],
                )

            password_selectors = [
                "#ctl00_ContentPlaceHolder1_txtPassword",
                "input[type='password']",
                "input[id*='Password' i]",
                "input[name*='Password' i]",
            ]
            password_filled = False
            for sel in password_selectors:
                try:
                    loc = self.page.locator(sel).first
                    if await loc.count() == 0:
                        continue
                    await loc.click()
                    await self.page.keyboard.press('Control+A')
                    await self.page.keyboard.press('Backspace')
                    await loc.fill(str(password))
                    password_filled = True
                    break
                except:
                    continue
            if not password_filled:
                raise Exception("Password field not found")

            submit_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button:has-text('Login')",
                "button:has-text('Sign')",
                "input[value*='Login' i]",
            ]
            clicked = False
            for sel in submit_selectors:
                try:
                    loc = self.page.locator(sel).first
                    if await loc.count() == 0:
                        continue
                    await loc.click()
                    clicked = True
                    break
                except:
                    continue
            if not clicked:
                await self.page.keyboard.press('Enter')

            await self.page.wait_for_load_state('networkidle')

            try:
                await self.page.wait_for_timeout(1500)
            except:
                pass

            # Determine success by checking if username field still exists/visible or URL still on login.
            still_login_url = 'login' in (self.page.url or '').lower()
            username_still_visible = False
            try:
                username_still_visible = await self.page.locator(username_selector).is_visible()
            except:
                username_still_visible = False

            if still_login_url and username_still_visible:
                print("✗ Login appears to have failed (still on login page)")
                await self.page.screenshot(path=os.path.join(self.session_dir, "login_failed.png"))
                return False

            await self.save_cookies()
            print("✓ Logged in successfully")
            return True
        except Exception as e:
            print(f"✗ Automated login failed: {e}")
            try:
                await self.page.screenshot(path=os.path.join(self.session_dir, "login_error.png"))
            except:
                pass
            return False

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

        except KeyboardInterrupt:
            raise

        except Exception as e:
            print(f"✗ Manual login failed: {e}")
            try:
                await self.page.screenshot(path=os.path.join(self.session_dir, "manual_login_error.png"))
            except:
                pass
            return False

    async def navigate_to_target_page(self):
        """Navigate to the target page"""
        try:
            await self.page.goto(self.target_url, wait_until="networkidle")
            print(f"✓ Navigated to target page: {self.target_url}")
            return True
        except Exception as e:
            print(f"✗ Failed to navigate to target page: {e}")
            await self.page.screenshot(path=os.path.join(self.session_dir, "navigation_error.png"))
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
            await self.page.screenshot(path=os.path.join(self.session_dir, "pagination_debug.png"))

            # Handle pagination - look for page numbers and next buttons
            page_num = 1
            max_pages = getattr(config, 'MAX_PAGES', None)
            consecutive_no_data = 0
            max_consecutive_no_data = 2

            while max_pages is None or page_num < max_pages:
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

                            if len(table_rows) > header_row:
                                # Process data rows
                                for i in range(header_row + 1, len(table_rows)):
                                    try:
                                        cells = await table_rows[i].locator('td').all()
                                        row_data = []

                                        for cell in cells:
                                            text = await cell.inner_text()
                                            text = ' '.join(text.split())
                                            row_data.append(text)

                                        if row_data and len(row_data) > 1:
                                            data.append(row_data)
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
            await self.page.screenshot(path=os.path.join(self.session_dir, "scraping_error.png"))
            return [], []

    def save_to_csv(self, headers, data):
        """Save data to CSV file as fallback"""
        try:
            filename = f"{self.tm_form}_trademark_data_{self.session_timestamp}.csv"
            session_path = os.path.join(self.session_dir, filename)
            tm_path = os.path.join(self.tm_export_dir, filename)

            with open(session_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                writer.writerows(data)

            with open(tm_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                writer.writerows(data)

            print(f"✓ Data saved to CSV: {session_path}")
            return True
        except Exception as e:
            print(f"✗ Failed to save CSV: {e}")
            return False

    def save_session_summary(self):
        try:
            summary_path = os.path.join(self.session_dir, "session_summary.json")
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(self.session_stats, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"✗ Failed to save session summary: {e}")
            return False

    async def run(self):
        """Main execution flow"""
        print("=" * 50)
        version = getattr(config, 'APP_VERSION', None)
        if version:
            print(f"IPO Pakistan Trademark Scraper v{version}")
        else:
            print("IPO Pakistan Trademark Scraper")
        print("=" * 50)

        await self.init_browser()
        try:
            cookies_loaded = await self.load_cookies()
            if cookies_loaded and await self.check_login_status():
                print("✓ Using saved session - no login required")
            else:
                login_mode = str(getattr(config, 'LOGIN_MODE', 'manual')).strip().lower()
                if login_mode == 'auto':
                    ok = await self.automated_login()
                else:
                    ok = await self.manual_login()
                if not ok:
                    return False

            if not await self.navigate_to_target_page():
                return False

            headers, data = await self.scrape_table_data()
            self.session_stats['scraped_total'] = len(data)

            if not data:
                print("✗ No data scraped")
                self.save_session_summary()
                return False

            print("\n" + "=" * 50)
            print("Saving data to CSV...")
            print("=" * 50)
            self.save_to_csv(headers, data)

            print("\n" + "=" * 50)
            print("Attempting to upload to Google Sheets...")
            print("=" * 50)

            if not self.sheets_manager.authenticate():
                print("✗ Google Sheets authentication failed - data saved to CSV instead")
                self.save_session_summary()
                return True

            if not self.sheets_manager.open_spreadsheet_by_id(config.SHEET_ID):
                print("✗ Failed to open spreadsheet by ID - data saved to CSV instead")
                self.save_session_summary()
                return True

            worksheet_created = self.sheets_manager.get_or_create_worksheet(self.sheet_name)
            if worksheet_created is None:
                print("✗ Failed to get/create worksheet - data saved to CSV instead")
                self.save_session_summary()
                return True

            existing_key_values = self.sheets_manager.get_existing_key_values()

            if worksheet_created:
                print("Newly created worksheet, writing headers...")
                if not self.sheets_manager.write_headers(headers):
                    print("✗ Failed to write headers - data saved to CSV instead")
                    self.save_session_summary()
                    return True
            else:
                worksheet_data = self.sheets_manager.worksheet.get_all_values()
                if not worksheet_data:
                    print("Existing worksheet is empty, writing headers...")
                    if not self.sheets_manager.write_headers(headers):
                        print("✗ Failed to write headers - data saved to CSV instead")
                        self.save_session_summary()
                        return True
                else:
                    print(f"Worksheet already has {len(worksheet_data)} rows, skipping headers")

            always_append = bool(getattr(config, 'ALWAYS_APPEND_TO_SHEETS', False))
            if always_append:
                # Always append all rows; we still compute an estimated duplicates count by comparing with existing keys.
                duplicates_estimate = 0
                for row in data:
                    if len(row) > self.duplicate_column:
                        key_value = row[self.duplicate_column].strip()
                        if key_value and key_value in existing_key_values:
                            duplicates_estimate += 1
                write_stats = {
                    'attempted': len(data),
                    'written': len(data),
                    'duplicates': duplicates_estimate,
                }

                # Append in one go at next empty row
                values = self.sheets_manager.worksheet.col_values(1)
                start_row = len(values) + 1
                self.sheets_manager.worksheet.update(range_name=f'A{start_row}', values=data)
                print(f"✓ Data appended: {len(data)} rows (duplicates estimate: {duplicates_estimate})")
            else:
                write_stats = self.sheets_manager.write_new_data(data, existing_key_values)
            if write_stats is None:
                print("✗ Failed to write data - data saved to CSV instead")
                self.save_session_summary()
                return True

            self.session_stats['duplicates_skipped'] = int(write_stats.get('duplicates', 0))
            self.session_stats['new_rows_written'] = int(write_stats.get('written', 0))

            if not self.sheets_manager.apply_formatting():
                print("⚠ Warning: Failed to apply formatting (data still saved)")

            url = self.sheets_manager.get_spreadsheet_url()
            print("\n" + "=" * 50)
            print("✓ AUTOMATION COMPLETED SUCCESSFULLY")
            print("=" * 50)
            print(f"TM Form: {self.tm_form}")
            print(f"Data uploaded to: {url}")
            print(f"Worksheet: {self.sheet_name}")
            print(f"Scraped this run: {self.session_stats['scraped_total']}")
            print(f"New rows written: {self.session_stats['new_rows_written']}")
            print(f"Duplicates skipped: {self.session_stats['duplicates_skipped']}")
            print("=" * 50)

            self.save_session_summary()
            return True
        finally:
            await self.close_browser()


def display_main_menu():
    """Display the main menu"""
    print("\n" + "=" * 60)
    print(" " * 15 + "IPO TRADEMARK SCRAPER")
    print("=" * 60)
    print("1. Number Check [PENDING]")
    print("2. Acknowledgements [PENDING]")
    print("3. Submission")
    print("4. Run All (Configured TM List) and Exit")
    print("0. Exit")
    print("=" * 60)
    try:
        choice = input("Select an option: ")
    except EOFError:
        return "0"
    return choice


def display_submission_menu():
    """Display the submission sub-menu in a bordered table format"""
    print("\n" + "=" * 100)
    print(" " * 30 + "SUBMISSION MENU")
    print("=" * 100)

    # Table header
    print("┌" + "─" * 4 + "┬" + "─" * 8 + "┬" + "─" * 60 + "┬" + "─" * 15 + "┐")
    print("│ No │ TM Form │ Description                                           │ Fee (PKR)    │ Run │ Dup │")
    print("├" + "─" * 4 + "┼" + "─" * 8 + "┼" + "─" * 60 + "┼" + "─" * 15 + "┼" + "─" * 5 + "┼" + "─" * 5 + "┤")

    # Table rows - use TM number as selection key
    tm_list = sorted(config.TM_FORMS.keys())
    for tm in tm_list:
        form_info = config.TM_FORMS[tm]
        desc = form_info['description'][:57] + "..." if len(form_info['description']) > 57 else form_info['description']
        fee = str(form_info['fee'])
        tm_num = tm.split('-')[1]  # Extract number from TM-XX
        dup_col = form_info.get('duplicate_column', None)
        dup_enabled = bool(form_info.get('duplicate_check', True))
        run_enabled = tm in resolve_tm_forms_for_run()

        if not dup_enabled or dup_col is None:
            dup_label = "OFF"
        else:
            # dup_col is 0-based index -> Excel style letter (A=0)
            dup_label = f"COL {chr(65 + int(dup_col))}"

        run_label = "YES" if run_enabled else "NO"
        print(f"│ {tm_num:2} │ {tm:6} │ {desc:<57} │ {fee:<11} │ {run_label:<3} │ {dup_label:<3} │")

    # Table footer
    print("├" + "─" * 4 + "┼" + "─" * 8 + "┼" + "─" * 60 + "┼" + "─" * 15 + "┼" + "─" * 5 + "┼" + "─" * 5 + "┤")
    print("│  0 │ Back    │ Return to Main Menu" + " " * 39 + "│              │     │     │")
    print("└" + "─" * 4 + "┴" + "─" * 8 + "┴" + "─" * 60 + "┴" + "─" * 15 + "┴" + "─" * 5 + "┴" + "─" * 5 + "┘")
    print("=" * 100)
    try:
        choice = input("Select TM Form (enter TM number, e.g., 11 for TM-11): ")
    except EOFError:
        return "0"
    return choice


def resolve_tm_forms_for_run():
    forms = list(getattr(config, 'TM_RUN_FORMS', []))
    if not forms:
        return sorted(config.TM_FORMS.keys())
    return [f for f in forms if f in config.TM_FORMS]


async def run_all_configured_and_exit():
    forms = resolve_tm_forms_for_run()
    print("\n" + "=" * 60)
    print("RUN ALL (CONFIGURED) - START")
    print("=" * 60)
    for tm_form in forms:
        await run_scraper(tm_form)
    print("\n" + "=" * 60)
    print("RUN ALL (CONFIGURED) - DONE")
    print("=" * 60)


async def run_scraper(tm_form):
    """Run the scraper for the selected TM form"""
    print("\n" + "=" * 60)
    print(f" " * 10 + f"SCRAPING {tm_form} DATA")
    print("=" * 60)
    
    scraper = IPOTrademarkScraper(tm_form)
    form_info = config.TM_FORMS.get(tm_form, {})
    if not bool(form_info.get('duplicate_check', True)):
        scraper.duplicate_column = None
        scraper.sheets_manager.duplicate_key_column = None
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
        elif choice == "4":
            await run_all_configured_and_exit()
            break
        else:
            print("\n⚠ Invalid selection. Please try again.")


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.default_int_handler)

    def run_with_ctrl_c(coro):
        try:
            asyncio.run(coro)
        except KeyboardInterrupt:
            print("\nStopping (Ctrl+C)...")
        except EOFError:
            print("\nStopping (EOF)...")

    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument('--tm', dest='tm_form', help='Run directly for a TM form (e.g., TM-11)', default=None)
    parser.add_argument('--all', dest='run_all', action='store_true', help='Run all configured TM forms and exit')
    args = parser.parse_args()

    if args.run_all:
        run_with_ctrl_c(run_all_configured_and_exit())
    elif args.tm_form:
        run_with_ctrl_c(run_scraper(args.tm_form))
    else:
        run_with_ctrl_c(main())
