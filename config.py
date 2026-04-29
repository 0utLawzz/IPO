# Configuration file for IPO Pakistan Trademark Scraper

# Login credentials (will be prompted at runtime)
USERNAME = None
PASSWORD = None

# URLs
LOGIN_URL = "https://apply.ipo.gov.pk/UserLogin"

# Google Sheets configuration
CREDENTIALS_FILE = "credentials.json"
SPREADSHEET_NAME = "TM"
SHEET_ID = "1CLZSTLR17cSTo-ERZkpRc1HuXYQ93PZumxyQY5x0qZ4"

# TM Form configurations (from official IPO Pakistan fee schedule)
TM_FORMS = {
    "TM-01": {
        "url": "https://apply.ipo.gov.pk/View_User_Application_Trademark_01",
        "sheet_name": "TM-01",
        "description": "Application for registration of trade mark for goods or services and to register a domain name under section 22(1), section 84(2); rule 12",
        "fee": 3000,
        "duplicate_column": 7  # Application Date Time
    },
    "TM-02": {
        "url": "https://apply.ipo.gov.pk/View_User_Application_Trademark_02",
        "sheet_name": "TM-02",
        "description": "Application for Registration of a Trade Mark for Goods or Services (other than a Collective or a Certification Trade Mark) in the Register from a Convention Country under Section 25, 22 and Rule 15 and for Registration to Provide Temporary Protection during Exhibition under Section 26",
        "fee": 3000,
        "duplicate_column": 2  # Trademark Application No.
    },
    "TM-05": {
        "url": "https://apply.ipo.gov.pk/View_User_Application_Trademark_05",
        "sheet_name": "TM-05",
        "description": "Notice of Opposition to Application for Registration of a Trade Mark [Section 28, Rule 31]",
        "fee": 9000,
        "duplicate_column": 1  # Trademark Application No.
    },
    "TM-06": {
        "url": "https://apply.ipo.gov.pk/View_User_Application_Trademark_06",
        "sheet_name": "TM-06",
        "description": "Form of Counter-statement. [Section 28, 37, 73, 80, 96 & 97(5), Rule 30(2) & 72(1)]",
        "fee": 1500,
        "duplicate_column": 2  # Trademark Application No.
    },
    "TM-07": {
        "url": "https://apply.ipo.gov.pk/View_User_Application_Trademark_07",
        "sheet_name": "TM-07",
        "description": "On notice of intention to attend hearing under any of sections 28, 37, 73, 80, 96 and 97 by each party to the proceeding concerned",
        "fee": 600,
        "duplicate_column": 2  # Trademark Application No.
    },
    "TM-11": {
        "url": "https://apply.ipo.gov.pk/View_User_Application_Trademark_11",
        "sheet_name": "TM-11",
        "description": "For one registration of a trademark not otherwise charged, in respect of an application for a specification of goods or services including series of trademarks, collective mark, certification mark and textile mark, including in one class",
        "fee": 9000,
        "duplicate_column": 2  # Trademark Application No.
    },
    "TM-12": {
        "url": "https://apply.ipo.gov.pk/View_User_Application_Trademark_12",
        "sheet_name": "TM-12",
        "description": "For renewal under section 35 of the registration of a trademark at the expiration of the last registration, not otherwise charge including renewal of series of trademarks, collective mark, certification marks and textile mark. Additional fee under rule 52(1) for late payment of renewal",
        "fee": "15000 + 900 (late fee)",
        "duplicate_column": 2  # Trademark Application No.
    },
    "TM-13": {
        "url": "https://apply.ipo.gov.pk/View_User_Application_Trademark_13",
        "sheet_name": "TM-13",
        "description": "On request for restoration under section 35(6) of a trade mark removed from the register",
        "fee": 3000,
        "duplicate_column": 2  # Trademark Application No.
    },
    "TM-15": {
        "url": "https://apply.ipo.gov.pk/View_User_Application_Trademark_15",
        "sheet_name": "TM-15",
        "description": "On a request under section 27(6) to state grounds of decision",
        "fee": 1500,
        "duplicate_column": 2  # Trademark Application No.
    },
    "TM-16": {
        "url": "https://apply.ipo.gov.pk/View_User_Application_Trademark_16",
        "sheet_name": "TM-16",
        "description": "On request not otherwise charged, for correction of clerical error or for permission to amend application. Section 27(7)",
        "fee": 600,
        "duplicate_column": 2  # Trademark Application No.
    },
    "TM-24": {
        "url": "https://apply.ipo.gov.pk/View_User_Application_Trademark_24",
        "sheet_name": "TM-24",
        "description": "On the application under section 70(2)(a) to register a subsequent proprietor of more than one trade mark registered in the same name, the devolution of title being the same in each case",
        "fee": "6000/1500 (first/additional) or 7500/1500 (after 6 months)",
        "duplicate_column": 2  # Trademark Application No.
    },
    "TM-33": {
        "url": "https://apply.ipo.gov.pk/View_User_Application_Trademark_33",
        "sheet_name": "TM-33",
        "description": "On application under section 96(4) to change the name or description of a proprietor or registered user where there has been no change in the proprietorship or in the identity of the registered licensee",
        "fee": "1500/300 (first/additional)",
        "duplicate_column": 2  # Trademark Application No.
    },
    "TM-34": {
        "url": "https://apply.ipo.gov.pk/View_User_Application_Trademark_34",
        "sheet_name": "TM-34",
        "description": "On application under section 96(4) to alter one or more entries of the trade or business address of a registered proprietor or a registered licensee of a trade mark where the address in each case is the same and is altered in the same way",
        "fee": "600/150 (first/additional)",
        "duplicate_column": 2  # Trademark Application No.
    },
    "TM-46": {
        "url": "https://apply.ipo.gov.pk/View_User_Application_Trademark_46",
        "sheet_name": "TM-46",
        "description": "On request for certificate of the Registrar under any of section 11 and 12(2) other than certificate under section 33(1)",
        "fee": 1500,
        "duplicate_column": 2  # Trademark Application No.
    },
    "TM-55": {
        "url": "https://apply.ipo.gov.pk/View_User_Application_Trademark_55",
        "sheet_name": "TM-55",
        "description": "Request for search under rule 87 In respect of each class",
        "fee": 1000,
        "duplicate_column": 2  # Trademark Application No.
    },
    "TM-56": {
        "url": "https://apply.ipo.gov.pk/View_User_Application_Trademark_56",
        "sheet_name": "TM-56",
        "description": "On application for extension of time under any of the rule 80",
        "fee": 1500,
        "duplicate_column": 2  # Trademark Application No.
    },
    "TM-57": {
        "url": "https://apply.ipo.gov.pk/View_User_Application_Trademark_57",
        "sheet_name": "TM-57",
        "description": "On application for restoration of a trademark abandoned for non-compliance of the requirement of the registry [See section 33(5) and 26(3)]",
        "fee": 1500,
        "duplicate_column": 2  # Trademark Application No.
    }
}

# Current selected TM form (default to TM-05 for backward compatibility)
TARGET_URL = TM_FORMS["TM-05"]["url"]
SHEET_NAME = TM_FORMS["TM-05"]["sheet_name"]
DUPLICATE_KEY_COLUMN = TM_FORMS["TM-05"]["duplicate_column"]

# Browser settings
HEADLESS = False  # Set to True for headless mode
TIMEOUT = 30000  # 30 seconds in milliseconds

# Cookie persistence
COOKIES_FILE = "cookies.json"
