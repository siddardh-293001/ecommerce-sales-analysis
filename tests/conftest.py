"""Small hand-calculated transactions; never used in delivered analyses."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pandas as pd
import pytest
from src.data_cleaning import clean_data
@pytest.fixture
def raw():
    rows=[("1","A","Apple",2,"2020-01-01",5,"10","UK"),("1","BB","Berry",1,"2020-01-01",2,"10","UK"),("2","A",None,3,"2020-02-01",5,"10","UK"),("3","BB","Berry",2,"2020-02-29",2,"20","FR"),("4","POST","Postage",1,"2020-02-29",3,None,"UK"),("C1","A","Apple",-1,"2020-02-01",5,"10","UK"),("5","A","Apple",0,"2020-02-01",5,"10","UK"),("6","A","Apple",1,"2020-02-01",0,"10","UK")]
    frame=pd.DataFrame(rows,columns=["InvoiceNo","StockCode","Description","Quantity","InvoiceDate","UnitPrice","CustomerID","Country"])
    return pd.concat([frame,frame.iloc[[0]]],ignore_index=True)
@pytest.fixture
def cleaned(raw): return clean_data(raw)
