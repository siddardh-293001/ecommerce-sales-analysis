"""Run the complete real-data pipeline and optionally export figures."""
import argparse
import json
import math
from pathlib import Path
import pandas as pd
import matplotlib
if __name__ == "__main__":
    matplotlib.use("Agg")
import matplotlib.pyplot as plt
from src.config import OUTPUT_PATH, HOME_COUNTRY
from src.data_loader import load_data
from src.data_cleaning import clean_data
from src import analysis as a, visualizations as v, theme

def findings(sales,quality,report):
    """Build evidence-linked recommendations from computed metrics."""
    k=a.kpis(sales); c=a.concentration(sales); m=a.monthly(sales); complete=m.loc[~m.Partial].dropna(subset=["Revenue"])
    prod=a.products(sales); country=a.countries(sales); cust=a.customers(sales); ret=a.returns_analysis(quality,sales); seg=a.segments(sales)
    volume=a.products(sales,"Quantity"); mismatch=volume.assign(Gap=volume.RevenueRank-volume.QuantityRank).sort_values("Gap",ascending=False)
    facts=[
    ("Sales scale",f"Gross positive-sales revenue is £{k['revenue']:,.2f} across {k['invoices']:,} invoices.","This measures positive sales activity.","Use this baseline to monitor sales value.","No costs or matched refunds; this is not profit or net revenue."),
    ("Product leaders",f"{prod.index[0]} ({prod.iloc[0].Description}) leads merchandise revenue at £{prod.iloc[0].Revenue:,.2f}.","Sales value is uneven across merchandise.","Investigate stock availability for leading products.","Revenue does not establish margin or future demand."),
    ("Volume versus value",f"{mismatch.index[0]} has quantity rank {mismatch.iloc[0].QuantityRank:g} and revenue rank {mismatch.iloc[0].RevenueRank:g}.","High unit volume can differ from revenue contribution.","Investigate pricing and fulfillment workload.","Unit price and pack conventions can differ."),
    ("Complete-month peak",f"{complete.Revenue.idxmax()} has the highest complete-month revenue (£{complete.Revenue.max():,.2f}); {complete.Revenue.idxmin()} the lowest (£{complete.Revenue.min():,.2f}).","Activity varies within the historical window.","Test inventory planning around observed peaks.","Boundary partial months are excluded; this is not a current forecast."),
    ("Geography",f"{country.index[0]} contributes {country.iloc[0].Revenue/k['revenue']*100:.2f}% of gross sales.","The retailer depends heavily on its leading market.","Investigate smaller markets separately.","One UK retailer; missing IDs affect customer counts."),
    ("Repeat purchasing",f"{k['repeat_customer_pct']:.2f}% of identified customers purchased on multiple distinct invoices; customer {cust.sort_values('Frequency',ascending=False).index[0]} has {cust.Frequency.max():,} invoices.","Repeat activity is observable within this window.","Test retention outreach for established customers.","Purchases outside this window and unidentified customers are invisible."),
    ("Concentration",f"Top 10 products account for {c['top10_products_pct']:.2f}% of gross sales; top 20% of identified customers account for {c['top20pct_customers_pct']:.2f}% of identified revenue.","Customer dependence deserves monitoring.","Investigate service needs of major accounts.","Product and customer percentages use different denominators."),
    ("Segments",f"{seg.Revenue.idxmax()} is the largest revenue segment (£{seg.Revenue.max():,.2f}).","RFM describes historical customer behavior.","Test differentiated service by segment.","Heuristic quantile scores are not validated predictions."),
    ("Cancellations",f"{ret['cancellation_invoices']:,} cancellation invoices; cancelled value relative to gross sales is {ret['cancelled_value_relative_to_gross_pct']:.2f}%.","Cancellations warrant operational investigation.","Investigate cancellation product patterns and source records.","Cannot reliably match original sales or infer definitive refund rates."),
    ("Identity coverage",f"{report['missing_customer_revenue_share_pct']:.2f}% of sales revenue has no CustomerID.","Customer analysis covers a subset of sales.","Investigate identity capture quality.","Missing identifiers cannot be imputed reliably.")]
    return "\n\n".join(f"### {title}\nObservation → Supporting metric: {metric}\n\nBusiness interpretation: {meaning} Suggested action: {action} Limitation/uncertainty: {limit}" for title,metric,meaning,action,limit in facts)

def chart_specs(sales,quality,report):
    """Prepare all required static chart inputs outside visualization functions."""
    profiles=a.time_profiles(sales); geo=a.countries(sales); ret=a.returns_analysis(quality,sales)
    return [
    ("monthly",a.monthly(sales),"Revenue","How does monthly gross revenue vary? (hatched = partial)","bar",False,False),
    ("daily",profiles["daily"],"Revenue","How does revenue vary across observed trading dates?","line",False,False),
    ("products_revenue",a.products(sales).head(10),"Revenue","Which products lead revenue?","bar",True,False),
    ("products_quantity",a.products(sales,"Quantity").head(10),"Quantity","Which products lead unit sales?","bar",True,False),
    ("countries",geo.head(10),"Revenue","Which countries contribute sales?","bar",True,False),
    ("countries_ex_home",geo.drop(index=HOME_COUNTRY,errors="ignore").head(10),"Revenue","Which markets lead outside the UK?","bar",True,False),
    ("frequency",a.frequency(sales),"Customers","How many distinct invoices do customers place?","bar",False,False),
    ("weekday",profiles["weekday"],"Revenue","How does revenue vary by weekday?","bar",False,False),
    ("hour",profiles["hour"],"Invoices","When are sales invoices created?","bar",False,False),
    ("pareto",a.pareto(sales).set_index("Rank"),"CumulativePct","How concentrated is product revenue?","line",False,False),
    ("cancellations",ret["trend"],"CancellationInvoices","How do cancellation counts vary by month?","bar",False,True),
    ("quality",pd.Series({"duplicates":report["duplicates_removed"],**report["excluded_by_reason"]}).to_frame("Rows"),"Rows","Which reasons exclude rows?","bar",True,False),
    ("missing",pd.Series(report["inspection"]["missing"]).to_frame("Rows"),"Rows","Which raw fields are missing?","bar",True,False),
    ("rfm_size",a.segments(sales),"Customers","How large are RFM segments?","bar",True,False),
    ("rfm_revenue",a.segments(sales),"Revenue","How much revenue comes from each segment?","bar",True,False)]

def serializable(value):
    """Convert NumPy values and undefined numbers into strict JSON values."""
    if isinstance(value,dict): return {str(k):serializable(v) for k,v in value.items()}
    if isinstance(value,list): return [serializable(v) for v in value]
    if hasattr(value,"item"): value=value.item()
    if isinstance(value,float) and not math.isfinite(value): return None
    return value

def run(force_reload=False,export_charts=False):
    """Write computed outputs and return the shared pipeline objects."""
    raw=load_data(force_reload=force_reload); sales,quality,report=clean_data(raw)
    OUTPUT_PATH.mkdir(exist_ok=True)
    summary={"kpis":a.kpis(sales),"concentration":a.concentration(sales),"statistics":a.statistics(sales),"cleaning":report,"returns":{k:v for k,v in a.returns_analysis(quality,sales).items() if k not in ["trend","products"]}}
    (OUTPUT_PATH/"summary.json").write_text(json.dumps(serializable(summary),indent=2,allow_nan=False))
    (OUTPUT_PATH/"key_findings.md").write_text(findings(sales,quality,report))
    tables={"monthly":a.monthly(sales),"products":a.products(sales),"countries":a.countries(sales),"customers":a.customers(sales),"rfm":a.rfm(sales),"segments":a.segments(sales),"cancellation_products":a.returns_analysis(quality,sales)["products"]}
    for name,table in tables.items(): table.to_csv(OUTPUT_PATH/f"{name}.csv")
    theme.apply_matplotlib_theme(); theme.write_streamlit_config(Path(__file__).parent/".streamlit/config.toml")
    if export_charts:
        for name,table,value,title,kind,horizontal,cancel in chart_specs(sales,quality,report):
            fig=v.chart(table,value,title,kind,horizontal,cancel); fig.savefig(OUTPUT_PATH/"charts"/f"{name}.png",dpi=140); plt.close(fig)
        for name,values,title in [("customer_spend",a.customers(sales).Revenue,"How is customer spending distributed?"),("line_revenue",sales.Revenue,"How is line revenue distributed?"),("quantity",sales.Quantity,"How are line quantities distributed?")]:
            fig=v.distribution(values,title,"Quantity (units, logarithmic)" if name=="quantity" else "Revenue (GBP, logarithmic)"); fig.savefig(OUTPUT_PATH/"charts"/f"{name}.png",dpi=140); plt.close(fig)
    print(json.dumps(summary["kpis"],indent=2)); print(f"Outputs: {OUTPUT_PATH}")
    return raw,sales,quality,report
if __name__=="__main__":
    parser=argparse.ArgumentParser(); parser.add_argument("--force-reload",action="store_true"); parser.add_argument("--export-charts",action="store_true"); args=parser.parse_args(); run(args.force_reload,args.export_charts)
