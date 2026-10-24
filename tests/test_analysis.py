import numpy as np
import pandas as pd
import pytest
from src import analysis as a
from src.data_loader import load_data
from src.data_cleaning import clean_data
from src.config import DATA_PATH

def test_known_metrics(cleaned):
    sales,quality,_=cleaned; k=a.kpis(sales)
    assert k['revenue']==34 and k['invoices']==4 and k['identified_customers']==2
    assert k['repeat_customer_pct']==50 and k['mean_customer_revenue']==15.5
    assert a.concentration(sales)['top5_products_pct']==pytest.approx(31/34*100)
    assert a.concentration(sales)['top10_customers_pct']==100
    assert a.returns_analysis(quality,sales)['cancellation_invoices']==1

def test_months(cleaned):
    table=a.monthly(cleaned[0]); assert table.index.tolist()==['2020-01','2020-02']
    assert table.Revenue.tolist()==[12,22] and not table.Partial.any()
    assert table.MoMPct.iloc[1]==pytest.approx(1000/12)

def test_growth():
    result=a.mom_growth(pd.Series([0,3,np.nan,4,8]))
    assert result.iloc[:4].isna().all() and result.iloc[4]==100

def test_rankings(cleaned):
    sales=cleaned[0]; assert a.products(sales).index.tolist()==['A','BB']
    assert a.products(sales,'Quantity').Quantity.tolist()==[5,3]
    tied=sales.copy(); tied.loc[tied.StockCode.eq('A'),'Revenue']=3
    assert a.products(tied).index.tolist()==['A','BB']

def test_dates(cleaned):
    sales=cleaned[0]
    assert len(a.filter_data(sales,'2020-02-29','2020-02-29'))==2
    with pytest.raises(ValueError,match='Start date'): a.filter_data(sales,'2021-01-01','2020-01-01')
    assert a.filter_data(sales,countries=['absent']).empty

def test_rfm(cleaned):
    table=a.rfm(cleaned[0]); assert table.loc['10','Frequency']==2
    assert table.loc['10','Recency']==29 and table.loc['20','Recency']==1
    assert table.loc['10','M']==5 and table.loc['20','M']==3
    assert a.segments(cleaned[0]).Customers.sum()==2

@pytest.mark.parametrize('name',['invoices','customers','products','countries','kpis','monthly','time_profiles','concentration','pareto','frequency','rfm','segments','statistics','filter_data'])
def test_empty(cleaned,name):
    getattr(a,name)(cleaned[0].iloc[:0])
def test_empty_returns(cleaned):
    a.returns_analysis(cleaned[1].iloc[:0],cleaned[0].iloc[:0])
@pytest.mark.skipif(not DATA_PATH.exists(),reason='real workbook not downloaded')
def test_real_data_reconciles():
    sales,quality,report=clean_data(load_data())
    assert report['original_rows']-report['duplicates_removed']-len(quality)==len(sales)
    assert (sales.Quantity>0).all() and (sales.UnitPrice>0).all() and not sales.IsCancellation.any()
