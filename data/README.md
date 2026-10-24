# Official UCI Online Retail workbook
Run `python download_data.py` from the project folder. This downloads the official public ZIP and extracts only `data/Online Retail.xlsx`. The dashboard never calls external APIs. The raw workbook is never edited. A SHA-256 provenance record is saved alongside it. Cache: `processed/online_retail_raw.csv`; bypass with `python run_analysis.py --force-reload`.

Manual fallback: download https://archive.ics.uci.edu/dataset/352/online+retail and place `Online Retail.xlsx` here.

Credit: Daqing Chen (2015), Online Retail, UCI Machine Learning Repository, DOI https://doi.org/10.24432/C5BW33, CC BY 4.0. Currency: GBP. One UK-based non-store retailer, historical observations.
