# E-Commerce Sales Analysis
## Sales Trends, Customer Behavior, and Product Performance

A reproducible portfolio project using UCI Online Retail. It investigates historical sales, repeat purchasing, merchandise contribution, geography and cancellations. Written for a learner with basic Python and Pandas knowledge. The CLI, executed notebook and dashboard share the same Python functions.

## Features
- Official dataset downloader with SHA-256 provenance; validated, fingerprinted Excel/CSV cache.
- Reconciled cleaning audit, distinct sales and quality views, identity coverage.
- Gross-sales KPIs, daily/monthly patterns, partial-month flags and MoM growth.
- Merchandise rankings, geographic comparisons, customer frequency and concentration.
- RFM segments, retained IQR outliers, Spearman correlation and exploratory Mann–Whitney comparison.
- Streamlit dashboard with date/country/product/price filters, reset, empty states and filtered CSV download.
- Saved notebook outputs, exported PNG figures, computed JSON/CSV findings and automated tests.

## Dataset
[UCI Online Retail](https://archive.ics.uci.edu/dataset/352/online+retail), Daqing Chen (2015), [DOI](https://doi.org/10.24432/C5BW33), CC BY 4.0. Currency is GBP. Data describes one UK-based non-store retailer; country plots include a view excluding the home market. Source schema: InvoiceNo (invoice/cancellation identifier), StockCode (product code), Description (label), Quantity (units), InvoiceDate (timestamp), UnitPrice (GBP per unit), CustomerID (optional identifier), Country (recorded customer country).

## Technologies
Python 3.10+ (3.11 recommended), Pandas, NumPy, Matplotlib, Seaborn, Streamlit, OpenPyXL, Plotly, SciPy, Pytest, Jupyter Notebook, nbconvert and ipykernel. Plotly is used only by the dashboard; notebook/export charts use Matplotlib/Seaborn.

## Installation (required for a new checkout)
macOS/Linux:
```bash
cd ecommerce-sales-analysis
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```
Windows PowerShell:
```powershell
cd ecommerce-sales-analysis
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```
The local project already has an installed `.venv` and the downloaded workbook.

## Dataset setup
```bash
python download_data.py
```
Exact workbook location: `data/Online Retail.xlsx`. The command downloads the official ZIP directly; no scraping, credentials or paid APIs. Existing workbooks are preserved. To replace a workbook intentionally, move it aside first. Manual fallback instructions and attribution are in `data/README.md`. No external API calls occur in the dashboard.

## Run the analysis
```bash
python run_analysis.py
```
Writes computed `outputs/summary.json`, `outputs/key_findings.md`, and analytical CSV tables. Optional PNG export:
```bash
python run_analysis.py --export-charts
```
Optional cache refresh:
```bash
python run_analysis.py --force-reload
```

## Run the notebook
```bash
python -m notebook notebooks/sales_analysis.ipynb
```
Choose the virtual environment Python kernel. To reproduce automated execution:
```bash
python -m ipykernel install --prefix .venv --name retail --display-name "Retail project Python"
python -m nbconvert --to notebook --execute --inplace notebooks/sales_analysis.ipynb --ExecutePreprocessor.kernel_name=retail --ExecutePreprocessor.timeout=600
```

## Run the dashboard
```bash
python -m streamlit run app.py
```
Open the local URL printed by Streamlit. Sidebar filters are searchable. No selection means all available countries/products. CSV downloads contain the currently filtered positive sales.

## Run tests
```bash
python -m pytest -v
```
Tests use hand-calculated fixtures only in the test suite. Real-workbook integration and Streamlit widget tests run when the workbook exists.

## Project structure
```text
ecommerce-sales-analysis/
├── app.py
├── download_data.py
├── run_analysis.py
├── requirements.txt
├── README.md
├── .gitignore
├── .streamlit/config.toml
├── data/
│   ├── Online Retail.xlsx        # downloaded, ignored by git
│   ├── Online Retail.provenance.json
│   ├── README.md
│   └── processed/                # fingerprinted cache, ignored
├── docs/metric_definitions.md
├── notebooks/sales_analysis.ipynb
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── theme.py
│   ├── data_loader.py
│   ├── data_cleaning.py
│   ├── analysis.py
│   └── visualizations.py
├── tests/
│   ├── conftest.py
│   ├── test_data_loader.py
│   ├── test_data_cleaning.py
│   ├── test_analysis.py
│   └── test_dashboard.py
└── outputs/
    ├── summary.json
    ├── key_findings.md
    ├── *.csv
    └── charts/*.png
```

## Design system
Monsoon Clay: warm paper and surface backgrounds; peepal green for revenue, terracotta for emphasis, indigo, turmeric, clay and sage for categories. Cancellation charts use the negative token; partial-month bars are muted and hatched. Tokens and colormaps live only in `src/theme.py`; `.streamlit/config.toml` is generated from them. All charts carry axis labels and titles. Continuous values use readable labels and markers; category labels and hatch patterns keep meaning visible in grayscale. Body and muted text contrast against backgrounds is checked programmatically. Formal color-blindness simulator review and narrow-screen visual review are listed in verification notes if not performed.

## Methodology
[Metric definitions](docs/metric_definitions.md) are the single source of truth. Preserve raw data. Remove exact duplicates across all source columns: identical repeated scans could sometimes be legitimate, so this is an assumption. Conversion failures are counted. Missing CustomerID rows contribute to sales, never customer analysis. Labels use each StockCode's most frequent known description, ties resolved alphabetically; otherwise Unknown.

Gross positive-sales revenue = Quantity × UnitPrice for non-cancellation rows with valid invoice/date and positive quantity/price. Non-product charges and adjustments with positive sales values remain in gross revenue but are excluded from merchandise rankings. The explicit code list is in `src/config.py`; actual observed codes are in `outputs/summary.json`. Cancellations and all other excluded rows remain in a separate quality view. Cleaning reasons are mutually exclusive so the audit reconciles.

Customer frequency counts distinct invoices. Customer spending and concentration denominators use only identified revenue. Quintile RFM scores preserve ties using average percentile ranks; bins can be empty. Segment rules and statistical assumptions are documented in the metric definitions.

Dates apply to every analytical result. Country/product/price filters apply to every sales metric, including customer metrics, within the chosen dates; behavior outside filters is invisible. Returns/quality use only dates and are labeled accordingly. The full-source audit is separately labeled provenance metadata. Reversed dates produce a message and empty filters produce a friendly state. Missing days/months are not automatically zero demand. Partial calendar months are flagged, MoM comparisons touching partial months are flagged, and highest/lowest-month findings exclude partial months.

## Key findings
### Sales scale
Observation → Supporting metric: Gross positive-sales revenue is £10,642,110.80 across 19,960 invoices.

Business interpretation: This measures positive sales activity. Suggested action: Use this baseline to monitor sales value. Limitation/uncertainty: No costs or matched refunds; this is not profit or net revenue.

### Product leaders
Observation → Supporting metric: 22423 (REGENCY CAKESTAND 3 TIER) leads merchandise revenue at £174,156.54.

Business interpretation: Sales value is uneven across merchandise. Suggested action: Investigate stock availability for leading products. Limitation/uncertainty: Revenue does not establish margin or future demand.

### Volume versus value
Observation → Supporting metric: 16045 has quantity rank 102 and revenue rank 2387.

Business interpretation: High unit volume can differ from revenue contribution. Suggested action: Investigate pricing and fulfillment workload. Limitation/uncertainty: Unit price and pack conventions can differ.

### Complete-month peak
Observation → Supporting metric: 2011-11 has the highest complete-month revenue (£1,503,866.78); 2011-02 the lowest (£522,545.56).

Business interpretation: Activity varies within the historical window. Suggested action: Test inventory planning around observed peaks. Limitation/uncertainty: Boundary partial months are excluded; this is not a current forecast.

### Geography
Observation → Supporting metric: United Kingdom contributes 84.59% of gross sales.

Business interpretation: The retailer depends heavily on its leading market. Suggested action: Investigate smaller markets separately. Limitation/uncertainty: One UK retailer; missing IDs affect customer counts.

### Repeat purchasing
Observation → Supporting metric: 65.58% of identified customers purchased on multiple distinct invoices; customer 12748 has 209 invoices.

Business interpretation: Repeat activity is observable within this window. Suggested action: Test retention outreach for established customers. Limitation/uncertainty: Purchases outside this window and unidentified customers are invisible.

### Concentration
Observation → Supporting metric: Top 10 products account for 9.09% of gross sales; top 20% of identified customers account for 74.68% of identified revenue.

Business interpretation: Customer dependence deserves monitoring. Suggested action: Investigate service needs of major accounts. Limitation/uncertainty: Product and customer percentages use different denominators.

### Segments
Observation → Supporting metric: Champions is the largest revenue segment (£5,676,143.38).

Business interpretation: RFM describes historical customer behavior. Suggested action: Test differentiated service by segment. Limitation/uncertainty: Heuristic quantile scores are not validated predictions.

### Cancellations
Observation → Supporting metric: 3,836 cancellation invoices; cancelled value relative to gross sales is 8.40%.

Business interpretation: Cancellations warrant operational investigation. Suggested action: Investigate cancellation product patterns and source records. Limitation/uncertainty: Cannot reliably match original sales or infer definitive refund rates.

### Identity coverage
Observation → Supporting metric: 16.49% of sales revenue has no CustomerID.

Business interpretation: Customer analysis covers a subset of sales. Suggested action: Investigate identity capture quality. Limitation/uncertainty: Missing identifiers cannot be imputed reliably.

## Limitations
Historical data cannot establish current trends. The earliest/latest day may itself be incomplete even when a month touches its first/last calendar day. Missing CustomerIDs limit behavioral analysis; their computed revenue share is reported above and alongside dashboard KPIs. No original-sale matching guarantees are available, so cancellation value relative to gross sales is not a refund or return rate. One UK-based retailer is not a representative sample of all e-commerce. Descriptions are imperfectly standardized. No costs, margins or profit data exist. Statistical comparisons are exploratory and can be confounded by seasonality and correlated daily activity. Outliers remain in analysis and may dominate some results.

## Future improvements (optional, not implemented)
Cohort retention, better original-sale/return matching, forecasting, geographic maps and richer statistical modeling. These stretch features are separate from the completed core and extended analyses.

## Verification
Verified on 2026-10-25 (Asia/Kolkata), using project-local Python 3.14.6. Resolved dependency versions are saved in `outputs/environment.txt`.

- Installed requirements into the initially empty project virtual environment. `python -m pip check`: No broken requirements found.
- Downloaded official UCI ZIP and extracted the original 23,715,344-byte workbook. Source URL and SHA-256 are in `data/Online Retail.provenance.json`. Repeat downloader invocation preserved the existing file.
- CLI completed with `--export-charts`: strict JSON summary, findings, seven analytical CSVs and 18 chart PNGs written. Monthly chart visually inspected; boundary partial month is hatched. Raw workbook preserved.
- Final `python -m pytest -v`: **35 passed in 38.08s**, no failures/skips. Includes real-workbook reconciliation, Streamlit launch within AppTest, country/product/price/date widgets, invalid dates, empty states, reset, download-button availability, and AA body-text contrast.
- Notebook executed in the project virtual environment: **21/21 code cells executed, zero error outputs, 16 embedded PNG figures**. Outputs saved in place.
- Streamlit server launched and rendered in the actual in-app browser at http://localhost:8501. KPI layout visually inspected at the browser's narrow viewport; values readable after adjustment. Download button clicked in the browser. Screenshot saved as `outputs/dashboard.png`.
- Filtered CSV serialization independently round-tripped using the real January 2011 France data with price <= GBP 10: **619 rows**, matching row count, country selection and revenue sum. Browser-downloaded bytes were not independently inspected.
- Python compilation check completed for app, downloader, CLI and all source modules.

Remaining review limits: no formal color-blindness simulator run; no exhaustive device/browser matrix. Charts use labels, markers and partial-month hatching to avoid color-only meaning. Stretch cohort retention and basket analysis are not implemented. Historical-data, missing-ID, unmatched-cancellation and no-cost caveats remain substantive analytical limitations, documented in the README and metric definitions.



## Public deployment
The source repository is https://github.com/siddardh-293001/ecommerce-sales-analysis.

Render build command: `bash build.sh`. Start command: `bash start.sh`.
The build downloads the official workbook and runs `prepare_dashboard.py`, which calls the same cleaning pipeline and writes compact Parquet inputs under ignored `data/processed/dashboard/`. These are build artifacts, not a second analytical implementation. PyArrow supplies Parquet storage. The dashboard uses these prepared inputs when available and falls back to the ordinary local pipeline otherwise. No dataset download occurs on browser requests.

Free Render instances can sleep while idle; allow time for the first request to wake the application. No database, credentials or paid instance is required.


Hosting memory optimization: prepared Parquet files retain categorical identifiers and load without parallel decompression. Statistical and static-plotting libraries import only when those features are called. CSV downloads are generated on demand through a temporary file in bounded chunks; Streamlit 1.66+ is required for deferred download callbacks. The shared calculations are unchanged. The publication check passed 37 tests, including prepared-data equivalence and filtered CSV serialization.
