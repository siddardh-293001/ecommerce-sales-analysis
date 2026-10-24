import pandas as pd
from src.exports import sales_csv_file

def test_csv_preserves_filtered_rows(cleaned):
    data=cleaned[0].loc[cleaned[0].Country.eq('FR')]
    with sales_csv_file(data) as handle:
        exported=pd.read_csv(handle)
    assert len(exported)==len(data)
    assert exported.Country.eq('FR').all()
    assert exported.Revenue.sum()==data.Revenue.sum()
