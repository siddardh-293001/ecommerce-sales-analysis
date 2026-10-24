"""Load build-time dashboard artifacts, or use the normal local pipeline."""
import json
import pandas as pd
from .config import ROOT
from .data_loader import load_data
from .data_cleaning import clean_data
PREPARED_VERSION = '1'

def load_dashboard_data():
    """Read compact shared-pipeline outputs if available, preserving metric inputs."""
    folder = ROOT / 'data' / 'processed' / 'dashboard'
    if (folder/'version.txt').is_file() and (folder/'version.txt').read_text() == PREPARED_VERSION:
        sales = pd.read_parquet(folder/'sales.parquet')
        quality = pd.read_parquet(folder/'quality.parquet')
        # Identifiers stay string-like in public functions; low-cardinality labels remain compact.
        for frame in [sales,quality]:
            for column in ['InvoiceNo','StockCode','CustomerID','YearMonth','ExclusionReason']:
                frame[column] = frame[column].astype('string')
            # Country categories must not produce unobserved country groups.
            frame['Country'] = frame.Country.astype('string')
        return sales, quality, json.loads((folder/'report.json').read_text())
    return clean_data(load_data())
