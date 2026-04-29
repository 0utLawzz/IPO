import gspread
import google.auth
from google.oauth2.service_account import Credentials
import config

class GoogleSheetsManager:
    def __init__(self):
        self.scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        self.credentials = None
        self.client = None
        self.spreadsheet = None
        self.worksheet = None
        self.duplicate_key_column = config.DUPLICATE_KEY_COLUMN  # Use configurable column

    def authenticate(self):
        """Authenticate with Google Sheets API using service account"""
        try:
            self.credentials = Credentials.from_service_account_file(
                config.CREDENTIALS_FILE, scopes=self.scope
            )
            self.client = gspread.authorize(self.credentials)
            print("✓ Successfully authenticated with Google Sheets")
            return True
        except Exception as e:
            print(f"✗ Authentication failed: {e}")
            return False

    def open_spreadsheet_by_id(self, sheet_id):
        """Open spreadsheet by ID"""
        try:
            self.spreadsheet = self.client.open_by_key(sheet_id)
            print(f"✓ Opened spreadsheet by ID: {sheet_id}")
            return True
        except Exception as e:
            print(f"✗ Failed to open spreadsheet by ID: {e}")
            return False

    def get_or_create_worksheet(self, sheet_name):
        """Get existing worksheet or create new one"""
        try:
            # Try to get existing worksheet
            try:
                self.worksheet = self.spreadsheet.worksheet(sheet_name)
                print(f"✓ Opened existing worksheet: {sheet_name}")
                return False  # Not created
            except gspread.WorksheetNotFound:
                # Create new worksheet
                self.worksheet = self.spreadsheet.add_worksheet(title=sheet_name, rows="1000", cols="20")
                print(f"✓ Created new worksheet: {sheet_name}")
                return True  # Just created
        except Exception as e:
            print(f"✗ Failed to get/create worksheet: {e}")
            return None

    def get_existing_key_values(self):
        """Get all existing key values from the sheet for duplicate checking"""
        try:
            if not self.worksheet:
                return set()

            # Get all data from the worksheet
            all_data = self.worksheet.get_all_values()
            if len(all_data) < 2:
                return set()

            # Skip header row, extract key values from configured column
            key_values = set()
            for row in all_data[1:]:
                if len(row) > self.duplicate_key_column:
                    key_values.add(row[self.duplicate_key_column].strip())

            print(f"✓ Found {len(key_values)} existing key values (column {self.duplicate_key_column})")
            return key_values
        except Exception as e:
            print(f"✗ Failed to get existing key values: {e}")
            return set()

    def write_headers(self, headers):
        """Write headers to first row with formatting"""
        try:
            self.worksheet.update('A1', [headers])
            print(f"✓ Headers written: {len(headers)} columns")
            return True
        except Exception as e:
            print(f"✗ Failed to write headers: {e}")
            return False

    def write_new_data(self, data, existing_key_values):
        """Write only new data rows (excluding duplicates)"""
        try:
            new_rows = []
            for row in data:
                if len(row) > self.duplicate_key_column:
                    key_value = row[self.duplicate_key_column].strip()
                    if key_value and key_value not in existing_key_values:
                        new_rows.append(row)
                        existing_key_values.add(key_value)

            if new_rows:
                # Find next empty row
                if self.worksheet.row_count == 1:
                    start_row = 2
                else:
                    values = self.worksheet.col_values(1)
                    start_row = len(values) + 1

                # Write new data
                self.worksheet.update(f'A{start_row}', new_rows)
                print(f"✓ New data written: {len(new_rows)} rows (skipped {len(data) - len(new_rows)} duplicates)")
                return True
            else:
                print(f"✓ No new data to write (all {len(data)} rows were duplicates)")
                return True
        except Exception as e:
            print(f"✗ Failed to write data: {e}")
            return False

    def apply_formatting(self):
        """Apply formatting to the worksheet with Calibri font and center/middle alignment"""
        try:
            if not self.worksheet:
                return False

            # Get all data
            all_data = self.worksheet.get_all_values()
            if not all_data:
                return False

            num_rows = len(all_data)
            num_cols = len(all_data[0]) if all_data else 0

            # Format header row with bold, background color, Calibri font, and center/middle alignment
            header_format = {
                "backgroundColor": {"red": 0.2, "green": 0.4, "blue": 0.8},
                "textFormat": {
                    "bold": True,
                    "foregroundColor": {"red": 1, "green": 1, "blue": 1},
                    "fontFamily": "Calibri",
                    "fontSize": 11
                },
                "horizontalAlignment": "CENTER",
                "verticalAlignment": "MIDDLE"
            }
            self.worksheet.format('A1:' + chr(65 + num_cols - 1) + '1', header_format)

            # Apply alternating row colors with Calibri font and center/middle alignment for data rows
            for i in range(2, num_rows + 1):
                if i % 2 == 0:
                    row_format = {
                        "backgroundColor": {"red": 0.95, "green": 0.95, "blue": 0.95},
                        "textFormat": {
                            "fontFamily": "Calibri",
                            "fontSize": 10
                        },
                        "horizontalAlignment": "CENTER",
                        "verticalAlignment": "MIDDLE"
                    }
                    self.worksheet.format(f'A{i}:{chr(65 + num_cols - 1)}{i}', row_format)
                else:
                    # Odd rows - just Calibri font and center/middle alignment
                    row_format = {
                        "textFormat": {
                            "fontFamily": "Calibri",
                            "fontSize": 10
                        },
                        "horizontalAlignment": "CENTER",
                        "verticalAlignment": "MIDDLE"
                    }
                    self.worksheet.format(f'A{i}:{chr(65 + num_cols - 1)}{i}', row_format)

            # Freeze header row
            self.worksheet.freeze(rows=1)

            print("✓ Formatting applied (Calibri font, center/middle alignment)")
            return True
        except Exception as e:
            print(f"✗ Failed to apply formatting: {e}")
            return False

    def get_spreadsheet_url(self):
        """Get the URL of the spreadsheet"""
        if self.spreadsheet:
            return self.spreadsheet.url
        return None
