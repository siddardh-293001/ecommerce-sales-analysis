"""Download the official public UCI archive without scraping or credentials."""
import hashlib
import io
import json
import urllib.request
import zipfile
from src.config import DATA_PATH
URL = "https://archive.ics.uci.edu/static/public/352/online+retail.zip"
def download():
    """Save only the expected workbook and a provenance record."""
    if DATA_PATH.exists():
        print(f"Already present: {DATA_PATH}")
        return
    with urllib.request.urlopen(URL, timeout=120) as response:
        archive = response.read()
    with zipfile.ZipFile(io.BytesIO(archive)) as zipped:
        workbook = zipped.read("Online Retail.xlsx")
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary = DATA_PATH.with_suffix(".tmp")
    temporary.write_bytes(workbook)
    temporary.replace(DATA_PATH)
    DATA_PATH.with_suffix(".provenance.json").write_text(json.dumps({"url": URL, "sha256": hashlib.sha256(workbook).hexdigest()}, indent=2))
    print(f"Downloaded {DATA_PATH}")
if __name__ == "__main__":
    download()
