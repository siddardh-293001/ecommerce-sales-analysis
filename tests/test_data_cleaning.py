import pandas as pd
import pytest
from src.data_cleaning import clean_data

def test_reconciliation(cleaned):
    sales,quality,report=cleaned
    assert report['original_rows']==9 and report['duplicates_removed']==1
    assert len(sales)==5 and len(quality)==3
    assert sales.Revenue.sum()==34
    assert not sales.loc[sales.StockCode.eq('POST'),'IsProduct'].any()
    assert quality.IsCancellation.sum()==1
    assert sales.CustomerID.isna().sum()==1
    assert sales.loc[sales.StockCode.eq('A'),'Description'].eq('Apple').all()

def test_near_duplicate_kept(raw):
    extra=raw.iloc[[0]].copy(); extra['Quantity']=4
    sales,_,r=clean_data(pd.concat([raw,extra],ignore_index=True))
    assert len(sales)==6 and r['duplicates_removed']==1

@pytest.mark.parametrize('column,value',[('Quantity',-1),('Quantity','bad'),('UnitPrice',-2),('UnitPrice','bad'),('InvoiceDate','bad')])
def test_invalid(raw,column,value):
    frame=raw.iloc[[0]].copy(); frame[column]=frame[column].astype(object); frame.loc[frame.index[0],column]=value
    sales,quality,r=clean_data(frame)
    assert sales.empty and len(quality)==1
