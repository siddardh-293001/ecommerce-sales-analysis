"""Single source of Monsoon Clay design tokens."""
import matplotlib as mpl
import seaborn as sns
import plotly.graph_objects as go
import plotly.io as pio
from matplotlib.colors import LinearSegmentedColormap
BACKGROUND="#F4EDE4"
SURFACE="#FFFDF8"
SIDEBAR="#EBDFCF"
TEXT="#2B2118"
TEXT_MUTED="#6B5B4B"
GRID="#E2D6C6"
PRIMARY="#2E5E4E"
ACCENT="#C2571A"
POSITIVE="#4F7F5B"
NEGATIVE="#A12A2A"
CONTEXT="#B8A99A"
INDIGO="#3B4A7A"
TURMERIC="#D9A441"
CLAY="#8A6F5A"
SAGE="#7FA39A"
SAND="#E8C27A"
CATEGORIES=[PRIMARY,ACCENT,INDIGO,TURMERIC,CLAY,SAGE]
SEQUENTIAL=LinearSegmentedColormap.from_list("clay",[BACKGROUND,SAND,TURMERIC,ACCENT])
DIVERGING=LinearSegmentedColormap.from_list("change",[NEGATIVE,BACKGROUND,PRIMARY])
def apply_matplotlib_theme():
    """Set consistent chart typography, backgrounds, and grid styling."""
    sns.set_theme(style="whitegrid",palette=CATEGORIES)
    mpl.rcParams.update({"figure.facecolor":BACKGROUND,"axes.facecolor":SURFACE,"text.color":TEXT,"axes.labelcolor":TEXT_MUTED,"xtick.color":TEXT_MUTED,"ytick.color":TEXT_MUTED,"grid.color":GRID,"axes.spines.top":False,"axes.spines.right":False,"figure.figsize":(10,5)})
def get_plotly_template():
    """Register and return the shared interactive template."""
    template=go.layout.Template(layout=dict(colorway=CATEGORIES,paper_bgcolor=BACKGROUND,plot_bgcolor=SURFACE,font=dict(color=TEXT),xaxis=dict(gridcolor=GRID),yaxis=dict(gridcolor=GRID)))
    pio.templates["monsoon"]=template
    return template

def write_streamlit_config(path):
    """Generate Streamlit configuration directly from theme tokens."""
    path.write_text(f'[theme]\nbase = "light"\nprimaryColor = "{PRIMARY}"\nbackgroundColor = "{BACKGROUND}"\nsecondaryBackgroundColor = "{SIDEBAR}"\ntextColor = "{TEXT}"\nfont = "sans serif"\n')
