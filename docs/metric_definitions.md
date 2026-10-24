# Metric definitions

All monetary values are GBP. The positive-sales view consists of deduplicated non-cancellation lines with valid dates/invoice IDs, Quantity > 0 and UnitPrice > 0. Non-product codes contribute to sales revenue but never merchandise rankings. Identified means CustomerID is present. All metrics use the supplied filtered frame unless stated otherwise.

| Metric | Formula / denominator / rows |
|---|---|
| Gross positive-sales revenue | Sum(Quantity × UnitPrice), positive sales only; never profit or net revenue |
| Units | Sum Quantity, including eligible non-product lines |
| Invoices | Distinct InvoiceNo, never line counts |
| Products | Distinct merchandise StockCode |
| Customers | Distinct non-missing CustomerID |
| Mean / median invoice revenue | Mean / median of distinct invoice line-revenue sums |
| Mean / median customer revenue | Mean / median of identified customer revenue sums; denominator excludes unidentified revenue |
| Unidentified revenue share | Sales revenue on missing-ID lines / all positive sales revenue × 100 |
| Missing-ID row share | Missing-ID positive-sales rows / all positive-sales rows × 100 |
| Repeat-customer rate | Identified customers with >1 distinct sales invoice / identified customers × 100; within selected window and filters |
| Purchase frequency | Distinct invoices per identified customer; distribution counts customers at each frequency |
| Daily revenue | Sum Revenue per observed date; missing dates are absent, not filled with zero |
| Monthly revenue / invoices | Revenue sum / distinct invoice count by calendar month in chronological order; missing months remain NaN |
| Partial month | Observation/filter start later than calendar first day or end earlier than last day; boundary-day completeness itself is unknown |
| MoM | (Current − Previous) / Previous × 100; NaN if previous missing/zero. MoMPartial flags either month incomplete |
| Weekday revenue | Revenue summed by weekday, Monday through Sunday; not normalized for number of days |
| Hour transactions | Distinct invoices per recorded hour |
| Product revenue / quantity | Sum by merchandise StockCode, with one modal description; ties in rankings resolved by code |
| Product revenue share / concentration | Selected product revenue / ALL positive-sales revenue × 100, including non-product denominator |
| Customer concentration | Selected identified-customer revenue / ALL identified-customer revenue × 100; top 20% rounds customer count upward |
| Pareto | Cumulative ranked merchandise revenue / all positive-sales revenue × 100; may finish below 100% due to non-products |
| Country revenue / invoices / customers | Sum revenue / distinct invoices / distinct identified customers by recorded country; mean invoice revenue = country revenue / country invoices |
| Cancellation invoices | Distinct InvoiceNo starting C, after exact deduplication; not necessarily matched returns |
| Negative-quantity records | Deduplicated quality records with Quantity < 0, including cancellation lines |
| Cancelled value relative to gross sales | Sum absolute line value on C invoices / gross positive-sales revenue × 100 in the same dates; NOT refund or return rate |
| Cancellation products | Cancellation line count and distinct invoice count by merchandise StockCode |
| IQR outliers | Invoice revenue or units outside Q1−1.5×IQR to Q3+1.5×IQR; retained. Revenue share uses all invoice revenue |
| Spearman correlation | Rank correlation between invoice total units and invoice revenue; descriptive, not causal |
| Mann–Whitney comparison | Observed weekday versus weekend daily revenues; two-sided U p-value; effect size = 2U/(n_weekday×n_weekend)−1; positive favors weekday. Medians and group day counts reported. Days may be temporally dependent; missing trading days and seasonality confound interpretation |
| RFM Recency | Days since last identified purchase, reference one day after latest sales date in supplied data |
| RFM Frequency / Monetary | Distinct identified invoices / identified revenue in supplied data |
| RFM scores | ceil(average percentile rank × 5), clipped 1–5. Recency ranks reversed. Equal values share score; some bins may be empty, particularly tiny data |
| RFM segments | First matching: Champions R≥4,F≥4,M≥4; At Risk R≤2,F≥3; Lost R=1; Loyal F≥3; New R≥4,F≤2; otherwise Developing |
| Segment contribution | Segment identified revenue / all identified revenue × 100; size counts identified customers |

The full-source cleaning audit is provenance metadata and is not recomputed by dashboard filters. Date-window quality tables are filtered by date only; country/product/price filters apply to sales metrics. Cleaning exclusion reasons are mutually exclusive in this priority: cancellation, invalid date, missing invoice, invalid quantity, nonpositive quantity, invalid price, nonpositive price. A row with several problems is counted once in reconciliation.
