"""Check hosting artifacts preserve real-data metrics and cleaning reports."""
import pytest
from src.config import ROOT
from src.data_loader import load_data
from src.data_cleaning import clean_data
from src.prepared_data import load_dashboard_data
from src.analysis import kpis, returns_analysis
@pytest.mark.skipif(not (ROOT/'data/processed/dashboard/version.txt').exists(),reason='prepared data not built')
def test_prepared_matches_shared_pipeline():
    sales,quality,report=clean_data(load_data())
    prepared,prepared_quality,prepared_report=load_dashboard_data()
    assert kpis(prepared)==kpis(sales)
    assert report==prepared_report
    assert returns_analysis(prepared_quality,prepared)['cancellation_invoices']==returns_analysis(quality,sales)['cancellation_invoices']
