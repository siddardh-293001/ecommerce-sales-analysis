"""Presentation only: callers supply already aggregated chart data."""
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from . import theme

def chart(table, value, title, kind="bar", horizontal=False, cancellation=False):
    """Return a static figure; partial observations use hatching and labels."""
    fig,ax=plt.subplots()
    color=theme.NEGATIVE if cancellation else theme.PRIMARY
    labels=table.index.astype(str)
    if kind=="line": ax.plot(labels,table[value],color=color,marker=".")
    elif horizontal: ax.barh(labels,table[value],color=color); ax.invert_yaxis()
    else:
        bars=ax.bar(labels,table[value],color=color)
        if "Partial" in table:
            for bar,partial in zip(bars,table.Partial):
                if partial: bar.set_facecolor(theme.CONTEXT); bar.set_hatch("///")
    ax.set_title(title); ax.set_xlabel(value if horizontal else (table.index.name or "Observation")); ax.set_ylabel((table.index.name or "Category") if horizontal else value)
    if not horizontal:
        step=max(1,len(labels)//12)
        ax.set_xticks(range(0,len(labels),step),labels[::step],rotation=45,ha="right")
    ax.grid(False); ax.grid(axis="x" if horizontal else "y"); fig.tight_layout(); return fig

def distribution(values,title,xlabel="Revenue (GBP, logarithmic)"):
    """Return a histogram with a logarithmic revenue axis; input must be positive."""
    import numpy as np
    fig,ax=plt.subplots()
    if len(values):
        lo,hi=values.min(),values.max()
        bins=np.geomspace(lo,hi if hi>lo else lo*1.01,35)
        ax.hist(values,bins=bins,color=theme.PRIMARY); ax.set_xscale("log")
    ax.set(title=title,xlabel=xlabel,ylabel="Count"); fig.tight_layout(); return fig

def interactive(table,value,title,kind="bar",horizontal=False,cancellation=False):
    """Return an interactive figure without computing metrics or filtering data."""
    labels=table.index.astype(str).tolist()
    color=theme.NEGATIVE if cancellation else theme.PRIMARY
    fig=go.Figure()
    if kind=="line": fig.add_scatter(x=labels,y=table[value],mode="lines+markers",line_color=color)
    elif horizontal: fig.add_bar(y=labels,x=table[value],orientation="h",marker_color=color)
    else:
        partial=table.Partial.tolist() if "Partial" in table else [False]*len(table)
        fig.add_bar(x=labels,y=table[value],marker_color=[theme.CONTEXT if x else color for x in partial],marker_pattern_shape=["/" if x else "" for x in partial],customdata=["Partial month" if x else "" for x in partial],hovertemplate="%{x}: %{y:,.2f}<br>%{customdata}<extra></extra>")
    fig.update_layout(template=theme.get_plotly_template(),title=title,xaxis_title=value if horizontal else table.index.name,yaxis_title=table.index.name if horizontal else value,height=410)
    if horizontal: fig.update_yaxes(autorange="reversed")
    return fig
