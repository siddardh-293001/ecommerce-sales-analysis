"""Validated Excel loading with a source-fingerprint CSV cache."""
import json
from zipfile import BadZipFile
from openpyxl.utils.exceptions import InvalidFileException
from pathlib import Path
import pandas as pd
from .config import DATA_PATH, CACHE_PATH, REQUIRED_COLUMNS

def validate_columns(frame: pd.DataFrame) -> None:
    """Reject incomplete schema with the exact missing column names."""
    missing = sorted(set(REQUIRED_COLUMNS) - set(frame.columns))
    if missing:
        raise ValueError(f"Dataset missing required columns: {', '.join(missing)}")

def load_data(path=DATA_PATH, cache_path=CACHE_PATH, force_reload=False) -> pd.DataFrame:
    """Load Excel, or a cache tied to its absolute path, size and modification time."""
    path, cache_path = Path(path), Path(cache_path)
    if not path.is_file():
        raise FileNotFoundError(f"Dataset not found: {path}. Run python download_data.py to fetch the official UCI workbook.")
    stat = path.stat()
    fingerprint = {"path": str(path.resolve()), "size": stat.st_size, "mtime_ns": stat.st_mtime_ns}
    metadata = cache_path.with_suffix(".json")
    if not force_reload and cache_path.exists() and metadata.exists():
        try:
            cached_fingerprint = json.loads(metadata.read_text())
            if cached_fingerprint == fingerprint:
                frame = pd.read_csv(cache_path, dtype={"InvoiceNo": "string", "StockCode": "string", "CustomerID": "string"})
                validate_columns(frame)
                return frame
        except (ValueError, OSError, pd.errors.ParserError) as error:
            raise ValueError(f"Unreadable cache {cache_path}; retry with --force-reload: {error}") from error
    try:
        frame = pd.read_excel(path, engine="openpyxl", dtype={"InvoiceNo": "string", "StockCode": "string", "CustomerID": "string"})
    except (OSError, ValueError, BadZipFile, InvalidFileException, KeyError) as error:
        # Third-party XLSX readers raise several format-specific exception types.
        raise ValueError(f"Unreadable Excel dataset {path}: {error}") from error
    validate_columns(frame)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(cache_path, index=False)
    metadata.write_text(json.dumps(fingerprint))
    return frame
