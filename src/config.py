"""Project paths and explicit analytical choices."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "Online Retail.xlsx"
CACHE_PATH = ROOT / "data" / "processed" / "online_retail_raw.csv"
OUTPUT_PATH = ROOT / "outputs"
REQUIRED_COLUMNS = ["InvoiceNo", "StockCode", "Description", "Quantity", "InvoiceDate", "UnitPrice", "CustomerID", "Country"]
NON_PRODUCT_CODES = {"POST", "D", "M", "DOT", "BANK CHARGES", "CRUISE", "AMAZONFEE", "B", "S", "ADJUST", "ADJUST2", "C2", "PADS", "GIFT_0001_10", "GIFT_0001_20", "GIFT_0001_30", "GIFT_0001_40", "GIFT_0001_50"}
# Positive-priced non-product lines contribute to gross sales, never product rankings.
INCLUDE_NON_PRODUCTS_IN_REVENUE = True
TOP_N = 10
HOME_COUNTRY = "United Kingdom"
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
