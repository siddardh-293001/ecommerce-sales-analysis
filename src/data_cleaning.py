"""Preserve raw rows and separate positive sales from returns and quality records."""
import pandas as pd
from .config import DAYS, NON_PRODUCT_CODES
from .data_loader import validate_columns

def inspect_data(raw: pd.DataFrame) -> dict:
    """Describe the raw schema and quality without mutating it."""
    validate_columns(raw)
    quantity = pd.to_numeric(raw.Quantity, errors="coerce")
    price = pd.to_numeric(raw.UnitPrice, errors="coerce")
    dates = pd.to_datetime(raw.InvoiceDate, errors="coerce")
    return {"rows": len(raw), "columns": len(raw.columns), "dtypes": raw.dtypes.astype(str).to_dict(),
            "missing": raw.isna().sum().to_dict(), "duplicates": int(raw.duplicated().sum()),
            "unique_invoices": int(raw.InvoiceNo.nunique()), "unique_customers": int(raw.CustomerID.nunique()),
            "unique_products": int(raw.StockCode.nunique()), "date_min": str(dates.min()), "date_max": str(dates.max()),
            "negative_quantities": int(quantity.lt(0).sum()), "zero_quantities": int(quantity.eq(0).sum()),
            "zero_prices": int(price.eq(0).sum()), "negative_prices": int(price.lt(0).sum()),
            "unit_price_distribution": price.describe().to_dict()}

def clean_data(raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Return positive sales, all excluded quality rows, and reconciled audit counts.

    Duplicate identity is evaluated on original columns before conversion. Exclusion
    reasons are mutually exclusive, in priority order, so counts reconcile exactly.
    """
    inspection = inspect_data(raw)
    frame = raw.drop_duplicates().copy()
    failures = {}
    for column in ["Quantity", "UnitPrice"]:
        converted = pd.to_numeric(frame[column], errors="coerce")
        failures[column] = int((frame[column].notna() & converted.isna()).sum())
        frame[column] = converted
    dates = pd.to_datetime(frame.InvoiceDate, errors="coerce")
    failures["InvoiceDate"] = int((frame.InvoiceDate.notna() & dates.isna()).sum())
    frame["InvoiceDate"] = dates
    for column in ["InvoiceNo", "StockCode", "CustomerID", "Country"]:
        frame[column] = frame[column].astype("string").str.strip().replace("", pd.NA)
    frame["CustomerID"] = frame.CustomerID.str.replace(r"\.0$", "", regex=True)
    frame["Description"] = frame.Description.astype("string").str.strip().replace("", pd.NA)
    labels = frame.dropna(subset=["StockCode", "Description"]).groupby("StockCode").Description.agg(lambda s: s.mode().sort_values().iloc[0])
    frame["Description"] = frame.StockCode.map(labels).fillna("Unknown")
    frame["IsCancellation"] = frame.InvoiceNo.str.upper().str.startswith("C", na=False)
    frame["IsProduct"] = frame.StockCode.notna() & ~frame.StockCode.str.upper().isin(NON_PRODUCT_CODES)
    reason = pd.Series("", index=frame.index)
    conditions = [
        ("cancellation", frame.IsCancellation),
        ("invalid_date", frame.InvoiceDate.isna()),
        ("missing_invoice", frame.InvoiceNo.isna()),
        ("invalid_quantity", frame.Quantity.isna()),
        ("nonpositive_quantity", frame.Quantity.le(0)),
        ("invalid_price", frame.UnitPrice.isna()),
        ("nonpositive_price", frame.UnitPrice.le(0)),
    ]
    for name, mask in conditions:
        reason.loc[reason.eq("") & mask] = name
    frame["ExclusionReason"] = reason
    frame["Revenue"] = frame.Quantity * frame.UnitPrice
    frame["Year"] = frame.InvoiceDate.dt.year
    frame["Month"] = frame.InvoiceDate.dt.month
    frame["YearMonth"] = frame.InvoiceDate.dt.to_period("M").astype("string")
    frame["DayOfWeek"] = pd.Categorical(frame.InvoiceDate.dt.day_name(), categories=DAYS, ordered=True)
    frame["Hour"] = frame.InvoiceDate.dt.hour
    frame["InvoiceDateOnly"] = frame.InvoiceDate.dt.normalize()
    sales = frame.loc[reason.eq("")].copy()
    quality = frame.loc[reason.ne("")].copy()
    total = sales.Revenue.sum()
    report = {"inspection": inspection, "original_rows": len(raw), "duplicates_removed": int(raw.duplicated().sum()),
              "excluded_by_reason": quality.ExclusionReason.value_counts().to_dict(), "excluded_rows": len(quality),
              "conversion_failures": failures, "final_rows": len(sales),
              "missing_customer_rows": int(sales.CustomerID.isna().sum()),
              "missing_customer_row_share_pct": float(sales.CustomerID.isna().mean()*100) if len(sales) else 0.,
              "missing_customer_revenue_share_pct": float(sales.loc[sales.CustomerID.isna(), "Revenue"].sum()/total*100) if total else 0.,
              "observed_non_product_codes": sorted(frame.loc[~frame.IsProduct, "StockCode"].dropna().unique().tolist()),
              "date_min": str(sales.InvoiceDate.min()), "date_max": str(sales.InvoiceDate.max())}
    assert report["original_rows"] - report["duplicates_removed"] - report["excluded_rows"] == len(sales)
    return sales, quality, report
