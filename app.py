"""Streamlit presentation; calculations are shared with the CLI and notebook."""
import pandas as pd
import streamlit as st
from src.prepared_data import load_dashboard_data
from src.config import HOME_COUNTRY, ROOT
from src import analysis as a, visualizations as v, theme
st.set_page_config(page_title="E-Commerce Sales Intelligence",layout="wide")
st.markdown(f"""<style>[data-testid='stMetric'] {{background:{theme.SURFACE};border:1px solid {theme.GRID};border-radius:10px;padding:14px;}} [data-testid='stMetricLabel'] {{color:{theme.TEXT_MUTED};}} [data-testid='stMetricValue'] {{color:{theme.TEXT};font-size:1.4rem;}}</style>""",unsafe_allow_html=True)
st.title("E-Commerce Sales Intelligence Dashboard")
st.caption("Explore historical sales performance, product trends, and customer purchasing behavior.")
@st.cache_data
def prepare():
    """Cache acquisition from the local workbook and shared cleaning pipeline."""
    return load_dashboard_data()
try:
    sales,quality,report=prepare()
except (FileNotFoundError,ValueError) as error:
    st.error(str(error)); st.info("Run python download_data.py, then refresh."); st.stop()
def reset():
    for key in ["start","end","countries","products","prices"]: st.session_state.pop(key,None)
with st.sidebar:
    st.header("Explore sales")
    st.button("Reset filters",on_click=reset)
    start=st.date_input("Start date",sales.InvoiceDate.min().date(),key="start")
    end=st.date_input("End date",sales.InvoiceDate.max().date(),key="end")
    countries=st.multiselect("Country",sorted(sales.Country.dropna().unique()),key="countries")
    products=st.multiselect("Product (search StockCode)",sorted(sales.StockCode.dropna().unique()),key="products")
    prices=st.slider("Unit price (GBP)",float(sales.UnitPrice.min()),float(sales.UnitPrice.max()),(float(sales.UnitPrice.min()),float(sales.UnitPrice.max())),key="prices")
try:
    filtered=a.filter_data(sales,start,end,countries,products,prices)
    # Returns/quality get the date filter only, explicitly labeled below.
    selected_quality=a.filter_data(quality,start,end)
except ValueError as error:
    st.warning(str(error)); st.stop()
with st.expander("Metric definitions and filter semantics"):
    st.markdown("Dates apply to every analytical result. Country, product and price apply to all sales metrics. Customer behavior is measured only within the filtered data and date window; outside purchases are invisible. Returns and data-quality views use dates only. The source cleaning audit is labeled separately as full-source metadata. Missing days are absent observations, not proven zero demand. Partial months are hatched; MoM involving them is flagged. This is historical data.")
    st.markdown((ROOT/"docs/metric_definitions.md").read_text())
if filtered.empty:
    st.info("No positive sales match these filters. Reset or broaden your selection."); st.stop()
k=a.kpis(filtered)
st.subheader("Filtered sales")
cols=st.columns(3)+st.columns(2)
for col,label,key in zip(cols,["Gross Revenue (GBP)","Total Units Sold","Unique Invoices","Identified Customers","Average Revenue per Invoice"],["revenue","units","invoices","identified_customers","mean_invoice_revenue"]):
    col.metric(label,f"{k[key]:,.2f}" if key in ["revenue","mean_invoice_revenue"] else f"{k[key]:,.0f}")
st.caption(f"Unidentified revenue: {k['unidentified_revenue_pct']:.2f}%. Customer behavior outside these filters is not visible.")
st.download_button("Download filtered sales CSV",filtered.to_csv(index=False).encode(),"filtered_sales.csv","text/csv")
def show(table,value,title,**kwargs):
    st.plotly_chart(v.interactive(table,value,title,**kwargs),width="stretch")
tabs=st.tabs(["Sales Overview","Product Performance","Customer Insights","Geographic Insights","Returns and Data Quality"])
with tabs[0]:
    monthly=a.monthly(filtered,max(sales.InvoiceDate.min(),pd.Timestamp(start)),min(sales.InvoiceDate.max(),pd.Timestamp(end)+pd.Timedelta(days=1)-pd.Timedelta(microseconds=1)))
    show(monthly,"Revenue","Filtered monthly revenue (hatched = partial)"); show(monthly,"Invoices","Filtered monthly invoices")
    st.dataframe(monthly); profiles=a.time_profiles(filtered)
    for name,value in [("daily","Revenue"),("weekday","Revenue"),("hour","Invoices")]: show(profiles[name],value,f"Filtered {name} sales activity")
with tabs[1]:
    for by in ["Revenue","Quantity"]:
        table=a.products(filtered,by); show(table.head(10),by,f"Filtered top products by {by}",horizontal=True); st.dataframe(table.head(10))
    show(a.pareto(filtered).set_index("Rank"),"CumulativePct","Filtered product revenue concentration",kind="line"); st.json(a.concentration(filtered))
with tabs[2]:
    st.metric("Filtered repeat-customer rate",f"{k['repeat_customer_pct']:.2f}%")
    cust=a.customers(filtered)
    st.dataframe(cust.head(10)); st.dataframe(cust.sort_values("Frequency",ascending=False).head(10))
    show(a.frequency(filtered),"Customers","Filtered purchase frequency")
    show(a.segments(filtered),"Customers","Filtered RFM segment size"); show(a.segments(filtered),"Revenue","Filtered RFM revenue")
with tabs[3]:
    geo=a.countries(filtered); show(geo.head(10),"Revenue","Filtered country revenue",horizontal=True)
    show(geo.drop(index=HOME_COUNTRY,errors="ignore").head(10),"Revenue","Filtered revenue outside the UK",horizontal=True)
    show(geo.head(10),"Invoices","Filtered country invoices",horizontal=True); st.dataframe(geo)
    st.caption("Customer counts exclude missing CustomerIDs.")
with tabs[4]:
    ret=a.returns_analysis(selected_quality,a.filter_data(sales,start,end))
    show(ret["trend"],"CancellationInvoices","Date-window cancellations (all countries/products/prices)",cancellation=True)
    st.json({key:value for key,value in ret.items() if key not in ["trend","products"]}); st.dataframe(ret["products"].head(10))
    st.dataframe(selected_quality.ExclusionReason.value_counts().to_frame("Date-window excluded rows"))
    with st.expander("Full-source cleaning audit (metadata, not filtered metrics)"): st.json(report)
    st.warning("Cancelled value relative to gross sales is not a return rate. Original purchases cannot reliably be matched. No cost data: revenue is not profit.")
