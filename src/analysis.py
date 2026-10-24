"""Shared metric definitions. All revenue is gross positive-sales value, in GBP."""
import math
import numpy as np
import pandas as pd
from .config import DAYS

def filter_data(data, start=None, end=None, countries=None, products=None, prices=None):
    """Apply inclusive calendar dates and optional sales filters; reject reversed dates."""
    if start is not None and end is not None and pd.Timestamp(start) > pd.Timestamp(end):
        raise ValueError("Start date must be on or before end date.")
    mask = pd.Series(True, index=data.index)
    if start is not None: mask &= data.InvoiceDate.ge(pd.Timestamp(start).normalize())
    if end is not None: mask &= data.InvoiceDate.lt(pd.Timestamp(end).normalize()+pd.Timedelta(days=1))
    if countries: mask &= data.Country.isin(countries)
    if products: mask &= data.StockCode.isin(products)
    if prices is not None: mask &= data.UnitPrice.between(*prices)
    return data.loc[mask].copy()

def invoices(data):
    """Aggregate distinct invoice totals, units and first timestamp."""
    return data.groupby("InvoiceNo",observed=True).agg(Revenue=("Revenue","sum"), Units=("Quantity","sum"), Date=("InvoiceDate","min"))

def customers(data):
    """Aggregate identified customers only; count distinct invoices."""
    return data.dropna(subset=["CustomerID"]).groupby("CustomerID",observed=True).agg(Revenue=("Revenue","sum"), Frequency=("InvoiceNo","nunique"), LastPurchase=("InvoiceDate","max")).sort_values(["Revenue"],ascending=False)

def products(data, by="Revenue"):
    """Rank merchandise codes with deterministic code-order tie breaking."""
    table=data.loc[data.IsProduct].groupby("StockCode",observed=True).agg(Description=("Description","first"),Revenue=("Revenue","sum"),Quantity=("Quantity","sum"))
    table=table.reset_index().sort_values([by,"StockCode"],ascending=[False,True]).set_index("StockCode")
    table["RevenueSharePct"]=table.Revenue/data.Revenue.sum()*100 if data.Revenue.sum() else 0.
    table["RevenueRank"]=table.Revenue.rank(method="min",ascending=False)
    table["QuantityRank"]=table.Quantity.rank(method="min",ascending=False)
    return table

def countries(data):
    """Country revenue, invoices, identified customers and invoice average."""
    table=data.groupby("Country",dropna=False,observed=True).agg(Revenue=("Revenue","sum"),Invoices=("InvoiceNo","nunique"),Customers=("CustomerID","nunique"))
    table["AverageInvoiceRevenue"]=table.Revenue/table.Invoices
    return table.sort_values("Revenue",ascending=False)

def kpis(data):
    """Compute sales and customer KPIs with separate identified denominators."""
    inv=invoices(data); cust=customers(data); revenue=float(data.Revenue.sum())
    return {"revenue":revenue,"units":float(data.Quantity.sum()),"invoices":len(inv),"identified_customers":len(cust),"products":int(data.loc[data.IsProduct,"StockCode"].nunique()),
    "mean_invoice_revenue":float(inv.Revenue.mean()) if len(inv) else 0.,"median_invoice_revenue":float(inv.Revenue.median()) if len(inv) else 0.,
    "mean_customer_revenue":float(cust.Revenue.mean()) if len(cust) else 0.,"median_customer_revenue":float(cust.Revenue.median()) if len(cust) else 0.,
    "repeat_customer_pct":float(cust.Frequency.gt(1).mean()*100) if len(cust) else 0.,
    "unidentified_revenue_pct":float(data.loc[data.CustomerID.isna(),"Revenue"].sum()/revenue*100) if revenue else 0.}

def mom_growth(values):
    """Percent change; undefined previous values or zero denominators yield NaN."""
    previous=values.shift(1)
    return (values-previous)/previous.where(previous.ne(0))*100

def monthly(data, window_start=None, window_end=None):
    """Calendar months including missing months; flag observation boundary months."""
    if data.empty: return pd.DataFrame(columns=["Revenue","Invoices","Partial","MoMPct","MoMPartial"])
    start=pd.Timestamp(window_start) if window_start is not None else data.InvoiceDate.min()
    end=pd.Timestamp(window_end) if window_end is not None else data.InvoiceDate.max()
    periods=pd.period_range(start,end,freq="M")
    table=data.groupby(data.InvoiceDate.dt.to_period("M")).agg(Revenue=("Revenue","sum"),Invoices=("InvoiceNo","nunique")).reindex(periods)
    table["Partial"]=[start.normalize()>m.start_time.normalize() or end.normalize()<m.end_time.normalize() for m in periods]
    table["MoMPct"]=mom_growth(table.Revenue)
    table["MoMPartial"]=table.Partial | table.Partial.shift(1,fill_value=False)
    table.index=table.index.astype(str); table.index.name="Month"
    return table

def time_profiles(data):
    """Observed daily revenue, ordered weekdays and hourly distinct invoices."""
    return {"daily":data.groupby("InvoiceDateOnly").Revenue.sum().to_frame(),
    "weekday":data.groupby("DayOfWeek",observed=False).Revenue.sum().reindex(DAYS).to_frame(),
    "hour":data.groupby("Hour").InvoiceNo.nunique().to_frame("Invoices")}

def concentration(data):
    """Product shares use all gross sales; customer shares use identified sales."""
    prod=products(data); cust=customers(data); gross=data.Revenue.sum(); identified=cust.Revenue.sum()
    return {"top5_products_pct":float(prod.Revenue.head(5).sum()/gross*100) if gross else 0.,"top10_products_pct":float(prod.Revenue.head(10).sum()/gross*100) if gross else 0.,
    "top10_customers_pct":float(cust.Revenue.head(10).sum()/identified*100) if identified else 0.,
    "top20pct_customers_pct":float(cust.Revenue.head(math.ceil(len(cust)*.2)).sum()/identified*100) if identified else 0.}

def pareto(data):
    """Product cumulative revenue share with gross-sales denominator."""
    table=products(data)[["Revenue"]].reset_index()
    table["Rank"]=np.arange(1,len(table)+1)
    table["CumulativePct"]=table.Revenue.cumsum()/data.Revenue.sum()*100 if data.Revenue.sum() else 0.
    return table

def frequency(data):
    """Number of identified customers at each distinct-invoice purchase count."""
    return customers(data).Frequency.value_counts().sort_index().rename_axis("Invoices").to_frame("Customers")

def returns_analysis(quality, sales):
    """Separate cancellation value magnitude from refund/return rates."""
    cancelled=quality.loc[quality.IsCancellation]
    trend=cancelled.groupby("YearMonth",observed=True).InvoiceNo.nunique().to_frame("CancellationInvoices")
    ranking=cancelled.loc[cancelled.IsProduct].groupby("StockCode",observed=True).agg(Lines=("InvoiceNo","size"),Invoices=("InvoiceNo","nunique")).sort_values("Lines",ascending=False)
    return {"cancellation_invoices":int(cancelled.InvoiceNo.nunique()),"negative_quantity_records":int(quality.Quantity.lt(0).sum()),
    "cancelled_value_relative_to_gross_pct":float(cancelled.Revenue.abs().sum()/sales.Revenue.sum()*100) if sales.Revenue.sum() else 0.,"trend":trend,"products":ranking}

def rfm(data, reference_date=None):
    """Quintiles via average percentile ranks: ties stay together, bins may be empty."""
    table=customers(data).copy()
    if table.empty:
        for column in ["Recency","R","F","M"]: table[column]=pd.Series(index=table.index,dtype="int64")
        table["Segment"]=pd.Series(index=table.index,dtype="str")
        return table
    reference=pd.Timestamp(reference_date) if reference_date is not None else data.InvoiceDate.max().normalize()+pd.Timedelta(days=1)
    table["Recency"]=(reference-table.LastPurchase.dt.normalize()).dt.days
    for column,score,ascending in [("Recency","R",False),("Frequency","F",True),("Revenue","M",True)]:
        table[score]=np.ceil(table[column].rank(method="average",pct=True,ascending=ascending)*5).clip(1,5).astype(int)
    table["Segment"]=np.select([table.R.ge(4)&table.F.ge(4)&table.M.ge(4),table.R.le(2)&table.F.ge(3),table.R.eq(1),table.F.ge(3),table.R.ge(4)&table.F.le(2)], ["Champions","At Risk","Lost","Loyal","New"],default="Developing")
    return table

def segments(data):
    """Customer count and identified-revenue contribution by RFM segment."""
    table=rfm(data).groupby("Segment",observed=True).agg(Customers=("Revenue","size"),Revenue=("Revenue","sum"))
    table["RevenueSharePct"]=table.Revenue/table.Revenue.sum()*100 if table.Revenue.sum() else 0.
    return table

def statistics(data):
    """IQR flags, Spearman correlation, and exploratory observed-day comparison."""
    from scipy.stats import mannwhitneyu
    inv=invoices(data); result={}
    for column in ["Revenue","Units"]:
        q1,q3=inv[column].quantile([.25,.75]); mask=(inv[column]<q1-1.5*(q3-q1))|(inv[column]>q3+1.5*(q3-q1))
        result[column+"_outliers"]=int(mask.sum())
        result[column+"_outlier_revenue_pct"]=float(inv.loc[mask,"Revenue"].sum()/inv.Revenue.sum()*100) if inv.Revenue.sum() else None
    result["units_revenue_spearman"]=float(inv.Units.corr(inv.Revenue,method="spearman")) if len(inv)>2 else None
    daily=time_profiles(data)["daily"]
    weekday=daily.loc[daily.index.day_of_week<5,"Revenue"]; weekend=daily.loc[daily.index.day_of_week>=5,"Revenue"]
    if len(weekday) and len(weekend):
        test=mannwhitneyu(weekday,weekend,alternative="two-sided")
        result.update({"mann_whitney_p":float(test.pvalue),"rank_biserial_weekday_minus_weekend":float(2*test.statistic/(len(weekday)*len(weekend))-1),"weekday_median":float(weekday.median()),"weekend_median":float(weekend.median()),"weekday_days":len(weekday),"weekend_days":len(weekend)})
    return result
