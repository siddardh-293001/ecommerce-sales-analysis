"""Build compact, versioned dashboard inputs with the shared cleaning pipeline."""
import json
from src.config import ROOT
from src.data_loader import load_data
from src.data_cleaning import clean_data
from src.prepared_data import PREPARED_VERSION

def prepare_dashboard():
    """Prepare Parquet artifacts during hosting builds, never on browser requests."""
    sales, quality, report = clean_data(load_data())
    folder = ROOT / 'data' / 'processed' / 'dashboard'
    folder.mkdir(parents=True, exist_ok=True)
    for name, frame in [('sales',sales),('quality',quality)]:
        for column in ['InvoiceNo','StockCode','Description','CustomerID','Country','YearMonth','ExclusionReason']:
            frame[column] = frame[column].astype('category')
        frame.to_parquet(folder / f'{name}.parquet', engine='pyarrow', index=False)
    (folder/'report.json').write_text(json.dumps(report, default=lambda value: value.item()))
    (folder/'version.txt').write_text(PREPARED_VERSION)
    print(f'Dashboard inputs prepared: {folder}')
if __name__ == '__main__':
    prepare_dashboard()
