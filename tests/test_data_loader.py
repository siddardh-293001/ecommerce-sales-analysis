import pandas as pd
import pytest
from src.data_loader import load_data

def test_missing(tmp_path):
    with pytest.raises(FileNotFoundError,match='Dataset not found'): load_data(tmp_path/'no.xlsx',tmp_path/'cache.csv')
def test_corrupt(tmp_path):
    path=tmp_path/'bad.xlsx'; path.write_text('broken')
    with pytest.raises(ValueError,match='Unreadable Excel'): load_data(path,tmp_path/'cache.csv')
def test_schema(tmp_path):
    path=tmp_path/'bad.xlsx'; pd.DataFrame({'x':[1]}).to_excel(path,index=False)
    with pytest.raises(ValueError,match='missing required columns'): load_data(path,tmp_path/'cache.csv')
def test_cache(tmp_path,raw):
    path=tmp_path/'data.xlsx'; raw.to_excel(path,index=False); cache=tmp_path/'cache.csv'
    first=load_data(path,cache); second=load_data(path,cache)
    assert len(first)==len(second)==9 and cache.exists()
