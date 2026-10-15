"""
Portfolio v7 - Cloud-Optimized Edition
For Streamlit Community Cloud deployment.

Run locally: python -m streamlit run portfolio_v7.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine, text
from scipy.optimize import newton
import warnings
import os

warnings.filterwarnings('ignore')

st.set_page_config(page_title="Portfolio v7 | Wealth Manager",
                   page_icon="⚡", layout="wide",
                   initial_sidebar_state="expanded")

# ==================== ENHANCED FUTURISTIC CSS ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Rajdhani:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');

    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    @keyframes slideInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .stApp {
        background: linear-gradient(-45deg, #eef2ff, #f0f7ff, #fdf0ff, #fff0f5, #f0fff7);
        background-size: 400% 400%;
        animation: gradientShift 25s ease infinite;
        color: #1a1a2e;
    }
    * { font-family: 'Inter', 'Rajdhani', sans-serif; }
    h1, h2, h3, .futuristic-font {
        font-family: 'Orbitron', sans-serif !important;
        letter-spacing: 1.5px;
        color: #1a1a2e;
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(255,255,255,0.92) 0%, rgba(245,240,255,0.92) 100%);
        backdrop-filter: blur(24px);
        border-right: 1px solid rgba(124,77,255,0.15);
        box-shadow: 4px 0 30px rgba(100,100,200,0.08);
    }
    section[data-testid="stSidebar"] * { color: #2a2a4a !important; }

    .hero-card {
        background: linear-gradient(135deg, rgba(99,102,241,0.95) 0%, rgba(168,85,247,0.92) 50%, rgba(236,72,153,0.90) 100%);
        border-radius: 24px;
        padding: 40px 44px;
        color: #fff;
        margin-bottom: 28px;
        box-shadow: 0 20px 60px rgba(99,102,241,0.35), 0 8px 20px rgba(168,85,247,0.20);
        position: relative;
        overflow: hidden;
        animation: slideInUp 0.6s ease-out;
    }
    .hero-card::before {
        content: '';
        position: absolute;
        top: -50%; right: -50%;
        width: 200%; height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 60%);
        animation: float 8s ease-in-out infinite;
    }
    .hero-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 38px;
        font-weight: 900;
        letter-spacing: 4px;
        margin-bottom: 8px;
        text-shadow: 0 4px 20px rgba(0,0,0,0.15);
        position: relative; z-index: 2;
    }
    .hero-subtitle {
        font-size: 16px;
        opacity: 0.92;
        letter-spacing: 1px;
        position: relative; z-index: 2;
    }
    .glass-card {
        background: rgba(255,255,255,0.78);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.6);
        border-radius: 20px;
        padding: 22px 24px;
        box-shadow: 0 10px 30px rgba(100,100,200,0.10), 0 2px 6px rgba(100,100,200,0.05), inset 0 1px 0 rgba(255,255,255,0.9);
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 14px;
        position: relative;
        overflow: hidden;
    }
    .glass-card::after {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #6366f1, #a855f7, #ec4899);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    .glass-card:hover { transform: translateY(-4px); box-shadow: 0 20px 40px rgba(124,77,255,0.20), 0 4px 12px rgba(100,100,200,0.10); }
    .glass-card:hover::after { opacity: 1; }
    .metric-label { font-size: 11px; color: #8a8aa8; text-transform: uppercase; letter-spacing: 2px; font-weight: 600; }
    .metric-value {
        font-size: 26px; font-weight: 800; font-family: 'Orbitron', sans-serif;
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; margin: 8px 0 4px 0; letter-spacing: 0.5px;
    }
    .metric-value.profit { background: linear-gradient(135deg, #10b981 0%, #059669 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .metric-value.loss { background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .metric-sub { font-size: 12px; color: #8a8aa8; margin-top: 2px; }
    .cyber-header {
        font-family: 'Orbitron', sans-serif; font-size: 24px; font-weight: 800;
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; text-transform: uppercase; letter-spacing: 3px;
        padding-bottom: 12px; border-bottom: 2px solid;
        border-image: linear-gradient(90deg, #6366f1, #a855f7, #ec4899, transparent) 1;
        margin: 20px 0 18px 0;
    }
    .cyber-subheader {
        font-family: 'Orbitron', sans-serif; font-size: 14px; font-weight: 700;
        color: #7c3aed; text-transform: uppercase; letter-spacing: 2.5px;
        margin: 20px 0 12px 0; display: flex; align-items: center; gap: 8px;
    }
    .cyber-subheader::before {
        content: ''; display: inline-block; width: 4px; height: 16px;
        background: linear-gradient(180deg, #6366f1, #ec4899); border-radius: 2px;
    }
    .status-bar {
        background: rgba(255,255,255,0.72); backdrop-filter: blur(20px);
        border: 1px solid rgba(124,77,255,0.12); border-radius: 14px;
        padding: 12px 22px; display: flex; justify-content: space-between;
        align-items: center; font-size: 13px; color: #4a4a6a;
        margin-bottom: 22px; box-shadow: 0 4px 14px rgba(100,100,200,0.06);
        flex-wrap: wrap; gap: 8px;
    }
    .status-live { color: #059669; font-weight: 700; }
    .status-cached { color: #d97706; font-weight: 700; }
    .stButton button {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%) !important;
        color: #fff !important; border: none !important; border-radius: 12px !important;
        font-weight: 700 !important; font-family: 'Orbitron', sans-serif !important;
        letter-spacing: 1px; font-size: 12px; padding: 10px 20px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 14px rgba(99,102,241,0.25);
    }
    .stButton button:hover { box-shadow: 0 12px 28px rgba(99,102,241,0.45); transform: translateY(-2px); }
    .stButton button[kind="secondary"] {
        background: rgba(255,255,255,0.9) !important;
        border: 1px solid rgba(239,68,68,0.4) !important;
        color: #dc2626 !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255,255,255,0.55); backdrop-filter: blur(14px);
        border-radius: 14px; padding: 6px; gap: 4px;
        border: 1px solid rgba(124,77,255,0.1);
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent; color: #6a6a8a; border-radius: 10px;
        font-weight: 600; padding: 9px 20px; transition: all 0.25s ease;
    }
    .stTabs [data-baseweb="tab"]:hover { background: rgba(168,85,247,0.08); }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(99,102,241,0.18), rgba(168,85,247,0.18)) !important;
        color: #6366f1 !important;
    }
    .stDataFrame { background: rgba(255,255,255,0.88); border-radius: 14px; border: 1px solid rgba(124,77,255,0.08); }
    .explainer {
        background: linear-gradient(135deg, rgba(238,242,255,0.85), rgba(253,240,255,0.85));
        backdrop-filter: blur(14px); border-left: 4px solid #a855f7;
        border-radius: 0 14px 14px 0; padding: 16px 22px;
        margin-bottom: 18px; font-size: 14px; color: #4a4a6a;
        box-shadow: 0 4px 12px rgba(100,100,200,0.06);
    }
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #6366f1, #a855f7, #ec4899); border-radius: 10px;
    }
    .stProgress > div > div > div { background: rgba(200,200,230,0.3); border-radius: 10px; height: 10px; }
    .stTextInput input, .stNumberInput input {
        background: rgba(255,255,255,0.9) !important;
        border: 1px solid rgba(124,77,255,0.15) !important;
        border-radius: 10px !important; color: #1a1a2e !important;
    }
    div[data-baseweb="select"] > div {
        background: rgba(255,255,255,0.9) !important;
        border: 1px solid rgba(124,77,255,0.15) !important; border-radius: 10px !important;
    }
    div[data-testid="stMetricValue"] { color: #1a1a2e !important; font-family: 'Orbitron', sans-serif; }
    div[data-testid="stMetricLabel"] { color: #6a6a8a !important; }
    .stAlert { border-radius: 14px !important; border-left-width: 4px !important; }
</style>
""", unsafe_allow_html=True)

# ==================== IST HELPERS ====================
IST = timezone(timedelta(hours=5, minutes=30))
def now_ist(): return datetime.now(IST)
def is_market_open():
    n = now_ist()
    if n.weekday() >= 5: return False
    t = n.time()
    return datetime.strptime('09:15','%H:%M').time() <= t <= datetime.strptime('15:30','%H:%M').time()
def should_refresh():
    n = now_ist(); today = n.strftime('%Y-%m-%d')
    if st.session_state.get('last_fetch_date') != today: return True
    if st.session_state.get('last_fetch_time') is None: return True
    t = n.time()
    sess = 'open' if datetime.strptime('09:15','%H:%M').time() <= t <= datetime.strptime('15:30','%H:%M').time() else 'closed'
    return st.session_state.get('last_session') != sess
def mark_fetched():
    n = now_ist()
    st.session_state['last_fetch_time'] = n
    st.session_state['last_fetch_date'] = n.strftime('%Y-%m-%d')
    t = n.time()
    st.session_state['last_session'] = 'open' if datetime.strptime('09:15','%H:%M').time() <= t <= datetime.strptime('15:30','%H:%M').time() else 'closed'

# ==================== DATABASE ====================
# Use /tmp on cloud (Streamlit Cloud has ephemeral but writable /tmp), else local file
if os.path.exists('/tmp') and os.access('/tmp', os.W_OK) and 'STREAMLIT_SHARING' in os.environ:
    DB_PATH = "/tmp/portfolio_v7.db"
else:
    DB_PATH = "portfolio_v7.db"

engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})

def init_db():
    with engine.connect() as conn:
        conn.execute(text("""CREATE TABLE IF NOT EXISTS holdings (
            id INTEGER PRIMARY KEY AUTOINCREMENT, symbol TEXT NOT NULL, name TEXT,
            asset_type TEXT, quantity REAL DEFAULT 0, avg_price REAL DEFAULT 0,
            target_weight REAL DEFAULT 0, sector TEXT DEFAULT 'Unknown', added_date TEXT)"""))
        conn.execute(text("""CREATE TABLE IF NOT EXISTS snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT NOT NULL,
            portfolio_value REAL, invested_value REAL, pnl REAL, pnl_pct REAL, session TEXT)"""))
        conn.execute(text("""CREATE TABLE IF NOT EXISTS cash_flows (
            id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT NOT NULL, amount REAL, description TEXT)"""))
        conn.execute(text("""CREATE TABLE IF NOT EXISTS forward_tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT, start_date TEXT NOT NULL,
            initial_capital REAL, target_amount REAL, horizon_years REAL,
            status TEXT DEFAULT 'active', notes TEXT)"""))
        conn.execute(text("""CREATE TABLE IF NOT EXISTS custom_stocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT, symbol TEXT UNIQUE, name TEXT,
            cap_category TEXT, added_date TEXT)"""))
        try: conn.execute(text("ALTER TABLE snapshots ADD COLUMN session TEXT"))
        except Exception: pass
        conn.commit()
init_db()

# ==================== DEBT + GOLD + SILVER ====================
DEBT_INSTRUMENTS = {
    'G-Sec 2033': {'yield': 7.18, 'risk': 'Low', 'type': 'Government Bond'},
    'G-Sec 2043': {'yield': 7.35, 'risk': 'Low', 'type': 'Government Bond'},
    'G-Sec 2053': {'yield': 7.42, 'risk': 'Low', 'type': 'Government Bond'},
    'Corporate Bond AAA': {'yield': 7.85, 'risk': 'Medium', 'type': 'Corporate Bond'},
    'Corporate Bond AA': {'yield': 8.25, 'risk': 'Medium', 'type': 'Corporate Bond'},
    'SDI 2028': {'yield': 7.45, 'risk': 'Low-Medium', 'type': 'State Development Loan'},
    'T-Bill 91D': {'yield': 6.85, 'risk': 'Very Low', 'type': 'Treasury Bill'},
    'T-Bill 182D': {'yield': 6.95, 'risk': 'Very Low', 'type': 'Treasury Bill'},
    'Liquid Fund': {'yield': 6.50, 'risk': 'Very Low', 'type': 'Debt Mutual Fund'},
    'Ultra Short Duration Fund': {'yield': 7.10, 'risk': 'Very Low', 'type': 'Debt Mutual Fund'},
    'Short Duration Fund': {'yield': 7.30, 'risk': 'Low', 'type': 'Debt Mutual Fund'},
    'Corporate FD': {'yield': 8.50, 'risk': 'Medium', 'type': 'Fixed Deposit'},
    'Post Office TD': {'yield': 7.50, 'risk': 'Very Low', 'type': 'Post Office Scheme'},
    'PPF': {'yield': 7.10, 'risk': 'Very Low', 'type': 'Tax-Saving Scheme'},
}

COMMODITY_ASSETS = {
    'Gold (GOLDBEES)': {'ticker': 'GOLDBEES.NS', 'type': 'Gold ETF', 'risk': 'Medium'},
    'Gold (GOLD)': {'ticker': 'GOLD.NS', 'type': 'Gold ETF', 'risk': 'Medium'},
    'Silver (SILVERBEES)': {'ticker': 'SILVERBEES.NS', 'type': 'Silver ETF', 'risk': 'Medium-High'},
    'Silver (SILVER)': {'ticker': 'SILVER.NS', 'type': 'Silver ETF', 'risk': 'Medium-High'},
}

# ==================== STOCK UNIVERSE ====================
LARGECAP_STOCKS = [
    'HDFCBANK.NS', 'ICICIBANK.NS', 'SBIN.NS', 'AXISBANK.NS', 'KOTAKBANK.NS',
    'BAJFINANCE.NS', 'TCS.NS', 'INFY.NS', 'HCLTECH.NS', 'WIPRO.NS',
    'RELIANCE.NS', 'NTPC.NS', 'POWERGRID.NS', 'ADANIPORTS.NS', 'TATASTEEL.NS',
    'M&M.NS', 'TATAMOTORS.NS', 'MARUTI.NS', 'BHARTIARTL.NS', 'ITC.NS',
    'HINDUNILVR.NS', 'SUNPHARMA.NS', 'DRREDDY.NS', 'CIPLA.NS', 'LT.NS',
]

MIDCAP_STOCKS = [
    'DIXON.NS', 'POLYCAB.NS', 'COCHINSHIP.NS', 'MAZDOCK.NS', 'CUMMINSIND.NS',
    'BDL.NS', 'BHEL.NS', 'AIAENG.NS', 'KIRLOSENG.NS', 'KEI.NS',
    'FEDERALBNK.NS', 'IDFCFIRSTB.NS', 'INDUSINDBK.NS', 'MUTHOOTFIN.NS', 'MANAPPURAM.NS',
    'POLICYBZR.NS', 'BSE.NS', 'LTF.NS', 'HDFCAMC.NS', 'LICHSGFIN.NS',
    'ASTRAL.NS', 'SONACOMS.NS', 'TIINDIA.NS', 'SUPREMEIND.NS', 'METROBRAND.NS',
    'KALYANKJIL.NS', 'INDHOTEL.NS', 'UNOMINDA.NS', 'BALKRISIND.NS', 'DEVYANI.NS',
    'PERSISTENT.NS', 'COFORGE.NS', 'MPHASIS.NS', 'LTTS.NS', 'TATACOMM.NS',
    'ALKEM.NS', 'LAURUSLABS.NS', 'AUROPHARMA.NS', 'IPCALAB.NS', 'MAXHEALTH.NS', 'SYNGENE.NS',
    'JSWENERGY.NS', 'JINDALSTEL.NS', 'SAIL.NS', 'DEEPAKNTR.NS', 'TATACHEM.NS',
    'PIIND.NS', 'GUJGASLTD.NS', 'ATUL.NS', 'CONCOR.NS',
]

SMALLCAP_STOCKS = [
    'SYRMA.NS', 'HFCL.NS', 'DATAPATTNS.NS', 'ELECON.NS', 'IONEXCHANG.NS',
    'ACE.NS', 'TECHNOE.NS', 'PRAJIND.NS', 'KIRLPNU.NS', 'VOLTAMP.NS',
    'TDPOWERSYS.NS', 'DYNAMATECH.NS', 'GMMPFAUDLR.NS', 'ENGINERSIN.NS', 'HBLPOWER.NS',
    'FORCEMOT.NS', 'CRAFTSMAN.NS', 'JAMNAAUTO.NS', 'GABRIEL.NS', 'SUPRAJIT.NS',
    'RKFORGE.NS', 'SUBROS.NS', 'LUMAXIND.NS', 'SUNDRMFAST.NS', 'ALICON.NS',
    'KARURVYSYA.NS', 'CUB.NS', 'KTKBANK.NS', 'EQUITASBNK.NS', 'UJJIVANSFB.NS',
    'CREDITACC.NS', 'CANFINHOME.NS', 'CAMS.NS', 'CDSL.NS', 'ANANDRATHI.NS',
    'IIFLSEC.NS', 'MONARCH.NS',
    'NESCO.NS', 'JKPAPER.NS', 'CENTURYPLY.NS', 'GREENPANEL.NS', 'STYLAMIND.NS',
    'VGUARD.NS', 'CERA.NS', 'SOMANYCERA.NS', 'GOKEX.NS', 'RAYMOND.NS',
    'SYMPHONY.NS', 'TCNSBRANDS.NS', 'AMBER.NS',
    'HSCL.NS', 'HINDCOPPER.NS', 'MAHSEAMLES.NS', 'GULFOILLUB.NS', 'FINEORG.NS',
    'AETHER.NS', 'CLEAN.NS', 'CHEMPLASTS.NS', 'GALAXYSURF.NS', 'NOCIL.NS',
    'TIRUMALCHM.NS', 'NEOGEN.NS',
    'SUVENPHAR.NS', 'GRANULES.NS', 'ERIS.NS', 'AJANTPHARM.NS', 'CAPLIPOINT.NS',
    'SHILPAMED.NS', 'METROPOLIS.NS',
    'BSOFT.NS', 'HAPPSTMNDS.NS', 'ZENSARTECH.NS', 'CYIENT.NS', 'SONATSOFTW.NS', 'ROUTE.NS',
]

PREDEFINED_PORTFOLIO = [
    ('POLYCAB.NS',   'Polycab India',              'Mid-Cap',   8.00, 800000),
    ('DIXON.NS',     'Dixon Technologies',         'Mid-Cap',   8.00, 800000),
    ('PERSISTENT.NS','Persistent Systems',         'Mid-Cap',   8.00, 800000),
    ('ASTRAL.NS',    'Astral Ltd',                 'Mid-Cap',   8.00, 800000),
    ('FEDERALBNK.NS','Federal Bank',               'Mid-Cap',   8.00, 800000),
    ('KALYANKJIL.NS','Kalyan Jewellers',           'Mid-Cap',   8.00, 800000),
    ('COCHINSHIP.NS','Cochin Shipyard',            'Mid-Cap',   8.00, 800000),
    ('METROBRAND.NS','Metro Brands',               'Mid-Cap',   8.00, 800000),
    ('SYNGENE.NS',   'Syngene International',      'Mid-Cap',   8.00, 800000),
    ('CDSL.NS',      'CDSL',                       'Small-Cap', 4.67, 467000),
    ('ANANDRATHI.NS','Anand Rathi Wealth',         'Small-Cap', 4.67, 467000),
    ('FINEORG.NS',   'Fine Organic Industries',    'Small-Cap', 4.67, 467000),
    ('DATAPATTNS.NS','Data Patterns',              'Small-Cap', 4.67, 467000),
    ('IONEXCHANG.NS','Ion Exchange',               'Small-Cap', 4.67, 467000),
    ('CERA.NS',      'Cera Sanitaryware',          'Small-Cap', 4.66, 466000),
]

SECTOR_MAP = {
    'Banking': ['HDFCBANK.NS','ICICIBANK.NS','SBIN.NS','AXISBANK.NS','KOTAKBANK.NS',
                 'FEDERALBNK.NS','IDFCFIRSTB.NS','INDUSINDBK.NS','KARURVYSYA.NS','CUB.NS',
                 'KTKBANK.NS','EQUITASBNK.NS','UJJIVANSFB.NS'],
    'Financial Services': ['BAJFINANCE.NS','MUTHOOTFIN.NS','MANAPPURAM.NS','POLICYBZR.NS',
                            'BSE.NS','LTF.NS','HDFCAMC.NS','LICHSGFIN.NS','CREDITACC.NS',
                            'CANFINHOME.NS','CAMS.NS','CDSL.NS','ANANDRATHI.NS','IIFLSEC.NS','MONARCH.NS'],
    'Technology': ['TCS.NS','INFY.NS','HCLTECH.NS','WIPRO.NS','PERSISTENT.NS','COFORGE.NS',
                    'MPHASIS.NS','LTTS.NS','TATACOMM.NS','BSOFT.NS','HAPPSTMNDS.NS',
                    'ZENSARTECH.NS','CYIENT.NS','SONATSOFTW.NS','ROUTE.NS'],
    'Energy': ['RELIANCE.NS','NTPC.NS','POWERGRID.NS','JSWENERGY.NS','GUJGASLTD.NS'],
    'Industrials': ['LT.NS','DIXON.NS','POLYCAB.NS','COCHINSHIP.NS','MAZDOCK.NS',
                     'CUMMINSIND.NS','BDL.NS','BHEL.NS','AIAENG.NS','KIRLOSENG.NS','KEI.NS',
                     'SYRMA.NS','HFCL.NS','DATAPATTNS.NS','ELECON.NS','IONEXCHANG.NS',
                     'ACE.NS','TECHNOE.NS','PRAJIND.NS','KIRLPNU.NS','VOLTAMP.NS',
                     'TDPOWERSYS.NS','DYNAMATECH.NS','GMMPFAUDLR.NS','ENGINERSIN.NS','HBLPOWER.NS',
                     'SONACOMS.NS','UNOMINDA.NS','BALKRISIND.NS'],
    'Auto': ['M&M.NS','TATAMOTORS.NS','MARUTI.NS','TIINDIA.NS',
              'FORCEMOT.NS','CRAFTSMAN.NS','JAMNAAUTO.NS','GABRIEL.NS','SUPRAJIT.NS',
              'RKFORGE.NS','SUBROS.NS','LUMAXIND.NS','SUNDRMFAST.NS','ALICON.NS'],
    'Consumer': ['ITC.NS','HINDUNILVR.NS','ASTRAL.NS','SUPREMEIND.NS','METROBRAND.NS',
                  'KALYANKJIL.NS','INDHOTEL.NS','DEVYANI.NS',
                  'NESCO.NS','JKPAPER.NS','CENTURYPLY.NS','GREENPANEL.NS','STYLAMIND.NS',
                  'VGUARD.NS','CERA.NS','SOMANYCERA.NS','GOKEX.NS','RAYMOND.NS',
                  'SYMPHONY.NS','TCNSBRANDS.NS','AMBER.NS'],
    'Healthcare': ['SUNPHARMA.NS','DRREDDY.NS','CIPLA.NS','ALKEM.NS','LAURUSLABS.NS',
                    'AUROPHARMA.NS','IPCALAB.NS','MAXHEALTH.NS','SYNGENE.NS',
                    'SUVENPHAR.NS','GRANULES.NS','ERIS.NS','AJANTPHARM.NS','CAPLIPOINT.NS',
                    'SHILPAMED.NS','METROPOLIS.NS'],
    'Materials': ['TATASTEEL.NS','JINDALSTEL.NS','SAIL.NS','DEEPAKNTR.NS','TATACHEM.NS',
                   'PIIND.NS','ATUL.NS','CONCOR.NS','HSCL.NS','HINDCOPPER.NS','MAHSEAMLES.NS',
                   'GULFOILLUB.NS','FINEORG.NS','AETHER.NS','CLEAN.NS','CHEMPLASTS.NS',
                   'GALAXYSURF.NS','NOCIL.NS','TIRUMALCHM.NS','NEOGEN.NS'],
    'Telecom': ['BHARTIARTL.NS'],
    'Logistics': ['ADANIPORTS.NS'],
    'Gold': ['GOLDBEES.NS','GOLD.NS'],
    'Silver': ['SILVERBEES.NS','SILVER.NS'],
}

def get_sector(symbol):
    for sector, stocks in SECTOR_MAP.items():
        if symbol in stocks: return sector
    return 'Other'

SECTOR_INDEX_MAP = {
    'Banking': '^NSEBANK', 'Financial Services': '^NSEBANK', 'Technology': '^CNXIT',
    'Energy': '^CNXENERGY', 'Industrials': '^CNXINFRA', 'Auto': '^CNXAUTO',
    'Consumer': '^CNXFMCG', 'Healthcare': '^CNXPHARMA', 'Materials': '^CNXMETAL',
}

# ==================== DATA FETCH ====================
@st.cache_data(ttl=900)
def fetch_price(symbol, period='1y'):
    try:
        h = yf.Ticker(symbol).history(period=period)
        return h if not h.empty else None
    except Exception: return None

@st.cache_data(ttl=900)
def fetch_current_price(symbol):
    try:
        h = yf.Ticker(symbol).history(period='5d')
        return float(h['Close'].iloc[-1]) if not h.empty else None
    except Exception: return None

@st.cache_data(ttl=3600)
def fetch_metrics(symbol):
    try:
        info = yf.Ticker(symbol).info
        return {
            'market_cap': info.get('marketCap', 0) or 0,
            'pe_ratio': info.get('trailingPE', 0) or 0,
            'forward_pe': info.get('forwardPE', 0) or 0,
            'pb_ratio': info.get('priceToBook', 0) or 0,
            'dividend_yield': info.get('dividendYield', 0) or 0,
            'beta': info.get('beta', 1.0) or 1.0,
            'roe': info.get('returnOnEquity', 0) or 0,
            'roa': info.get('returnOnAssets', 0) or 0,
            'eps': info.get('trailingEps', 0) or 0,
            'debt_to_equity': info.get('debtToEquity', 0) or 0,
            'current_ratio': info.get('currentRatio', 0) or 0,
            'profit_margin': info.get('profitMargins', 0) or 0,
            'operating_margin': info.get('operatingMargins', 0) or 0,
            'revenue_growth': info.get('revenueGrowth', 0) or 0,
            'earnings_growth': info.get('earningsGrowth', 0) or 0,
            'sector': info.get('sector', 'Unknown'),
            'name': info.get('longName', symbol) or symbol,
        }
    except Exception:
        return {k: 0 for k in ['market_cap','pe_ratio','forward_pe','pb_ratio','dividend_yield',
                'beta','roe','roa','eps','debt_to_equity','current_ratio','profit_margin',
                'operating_margin','revenue_growth','earnings_growth']} | {'sector':'Unknown','name':symbol}

@st.cache_data(ttl=3600)
def search_yahoo_stocks(query):
    try:
        r = yf.Lookup(query).get_all(count=15)
        if r is not None and not r.empty: return r[['symbol','shortName','exchange']].head(15)
    except Exception: pass
    try:
        r = yf.Lookup(query).get_stock(count=15)
        if r is not None and not r.empty: return r[['symbol','shortName','exchange']].head(15)
    except Exception: pass
    return pd.DataFrame()

@st.cache_data(ttl=1800)
def calculate_signal(symbol):
    try:
        h = fetch_price(symbol, '1mo')
        if h is None or len(h) < 2: return 'HOLD', 0.0, 0.0
        sr = (h['Close'].iloc[-1]/h['Close'].iloc[0] - 1)*100
        sec = get_sector(symbol); secr = 0.0
        idx = SECTOR_INDEX_MAP.get(sec)
        if idx:
            try:
                ih = fetch_price(idx, '1mo')
                if ih is not None and len(ih) >= 2:
                    secr = (ih['Close'].iloc[-1]/ih['Close'].iloc[0] - 1)*100
            except Exception: pass
        d = sr - secr
        sig = 'BUY' if d > 2 else ('REVIEW' if d < -2 else 'HOLD')
        return sig, round(sr,2), round(secr,2)
    except Exception: return 'HOLD', 0.0, 0.0

def quality_score(m):
    score = 50.0
    roe = m.get('roe', 0)*100; pm = m.get('profit_margin', 0)*100
    de = m.get('debt_to_equity', 0); rg = m.get('revenue_growth', 0)*100
    eg = m.get('earnings_growth', 0)*100; cr = m.get('current_ratio', 0)
    score += min(roe, 30)*0.5; score += min(pm, 25)*0.4
    score += min(rg, 30)*0.3; score += min(eg, 30)*0.3
    if de > 0: score -= min(de/100, 2)*5
    if cr >= 1.5: score += 5
    elif cr < 1: score -= 5
    return max(0, min(100, round(score, 1)))

def calculate_risk_metrics(returns):
    if returns is None or len(returns) < 30: return None
    av = returns.std()*np.sqrt(252)*100
    var = np.percentile(returns, 5)*100
    cvar = returns[returns <= np.percentile(returns, 5)].mean()*100
    cum = (1+returns).cumprod(); run = cum.cummax()
    dd = ((cum-run)/run).min()*100
    rf = 0.07/252; ex = returns - rf
    sh = (ex.mean()/returns.std())*np.sqrt(252) if returns.std() > 0 else 0
    dn = returns[returns < 0]
    so = (ex.mean()/dn.std())*np.sqrt(252) if len(dn) > 0 and dn.std() > 0 else 0
    return {'Annualized Volatility %': round(av,2), 'VaR 95% %': round(var,2),
            'CVaR 95% %': round(cvar,2), 'Max Drawdown %': round(dd,2),
            'Sharpe Ratio': round(sh,2), 'Sortino Ratio': round(so,2)}

def calculate_portfolio_returns(holdings_df, period='1y'):
    if holdings_df.empty: return None, None, None
    eq = holdings_df[holdings_df['asset_type'] == 'Equity']
    if eq.empty: return None, None, None
    tv = (eq['quantity']*eq['avg_price']).sum()
    if tv == 0: return None, None, None
    pd_ = {}
    for _, r in eq.iterrows():
        h = fetch_price(r['symbol'], period)
        if h is not None and not h.empty: pd_[r['symbol']] = h['Close']
    if not pd_: return None, None, None
    px = pd.DataFrame(pd_).dropna()
    if px.empty or len(px) < 30: return None, None, None
    ret = px.pct_change().dropna()
    w = {}
    for _, r in eq.iterrows():
        if r['symbol'] in ret.columns:
            w[r['symbol']] = (r['quantity']*r['avg_price'])/tv
    wv = np.array([w.get(c, 0) for c in ret.columns])
    wv = wv/wv.sum() if wv.sum() > 0 else np.ones(len(wv))/len(wv)
    return (ret*wv).sum(axis=1), px, w

def monte_carlo_projection(ar, av, years=2, initial=10000000, paths=10000):
    dt = 1/252; n = int(years*252)
    np.random.seed(42)
    dr = np.random.normal((ar-0.5*av**2)*dt, av*np.sqrt(dt), (n, paths))
    p = initial*np.exp(np.cumsum(dr, axis=0))
    fv = p[-1, :]
    return {'P10 (Bear)': np.percentile(fv, 10), 'P50 (Base)': np.percentile(fv, 50),
            'P90 (Bull)': np.percentile(fv, 90)}, p

@st.cache_data(ttl=3600, show_spinner=False)
def run_backtest(symbols_tuple, weights_tuple, years=2, initial=1000000):
    try:
        symbols = list(symbols_tuple); weights = np.array(list(weights_tuple))
        if weights.sum() == 0: return None
        weights = weights/weights.sum()
        period = f"{int(years*365)}d"
        px = {}
        for s in symbols:
            h = fetch_price(s, period)
            if h is not None and not h.empty: px[s] = h['Close']
        if not px: return None
        prices = pd.DataFrame(px).dropna()
        if prices.empty or len(prices) < 30: return None
        rets = prices.pct_change().dropna()
        w_map = dict(zip(symbols, weights))
        w_arr = np.array([w_map.get(c, 0) for c in rets.columns])
        w_arr = w_arr/w_arr.sum() if w_arr.sum() > 0 else np.ones(len(w_arr))/len(w_arr)
        port_ret = (rets*w_arr).sum(axis=1)
        port_val = initial*(1+port_ret).cumprod()
        nifty = fetch_price('^NSEI', period)
        bench_val = None
        if nifty is not None and not nifty.empty:
            n_ret = nifty['Close'].pct_change().dropna()
            n_ret = n_ret.reindex(port_ret.index).dropna()
            if len(n_ret) > 0: bench_val = initial*(1+n_ret).cumprod()
        total_return = (port_val.iloc[-1]/initial - 1)*100
        years_actual = len(port_ret)/252
        cagr = ((port_val.iloc[-1]/initial)**(1/years_actual) - 1)*100 if years_actual > 0 else 0
        vol = port_ret.std()*np.sqrt(252)*100
        cum = (1+port_ret).cumprod(); run = cum.cummax()
        mdd = ((cum-run)/run).min()*100
        sharpe = (port_ret.mean()/port_ret.std())*np.sqrt(252) if port_ret.std() > 0 else 0
        return {'dates': port_val.index, 'portfolio': port_val, 'benchmark': bench_val,
                'total_return': total_return, 'cagr': cagr, 'vol': vol,
                'max_dd': mdd, 'sharpe': sharpe, 'final_value': port_val.iloc[-1],
                'initial': initial, 'n_days': len(port_ret)}
    except Exception as e:
        return {'error': str(e)}

def calc_xnpv(rate, cf):
    if not cf: return 0
    d0 = cf[0][0]
    return sum(a/(1+rate)**((d-d0).days/365.0) for d, a in cf)
def calc_xirr(cf, g=0.1):
    if not cf or len(cf) < 2: return None
    try:
        r = newton(lambda x: calc_xnpv(x, cf), g, maxiter=1000, tol=1e-6)
        return r*100 if r is not None else None
    except Exception: return None
def calc_twr(snaps, cfs=None):
    if snaps.empty or len(snaps) < 2: return None
    df = snaps.copy(); df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)
    cm = {}
    if cfs is not None and not cfs.empty:
        c = cfs.copy(); c['date'] = pd.to_datetime(c['date'])
        for _, r in c.iterrows():
            cm[r['date'].strftime('%Y-%m-%d')] = cm.get(r['date'].strftime('%Y-%m-%d'), 0) + r['amount']
    dr = []
    for i in range(1, len(df)):
        pv = df.loc[i-1, 'portfolio_value']; cv = df.loc[i, 'portfolio_value']
        cs = df.loc[i, 'date'].strftime('%Y-%m-%d'); cf = cm.get(cs, 0)
        if pv and pv > 0: dr.append((cv-pv-cf)/pv)
    if not dr: return None
    return (np.prod([1+r for r in dr])-1)*100
def calc_mwr(snaps, cfs=None):
    if snaps.empty: return None
    df = snaps.copy(); df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)
    cf = [(df.iloc[0]['date'].to_pydatetime(), -float(df.iloc[0]['portfolio_value']))]
    if cfs is not None and not cfs.empty:
        c = cfs.copy(); c['date'] = pd.to_datetime(c['date'])
        for _, r in c.iterrows():
            cf.append((r['date'].to_pydatetime(), -float(r['amount'])))
    cf.append((df.iloc[-1]['date'].to_pydatetime(), float(df.iloc[-1]['portfolio_value'])))
    cf.sort(key=lambda x: x[0])
    return calc_xirr(cf)

def load_portfolio():
    try:
        with engine.connect() as conn:
            rows = conn.execute(text("SELECT * FROM holdings ORDER BY id")).fetchall()
        if not rows:
            return pd.DataFrame(columns=['id','symbol','name','asset_type','quantity','avg_price','target_weight','sector','added_date'])
        return pd.DataFrame(rows, columns=['id','symbol','name','asset_type','quantity','avg_price','target_weight','sector','added_date'])
    except Exception:
        return pd.DataFrame(columns=['id','symbol','name','asset_type','quantity','avg_price','target_weight','sector','added_date'])

def load_snapshots():
    try:
        with engine.connect() as conn:
            rows = conn.execute(text("SELECT * FROM snapshots ORDER BY date")).fetchall()
        if not rows:
            return pd.DataFrame(columns=['id','date','portfolio_value','invested_value','pnl','pnl_pct','session'])
        n = len(rows[0]); cols = ['id','date','portfolio_value','invested_value','pnl','pnl_pct','session']
        return pd.DataFrame(rows, columns=cols[:n])
    except Exception:
        return pd.DataFrame(columns=['id','date','portfolio_value','invested_value','pnl','pnl_pct','session'])

def load_cash_flows():
    try:
        with engine.connect() as conn:
            rows = conn.execute(text("SELECT * FROM cash_flows ORDER BY date")).fetchall()
        if not rows: return pd.DataFrame(columns=['id','date','amount','description'])
        return pd.DataFrame(rows, columns=['id','date','amount','description'])
    except Exception:
        return pd.DataFrame(columns=['id','date','amount','description'])

def load_custom():
    try:
        with engine.connect() as conn:
            rows = conn.execute(text("SELECT * FROM custom_stocks ORDER BY symbol")).fetchall()
        if not rows: return pd.DataFrame(columns=['id','symbol','name','cap_category','added_date'])
        return pd.DataFrame(rows, columns=['id','symbol','name','cap_category','added_date'])
    except Exception:
        return pd.DataFrame(columns=['id','symbol','name','cap_category','added_date'])

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:18px 0;">
        <div style="font-family:'Orbitron'; font-size:24px; font-weight:900;
                    background:linear-gradient(135deg, #6366f1, #a855f7, #ec4899);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                    letter-spacing:4px;">PORTFOLIO</div>
        <div style="font-family:'Orbitron'; font-size:11px; color:#a855f7; letter-spacing:8px;
                    margin-top:2px;">V 7 · CLOUD</div>
    </div>""", unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio("NAVIGATE", [
        "⚡ Dashboard", "🔍 Stock Screener", "💎 Fundamentals", "📜 Preset Portfolio",
        "➕ Build Portfolio", "📈 Performance", "🧪 Forward Test",
        "🛡️ Risk Analysis", "📊 Backtest", "🔮 Scenarios", "⚙️ Settings"
    ], label_visibility="collapsed")
    st.markdown("---")
    if is_market_open():
        st.markdown('<div class="status-live">● MARKET OPEN</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-cached">● MARKET CLOSED</div>', unsafe_allow_html=True)
    st.caption(f"IST: {now_ist().strftime('%d %b %Y, %H:%M')}")
    if st.session_state.get('last_fetch_time'):
        st.caption(f"Last fetch: {st.session_state['last_fetch_time'].strftime('%H:%M')}")

holdings_df = load_portfolio()
snapshots_df = load_snapshots()
cash_flows_df = load_cash_flows()
custom_df = load_custom()
CUSTOM_SYMBOLS = custom_df['symbol'].tolist() if not custom_df.empty else []
ALL_EQUITY = list(dict.fromkeys(LARGECAP_STOCKS + MIDCAP_STOCKS + SMALLCAP_STOCKS + CUSTOM_SYMBOLS))

should = should_refresh()
if should:
    st.cache_data.clear(); mark_fetched()

def render_status_bar():
    st.markdown(f"""
    <div class="status-bar">
        <span>◆ MARKET: <b>{'🟢 LIVE' if is_market_open() else '🔴 CLOSED'}</b></span>
        <span>◆ DATA: <b>{'Fresh' if should else 'Cached'}</b> | Last fetch: {st.session_state.get('last_fetch_time', now_ist()).strftime('%d %b, %H:%M IST')}</span>
        <span>◆ UPDATE: Open (09:15) + Close (15:30) IST</span>
    </div>""", unsafe_allow_html=True)

def render_refresh_button():
    _, col = st.columns([5, 1])
    with col:
        if st.button("⟳ REFRESH", use_container_width=True):
            st.cache_data.clear(); mark_fetched(); st.rerun()

# ==================== PAGE: DASHBOARD ====================
if menu == "⚡ Dashboard":
    st.markdown("""
    <div class="hero-card">
        <div class="hero-title">⚡ COMMAND CENTER</div>
        <div class="hero-subtitle">Live portfolio tracking · Real-time signals · Goal-driven wealth management</div>
    </div>
    """, unsafe_allow_html=True)
    render_status_bar(); render_refresh_button()

    if holdings_df.empty:
        st.markdown('<div class="explainer">Your portfolio is empty. Go to <b>📜 Preset Portfolio</b> to load the 15-stock ₹1 Cr preset, or <b>➕ Build Portfolio</b> to add your own.</div>', unsafe_allow_html=True)
        st.markdown('<div class="cyber-subheader">UNIVERSE AVAILABLE</div>', unsafe_allow_html=True)
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1: st.markdown(f'<div class="glass-card"><div class="metric-label">LARGE CAP</div><div class="metric-value">{len(LARGECAP_STOCKS)}</div><div class="metric-sub">Nifty 50 leaders</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="glass-card"><div class="metric-label">MID CAP</div><div class="metric-value">{len(MIDCAP_STOCKS)}</div><div class="metric-sub">Growth companies</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="glass-card"><div class="metric-label">SMALL CAP</div><div class="metric-value">{len(SMALLCAP_STOCKS)}</div><div class="metric-sub">High-upside picks</div></div>', unsafe_allow_html=True)
        with c4: st.markdown(f'<div class="glass-card"><div class="metric-label">DEBT</div><div class="metric-value">{len(DEBT_INSTRUMENTS)}</div><div class="metric-sub">Fixed income</div></div>', unsafe_allow_html=True)
        with c5: st.markdown(f'<div class="glass-card"><div class="metric-label">GOLD/SILVER</div><div class="metric-value">{len(COMMODITY_ASSETS)}</div><div class="metric-sub">Hedge assets</div></div>', unsafe_allow_html=True)
    else:
        ti, tc, ld = 0, 0, []
        for _, r in holdings_df.iterrows():
            if r['asset_type'] == 'Equity':
                p = fetch_current_price(r['symbol']) or r['avg_price']
            else:
                dh = (datetime.now() - pd.to_datetime(r['added_date'])).days
                ay = DEBT_INSTRUMENTS.get(r['symbol'], {}).get('yield', 7.0)
                p = r['avg_price']*(1+ay/100*dh/365)
            inv = r['quantity']*r['avg_price']; cur = r['quantity']*p
            pnl = cur-inv; pp = (pnl/inv*100) if inv > 0 else 0
            ti += inv; tc += cur
            ld.append({'Symbol': r['symbol'], 'Name': str(r['name'])[:30], 'Type': r['asset_type'],
                       'Qty': r['quantity'], 'Avg ₹': round(r['avg_price'],2), 'LTP ₹': round(p,2),
                       'Invested ₹': round(inv,0), 'Current ₹': round(cur,0),
                       'P&L ₹': round(pnl,0), 'P&L %': round(pp,2)})
        tp = tc-ti; tpp = (tp/ti*100) if ti > 0 else 0
        c1, c2, c3, c4 = st.columns(4)
        for col, l, v, cls, sub in [
            (c1,"TOTAL INVESTED",f"₹{ti:,.0f}","", f"{len(holdings_df)} holdings"),
            (c2,"CURRENT VALUE",f"₹{tc:,.0f}","", "Live market value"),
            (c3,"TOTAL P&L",f"₹{tp:,.0f}","profit" if tp>=0 else "loss", f"{tpp:+.2f}%"),
            (c4,"RETURN %",f"{tpp:+.2f}%","profit" if tpp>=0 else "loss", "Overall return")]:
            with col:
                st.markdown(f'<div class="glass-card"><div class="metric-label">{l}</div><div class="metric-value {cls}">{v}</div><div class="metric-sub">{sub}</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="cyber-subheader">🎯 GOAL PROGRESS</div>', unsafe_allow_html=True)
        gp = min(tc/17500000, 1.0)
        st.progress(gp)
        st.caption(f"₹{tc:,.0f} of ₹1,75,00,000 ({gp*100:.1f}% complete) • Remaining: ₹{max(17500000-tc,0):,.0f}")
        st.markdown('<div class="cyber-subheader">⚖ REBALANCING (5/25 RULE)</div>', unsafe_allow_html=True)
        da = []; tv = tc if tc > 0 else 1
        for _, r in holdings_df.iterrows():
            tw = r.get('target_weight')
            if tw and tw > 0:
                p = (fetch_current_price(r['symbol']) or r['avg_price']) if r['asset_type']=='Equity' else r['avg_price']
                cw = (r['quantity']*p)/tv*100; d = abs(cw-tw)
                if d > 5: da.append({'Symbol': r['symbol'], 'Target %': round(tw,1), 'Current %': round(cw,1), 'Drift %': round(d,1), 'Action': '⚠ REBALANCE'})
        if da: st.dataframe(pd.DataFrame(da), use_container_width=True, hide_index=True)
        else: st.success("✓ All holdings within 5% drift threshold")
        st.markdown('<div class="cyber-subheader">📋 LIVE HOLDINGS</div>', unsafe_allow_html=True)
        ldf = pd.DataFrame(ld)
        def cp(v): return 'color: #059669' if isinstance(v,(int,float)) and v>=0 else ('color: #dc2626' if isinstance(v,(int,float)) else '')
        st.dataframe(ldf.style.map(cp, subset=['P&L ₹','P&L %']), use_container_width=True, hide_index=True)
        today = now_ist().strftime('%Y-%m-%d'); sess = 'open' if is_market_open() else 'closed'
        try:
            with engine.connect() as conn:
                ex = conn.execute(text("SELECT id FROM snapshots WHERE date=:d AND session=:s"), {'d':today,'s':sess}).fetchone()
                if ex:
                    conn.execute(text("UPDATE snapshots SET portfolio_value=:p,invested_value=:i,pnl=:pn,pnl_pct=:pp WHERE id=:id"),
                                 {'p':tc,'i':ti,'pn':tp,'pp':tpp,'id':ex[0]})
                else:
                    conn.execute(text("INSERT INTO snapshots (date,portfolio_value,invested_value,pnl,pnl_pct,session) VALUES (:d,:p,:i,:pn,:pp,:s)"),
                                 {'d':today,'p':tc,'i':ti,'pn':tp,'pp':tpp,'s':sess})
                conn.commit()
        except Exception: pass
        if len(snapshots_df) > 1:
            st.markdown('<div class="cyber-subheader">📉 PORTFOLIO TRAJECTORY</div>', unsafe_allow_html=True)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=snapshots_df['date'], y=snapshots_df['portfolio_value'],
                                      name='Portfolio', line=dict(color='#6366f1', width=3),
                                      fill='tozeroy', fillcolor='rgba(99,102,241,0.10)'))
            fig.add_hline(y=ti, line_dash="dash", line_color="#a855f7", annotation_text="Invested")
            fig.add_hline(y=17500000, line_dash="dot", line_color="#f59e0b", annotation_text="Target ₹1.75 Cr")
            fig.update_layout(template='plotly_white', height=420, paper_bgcolor='rgba(0,0,0,0)',
                              plot_bgcolor='rgba(0,0,0,0)', font=dict(family='Inter', color='#4a4a6a'),
                              margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig, use_container_width=True)

# ==================== PAGE: SCREENER ====================
elif menu == "🔍 Stock Screener":
    st.markdown('<h1 class="cyber-header">🔍 Stock Screener</h1>', unsafe_allow_html=True)
    render_status_bar(); render_refresh_button()
    tabs = st.tabs(["🟦 LARGE CAP (25)", "🟩 MID CAP (50)", "🟧 SMALL CAP (75)", "🥇 GOLD & SILVER", "🔎 SEARCH & ADD", "📊 MY HOLDINGS"])

    def render_list(lst, label):
        with st.spinner(f"Loading {len(lst)} {label} stocks..."):
            rows = []
            for s in lst:
                m = fetch_metrics(s); p = fetch_current_price(s); h = fetch_price(s, '1y')
                r1y = ((h['Close'].iloc[-1]/h['Close'].iloc[0]-1)*100) if (h is not None and len(h)>1) else 0
                sig, r1m, sr = calculate_signal(s)
                rows.append({'Symbol':s, 'Name':str(m['name'])[:26], 'LTP ₹':round(p,2) if p else 0,
                             'Mkt Cap (₹Cr)':round(m['market_cap']/1e7,0), 'P/E':round(m['pe_ratio'],1),
                             'ROE %':round(m['roe']*100,1), '1Y %':round(r1y,1),
                             '1M %':r1m, 'Sector 1M %':sr, 'Signal':sig})
            df = pd.DataFrame(rows)
            def cs(v):
                if v=='BUY': return 'background-color: rgba(16,185,129,0.15); color:#059669; font-weight:700'
                if v=='REVIEW': return 'background-color: rgba(239,68,68,0.15); color:#dc2626; font-weight:700'
                if v=='HOLD': return 'background-color: rgba(245,158,11,0.15); color:#d97706; font-weight:700'
                return ''
            def cr(v): return 'color:#059669' if isinstance(v,(int,float)) and v>=0 else ('color:#dc2626' if isinstance(v,(int,float)) else '')
            st.dataframe(df.style.map(cr, subset=['1Y %','1M %','Sector 1M %']).map(cs, subset=['Signal']),
                         use_container_width=True, hide_index=True)

    with tabs[0]:
        st.markdown('<div class="cyber-subheader">LARGE CAP — NIFTY 50 LEADERS</div>', unsafe_allow_html=True)
        render_list(LARGECAP_STOCKS, "large-cap")
    with tabs[1]:
        st.markdown('<div class="cyber-subheader">MID CAP — 50 HIGH-QUALITY GROWTH STOCKS</div>', unsafe_allow_html=True)
        render_list(MIDCAP_STOCKS, "mid-cap")
    with tabs[2]:
        st.markdown('<div class="cyber-subheader">SMALL CAP — 75 HIGH-UPSIDE STOCKS</div>', unsafe_allow_html=True)
        render_list(SMALLCAP_STOCKS, "small-cap")
    with tabs[3]:
        st.markdown('<div class="cyber-subheader">🥇 GOLD & SILVER ETFs</div>', unsafe_allow_html=True)
        with st.spinner("Loading commodity ETFs..."):
            rows = []
            for name, info in COMMODITY_ASSETS.items():
                sym = info['ticker']
                p = fetch_current_price(sym); h = fetch_price(sym, '1y')
                r1y = ((h['Close'].iloc[-1]/h['Close'].iloc[0]-1)*100) if (h is not None and len(h)>1) else 0
                r1m = ((h['Close'].iloc[-1]/h['Close'].iloc[-21]-1)*100) if (h is not None and len(h)>21) else 0
                rows.append({'Name':name, 'Symbol':sym, 'Type':info['type'], 'Risk':info['risk'],
                             'LTP ₹':round(p,2) if p else 0, '1M %':round(r1m,2), '1Y %':round(r1y,2)})
            df = pd.DataFrame(rows)
            def cr2(v): return 'color:#059669' if isinstance(v,(int,float)) and v>=0 else ('color:#dc2626' if isinstance(v,(int,float)) else '')
            st.dataframe(df.style.map(cr2, subset=['1M %','1Y %']), use_container_width=True, hide_index=True)
            st.markdown("""
            <div class="explainer">
            <b>Why Gold & Silver?</b> Precious metals act as a hedge against inflation and market volatility.
            Typically allocate 5–15% of your portfolio to gold for defensive positioning.
            Gold ETFs trade on NSE just like stocks.
            </div>""", unsafe_allow_html=True)
    with tabs[4]:
        st.markdown('<div class="cyber-subheader">🔎 SEARCH YAHOO FINANCE</div>', unsafe_allow_html=True)
        q = st.text_input("SEARCH", placeholder="e.g., Tata Elxsi, HDFC, KPIT")
        if q:
            with st.spinner(f"Searching '{q}'..."):
                res = search_yahoo_stocks(q)
            if not res.empty:
                st.dataframe(res, use_container_width=True, hide_index=True)
                sel = st.selectbox("Select symbol", options=res['symbol'].tolist())
                cc = st.selectbox("Cap Category", ['Large Cap','Mid Cap','Small Cap','Gold','Debt','Custom'])
                if st.button("➕ ADD TO UNIVERSE"):
                    try:
                        info = yf.Ticker(sel).info; nm = info.get('longName', sel) or sel
                        with engine.connect() as conn:
                            conn.execute(text("INSERT OR REPLACE INTO custom_stocks (symbol,name,cap_category,added_date) VALUES (:s,:n,:c,:d)"),
                                         {'s':sel,'n':nm,'c':cc,'d':now_ist().strftime('%Y-%m-%d')})
                            conn.commit()
                        st.success(f"✓ Added {sel}"); st.cache_data.clear(); st.rerun()
                    except Exception as e: st.error(f"Failed: {e}")
            else: st.info("No results. Try another term.")
        if not custom_df.empty:
            st.markdown('<div class="cyber-subheader">CUSTOM STOCKS</div>', unsafe_allow_html=True)
            st.dataframe(custom_df[['symbol','name','cap_category','added_date']], use_container_width=True, hide_index=True)
            rm = st.selectbox("Remove", options=custom_df['symbol'].tolist())
            if st.button("🗑 REMOVE"):
                with engine.connect() as conn:
                    conn.execute(text("DELETE FROM custom_stocks WHERE symbol=:s"), {'s':rm})
                    conn.commit()
                st.cache_data.clear(); st.success(f"✓ Removed {rm}"); st.rerun()
    with tabs[5]:
        if holdings_df.empty: st.info("No holdings.")
        else: st.dataframe(holdings_df, use_container_width=True, hide_index=True)

# ==================== PAGE: FUNDAMENTALS ====================
elif menu == "💎 Fundamentals":
    st.markdown('<h1 class="cyber-header">💎 Fundamental Analysis</h1>', unsafe_allow_html=True)
    render_status_bar(); render_refresh_button()
    st.markdown("""
    <div class="explainer">
    Fundamental metrics from Yahoo Finance company filings.
    <b>Quality Score (0–100)</b> = composite of ROE, profit margin, revenue growth,
    earnings growth, debt-to-equity, and current ratio. 75+ = strong, 55-75 = good, 35-55 = fair, &lt;35 = weak.
    </div>""", unsafe_allow_html=True)
    scope = st.radio("Scope", ["My Holdings", "Large Cap (25)", "Mid Cap (50)", "Small Cap (75)", "Custom"], horizontal=True)
    if scope == "My Holdings":
        syms = holdings_df[holdings_df['asset_type']=='Equity']['symbol'].tolist() if not holdings_df.empty else []
    elif scope == "Large Cap (25)": syms = LARGECAP_STOCKS
    elif scope == "Mid Cap (50)": syms = MIDCAP_STOCKS
    elif scope == "Small Cap (75)": syms = SMALLCAP_STOCKS
    else: syms = CUSTOM_SYMBOLS
    if not syms: st.info("No stocks in this scope.")
    else:
        with st.spinner(f"Loading fundamentals for {len(syms)} stocks..."):
            rows = []
            for s in syms:
                m = fetch_metrics(s)
                rows.append({'Symbol': s, 'Name': str(m['name'])[:24],
                             'P/E': round(m['pe_ratio'],1), 'Fwd P/E': round(m['forward_pe'],1),
                             'P/B': round(m['pb_ratio'],2), 'ROE %': round(m['roe']*100,1),
                             'ROA %': round(m['roa']*100,1),
                             'Profit Margin %': round(m['profit_margin']*100,1),
                             'Op Margin %': round(m['operating_margin']*100,1),
                             'Rev Growth %': round(m['revenue_growth']*100,1),
                             'EPS Growth %': round(m['earnings_growth']*100,1),
                             'D/E': round(m['debt_to_equity'],1) if m['debt_to_equity'] else 0,
                             'Current Ratio': round(m['current_ratio'],2),
                             'Div Yield %': round(m['dividend_yield']*100,2),
                             'Beta': round(m['beta'],2),
                             'Mkt Cap (₹Cr)': round(m['market_cap']/1e7,0),
                             'Quality Score': quality_score(m)})
            df = pd.DataFrame(rows)
            def cq(v):
                if v >= 75: return 'background-color: rgba(16,185,129,0.18); color:#059669; font-weight:700'
                if v >= 55: return 'background-color: rgba(99,102,241,0.18); color:#6366f1; font-weight:700'
                if v >= 35: return 'background-color: rgba(245,158,11,0.18); color:#d97706; font-weight:700'
                return 'background-color: rgba(239,68,68,0.18); color:#dc2626; font-weight:700'
            st.dataframe(df.style.map(cq, subset=['Quality Score']), use_container_width=True, hide_index=True)

# ==================== PAGE: PRESET ====================
elif menu == "📜 Preset Portfolio":
    st.markdown('<h1 class="cyber-header">📜 Preset ₹1 Crore Portfolio</h1>', unsafe_allow_html=True)
    render_status_bar()
    st.markdown("""
    <div class="explainer">
    Pre-constructed 15-stock portfolio allocating ₹1,00,00,000 across mid and small caps.
    9 mid-caps @ 8% each (₹8,00,000) + 6 small caps @ ~4.67% each (~₹4,67,000).
    </div>""", unsafe_allow_html=True)
    preset_df = pd.DataFrame(PREDEFINED_PORTFOLIO, columns=['Symbol','Stock Name','Tier','Allocation %','Target Amount ₹'])
    st.dataframe(preset_df, use_container_width=True, hide_index=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Total Allocation", f"{preset_df['Allocation %'].sum():.2f}%")
    with c2: st.metric("Total Amount", f"₹{preset_df['Target Amount ₹'].sum():,.0f}")
    with c3: st.metric("Holdings", f"{len(preset_df)} stocks")
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1: replace = st.checkbox("Replace existing holdings", value=True)
    with c2: dry_run = st.checkbox("Preview only (don't save)", value=False)
    if st.button("🚀 LOAD PRESET PORTFOLIO", type="primary"):
        with st.spinner("Fetching live prices..."):
            preview = []
            for sym, name, tier, pct, amt in PREDEFINED_PORTFOLIO:
                price = fetch_current_price(sym)
                if price is None or price <= 0:
                    preview.append({'Symbol':sym,'Name':name,'Price ₹':'N/A','Qty':0,'Value ₹':0,'Note':'Fetch failed'})
                    continue
                qty = int(amt // price); av = qty * price
                preview.append({'Symbol':sym,'Name':name,'Price ₹':round(price,2),'Qty':qty,'Value ₹':round(av,0),'Note':f"{tier} @ {pct}%"})
            pdf = pd.DataFrame(preview)
            st.dataframe(pdf, use_container_width=True, hide_index=True)
            st.metric("Actual Invested (rounded)", f"₹{pdf['Value ₹'].sum():,.0f}")
            if not dry_run:
                with engine.connect() as conn:
                    if replace: conn.execute(text("DELETE FROM holdings"))
                    for row in preview:
                        if row['Qty'] > 0:
                            m = fetch_metrics(row['Symbol'])
                            w = float(row['Note'].split('@')[1].split('%')[0].strip()) if '@' in row['Note'] else 0
                            conn.execute(text("""INSERT INTO holdings (symbol,name,asset_type,quantity,avg_price,target_weight,sector,added_date)
                                                  VALUES (:s,:n,'Equity',:q,:p,:w,:sec,:d)"""),
                                         {'s':row['Symbol'],'n':m['name'],'q':row['Qty'],'p':row['Price ₹'],
                                          'w':w,'sec':get_sector(row['Symbol']),'d':now_ist().strftime('%Y-%m-%d')})
                    conn.commit()
                st.success("✓ Preset portfolio loaded"); st.cache_data.clear(); st.rerun()

# ==================== PAGE: BUILD ====================
elif menu == "➕ Build Portfolio":
    st.markdown('<h1 class="cyber-header">➕ Build Portfolio</h1>', unsafe_allow_html=True)
    render_status_bar()
    st.markdown('<div class="cyber-subheader">ADD EQUITY</div>', unsafe_allow_html=True)
    with st.form("add_s"):
        c1, c2 = st.columns(2)
        with c1: sel = st.selectbox("Select Stock", options=ALL_EQUITY)
        with c2: qty = st.number_input("Quantity", min_value=1, value=10, step=1)
        if st.form_submit_button("➕ ADD EQUITY", type="primary"):
            p = fetch_current_price(sel)
            if p is None: st.error(f"Could not fetch price for {sel}.")
            else:
                m = fetch_metrics(sel)
                with engine.connect() as conn:
                    conn.execute(text("""INSERT INTO holdings (symbol,name,asset_type,quantity,avg_price,sector,added_date)
                                          VALUES (:s,:n,'Equity',:q,:p,:sec,:d)"""),
                                 {'s':sel,'n':m['name'],'q':qty,'p':p,'sec':get_sector(sel),'d':now_ist().strftime('%Y-%m-%d')})
                    conn.commit()
                st.success(f"✓ Added {qty} × {sel} @ ₹{p:.2f}"); st.rerun()
    st.markdown('<div class="cyber-subheader">ADD DEBT</div>', unsafe_allow_html=True)
    with st.form("add_d"):
        c1, c2 = st.columns(2)
        with c1: dsel = st.selectbox("Instrument", options=list(DEBT_INSTRUMENTS.keys()))
        with c2: amt = st.number_input("Amount (₹)", min_value=1000, value=100000, step=10000)
        if st.form_submit_button("➕ ADD DEBT", type="primary"):
            with engine.connect() as conn:
                conn.execute(text("""INSERT INTO holdings (symbol,name,asset_type,quantity,avg_price,sector,added_date)
                                      VALUES (:s,:n,'Debt',1,:a,'Debt',:d)"""),
                             {'s':dsel,'n':dsel,'a':amt,'d':now_ist().strftime('%Y-%m-%d')})
                conn.commit()
            st.success(f"✓ Added {dsel} ₹{amt:,.0f}"); st.rerun()
    st.markdown('<div class="cyber-subheader">🥇 ADD GOLD / SILVER</div>', unsafe_allow_html=True)
    with st.form("add_commodity"):
        c1, c2 = st.columns(2)
        with c1: csel = st.selectbox("Commodity ETF", options=list(COMMODITY_ASSETS.keys()))
        with c2: camt = st.number_input("Amount (₹)", min_value=1000, value=50000, step=5000)
        if st.form_submit_button("➕ ADD COMMODITY", type="primary"):
            tick = COMMODITY_ASSETS[csel]['ticker']
            p = fetch_current_price(tick)
            if p is None or p <= 0:
                st.error(f"Could not fetch price for {tick}")
            else:
                qty_c = int(camt // p); av = qty_c * p
                with engine.connect() as conn:
                    conn.execute(text("""INSERT INTO holdings (symbol,name,asset_type,quantity,avg_price,sector,added_date)
                                          VALUES (:s,:n,'Equity',:q,:p,:sec,:d)"""),
                                 {'s':tick,'n':csel,'q':qty_c,'p':p,
                                  'sec':COMMODITY_ASSETS[csel]['type'].split()[0],
                                  'd':now_ist().strftime('%Y-%m-%d')})
                    conn.commit()
                st.success(f"✓ Added {qty_c} × {tick} @ ₹{p:.2f} (₹{av:,.0f})"); st.rerun()
    st.markdown('<div class="cyber-subheader">EDIT / REMOVE HOLDINGS</div>', unsafe_allow_html=True)
    if not holdings_df.empty:
        ed = holdings_df[['id','symbol','name','asset_type','quantity','avg_price','target_weight']].copy()
        ed['target_weight'] = ed['target_weight'].fillna(0); ed['Delete'] = False
        edited = st.data_editor(ed, use_container_width=True, hide_index=True, key='edit_v7',
            column_config={
                'id': st.column_config.NumberColumn('ID', disabled=True, width='small'),
                'symbol': st.column_config.TextColumn('Symbol', disabled=True, width='small'),
                'name': st.column_config.TextColumn('Name', disabled=True, width='medium'),
                'asset_type': st.column_config.TextColumn('Type', disabled=True, width='small'),
                'quantity': st.column_config.NumberColumn('Qty', min_value=0, step=1, format='%d'),
                'avg_price': st.column_config.NumberColumn('Avg ₹', min_value=0, step=0.01, format='%.2f'),
                'target_weight': st.column_config.NumberColumn('Target %', min_value=0, max_value=100, step=0.5, format='%.1f'),
                'Delete': st.column_config.CheckboxColumn('Del', default=False)})
        if st.button("💾 SAVE CHANGES", type="primary", use_container_width=True):
            with engine.connect() as conn:
                for _, r in edited.iterrows():
                    if r['Delete']:
                        conn.execute(text("DELETE FROM holdings WHERE id=:id"), {'id':int(r['id'])})
                    else:
                        conn.execute(text("UPDATE holdings SET quantity=:q,avg_price=:p,target_weight=:w WHERE id=:id"),
                                     {'q':float(r['quantity']) if pd.notna(r['quantity']) else 0,
                                      'p':float(r['avg_price']) if pd.notna(r['avg_price']) else 0,
                                      'w':float(r['target_weight']) if pd.notna(r['target_weight']) else 0,
                                      'id':int(r['id'])})
                conn.commit()
            st.cache_data.clear(); st.success("✓ Saved"); st.rerun()

# ==================== PAGE: PERFORMANCE ====================
elif menu == "📈 Performance":
    st.markdown('<h1 class="cyber-header">📈 Performance</h1>', unsafe_allow_html=True)
    render_status_bar()
    if holdings_df.empty: st.info("Build portfolio first.")
    else:
        st.markdown('<div class="cyber-subheader">TIME-WEIGHTED vs MONEY-WEIGHTED RETURN</div>', unsafe_allow_html=True)
        if len(snapshots_df) >= 2:
            twr = calc_twr(snapshots_df, cash_flows_df); mwr = calc_mwr(snapshots_df, cash_flows_df)
            c1, c2 = st.columns(2)
            with c1: st.metric("TWR (Strategy Return)", f"{twr:.2f}%" if twr is not None else "—")
            with c2: st.metric("MWR / XIRR (Personal Return)", f"{mwr:.2f}%" if mwr is not None else "—")
        else: st.info("Need 2+ days of history.")
        st.markdown('<div class="cyber-subheader">DAILY / WEEKLY / MONTHLY RETURNS</div>', unsafe_allow_html=True)
        rows = []
        for _, r in holdings_df.iterrows():
            if r['asset_type'] != 'Equity': continue
            h = fetch_price(r['symbol'], '1mo')
            if h is None or len(h) < 5: continue
            cur = h['Close'].iloc[-1]; y = h['Close'].iloc[-2]
            w = h['Close'].iloc[-6] if len(h) > 6 else h['Close'].iloc[0]
            mo = h['Close'].iloc[-21] if len(h) > 21 else h['Close'].iloc[0]
            rows.append({'Stock':r['symbol'],'LTP ₹':round(cur,2),'Day %':round((cur/y-1)*100,2),
                         'Week %':round((cur/w-1)*100,2),'Month %':round((cur/mo-1)*100,2)})
        if rows:
            df = pd.DataFrame(rows)
            def cr(v): return 'color:#059669' if isinstance(v,(int,float)) and v>=0 else 'color:#dc2626'
            st.dataframe(df.style.map(cr, subset=['Day %','Week %','Month %']), use_container_width=True, hide_index=True)

# ==================== PAGE: FORWARD TEST ====================
elif menu == "🧪 Forward Test":
    st.markdown('<h1 class="cyber-header">🧪 Forward Test</h1>', unsafe_allow_html=True)
    render_status_bar()
    with engine.connect() as conn:
        row = conn.execute(text("SELECT id,start_date,initial_capital,target_amount,horizon_years FROM forward_tests WHERE status='active' ORDER BY id DESC LIMIT 1")).fetchone()
    if row is None:
        if holdings_df.empty: st.warning("Add holdings first.")
        else:
            dcap = 0
            for _, h in holdings_df.iterrows():
                if h['asset_type']=='Equity': p = fetch_current_price(h['symbol']) or h['avg_price']
                else:
                    dh = (datetime.now()-pd.to_datetime(h['added_date'])).days
                    y = DEBT_INSTRUMENTS.get(h['symbol'],{}).get('yield',7.0); p = h['avg_price']*(1+y/100*dh/365)
                dcap += h['quantity']*p
            c1, c2, c3 = st.columns(3)
            with c1: ic = st.number_input("Initial Capital (₹)", value=int(dcap) if dcap>0 else 10000000, step=100000)
            with c2: ta = st.number_input("Target (₹)", value=17500000, step=100000)
            with c3: hy = st.number_input("Horizon (Years)", value=2.0, step=0.5)
            rc = ((ta/ic)**(1/hy)-1)*100
            st.markdown(f"**Required CAGR:** `{rc:.2f}%`")
            if rc > 25: st.warning("⚠ Very aggressive target.")
            if st.button("🚀 START FORWARD TEST", type="primary"):
                with engine.connect() as conn:
                    conn.execute(text("UPDATE forward_tests SET status='archived' WHERE status='active'"))
                    conn.execute(text("INSERT INTO forward_tests (start_date,initial_capital,target_amount,horizon_years,status) VALUES (:d,:i,:t,:h,'active')"),
                                 {'d':now_ist().strftime('%Y-%m-%d'),'i':float(ic),'t':float(ta),'h':float(hy)})
                    conn.commit()
                st.cache_data.clear(); st.rerun()
    else:
        ft_id, sds, ic, ta, hy = row
        sd = pd.to_datetime(sds); de = max((now_ist().replace(tzinfo=None)-sd).days, 0)
        td = max(int(hy*365), 1); dr = max(td-de, 0)
        ct = 0
        for _, h in holdings_df.iterrows():
            if h['asset_type']=='Equity': p = fetch_current_price(h['symbol']) or h['avg_price']
            else:
                dh = (datetime.now()-pd.to_datetime(h['added_date'])).days
                y = DEBT_INSTRUMENTS.get(h['symbol'],{}).get('yield',7.0); p = h['avg_price']*(1+y/100*dh/365)
            ct += h['quantity']*p
        cr_ = ((ct/ic)-1)*100 if ic > 0 else 0
        tp = min(ct/ta*100, 100) if ta > 0 else 0
        tmp = min(de/td*100, 100)
        ed = sd + pd.Timedelta(days=td)
        st.markdown(f'<div class="cyber-subheader">STARTED: {sd.strftime("%d %b %Y")} → TARGET: {ed.strftime("%d %b %Y")}</div>', unsafe_allow_html=True)
        st.caption(f"Day {de} of {td} • {dr} days remaining")
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f'<div class="glass-card"><div class="metric-label">INITIAL</div><div class="metric-value">₹{ic:,.0f}</div></div>', unsafe_allow_html=True)
        with c2:
            cls = "profit" if cr_ >= 0 else "loss"
            st.markdown(f'<div class="glass-card"><div class="metric-label">CURRENT</div><div class="metric-value {cls}">₹{ct:,.0f}</div><div class="metric-sub">{cr_:+.2f}%</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="glass-card"><div class="metric-label">TARGET</div><div class="metric-value">₹{ta:,.0f}</div><div class="metric-sub">{tp:.1f}% reached</div></div>', unsafe_allow_html=True)
        with c4: st.markdown(f'<div class="glass-card"><div class="metric-label">STILL NEEDED</div><div class="metric-value">₹{max(ta-ct,0):,.0f}</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="cyber-subheader">GOAL PROGRESS</div>', unsafe_allow_html=True)
        st.progress(tp/100); st.caption(f"₹{ct:,.0f} / ₹{ta:,.0f} ({tp:.1f}%)")
        st.markdown('<div class="cyber-subheader">TIME ELAPSED</div>', unsafe_allow_html=True)
        st.progress(tmp/100); st.caption(f"{de} / {td} days ({tmp:.1f}%)")
        if de > 0 and ic > 0:
            er = ((ta/ic)**(de/td) - 1)*100
            if cr_ >= er: st.success(f"✓ On track. Expected: {er:.2f}%. Actual: {cr_:.2f}%.")
            else: st.warning(f"⚠ Behind by {er-cr_:.2f}%. Expected: {er:.2f}%. Actual: {cr_:.2f}%.")
        if not snapshots_df.empty:
            fs = snapshots_df.copy(); fs['date'] = pd.to_datetime(fs['date'])
            fs = fs[fs['date'] >= sd]
            if not fs.empty:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=fs['date'], y=fs['portfolio_value'], name='Actual',
                                          line=dict(color='#6366f1', width=3),
                                          fill='tozeroy', fillcolor='rgba(99,102,241,0.08)'))
                tdates = pd.date_range(start=sd, end=ed, freq='D')
                n = len(tdates)
                if n > 1:
                    ratio = ta/ic if ic > 0 else 1
                    tvals = [ic*(ratio**(i/(n-1))) for i in range(n)]
                    fig.add_trace(go.Scatter(x=tdates, y=tvals, name='Target',
                                              line=dict(color='#a855f7', width=2, dash='dash')))
                fig.add_hline(y=ic, line_dash="dot", line_color="gray")
                fig.update_layout(template='plotly_white', height=500, paper_bgcolor='rgba(0,0,0,0)',
                                  plot_bgcolor='rgba(0,0,0,0)', xaxis_title="Date", yaxis_title="Value (₹)",
                                  font=dict(family='Inter', color='#4a4a6a'))
                st.plotly_chart(fig, use_container_width=True)

# ==================== PAGE: RISK ====================
elif menu == "🛡️ Risk Analysis":
    st.markdown('<h1 class="cyber-header">🛡 Risk Analysis</h1>', unsafe_allow_html=True)
    render_status_bar()
    if holdings_df.empty: st.info("Build portfolio first.")
    else:
        with st.spinner("Calculating risk metrics..."):
            pr, px_, w = calculate_portfolio_returns(holdings_df, '1y')
            if pr is not None:
                m = calculate_risk_metrics(pr)
                if m:
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.metric("Annualized Volatility", f"{m['Annualized Volatility %']}%")
                        st.metric("VaR 95% (Daily)", f"{m['VaR 95% %']}%")
                    with c2:
                        st.metric("CVaR 95% (Daily)", f"{m['CVaR 95% %']}%")
                        st.metric("Max Drawdown", f"{m['Max Drawdown %']}%")
                    with c3:
                        st.metric("Sharpe Ratio", m['Sharpe Ratio'])
                        st.metric("Sortino Ratio", m['Sortino Ratio'])
                    st.markdown("""
                    <div class="explainer">
                    <b>Methodology:</b><br>
                    • Volatility: Std Dev of daily returns × √252<br>
                    • VaR 95%: 5th percentile of daily returns<br>
                    • CVaR 95%: Average loss on days worse than VaR<br>
                    • Max Drawdown: Worst peak-to-trough decline<br>
                    • Sharpe: (Return − Risk-Free) / Volatility<br>
                    • Sortino: Like Sharpe but penalizes only downside
                    </div>""", unsafe_allow_html=True)
                if px_ is not None and len(px_.columns) > 1:
                    st.markdown('<div class="cyber-subheader">CORRELATION MATRIX</div>', unsafe_allow_html=True)
                    corr = px_.pct_change().dropna().corr()
                    fig = px.imshow(corr, text_auto='.2f', aspect='auto',
                                    color_continuous_scale=[[0,'#ef4444'],[0.5,'#ffffff'],[1,'#06b6d4']], zmin=-1, zmax=1)
                    fig.update_layout(height=500, template='plotly_white', paper_bgcolor='rgba(0,0,0,0)',
                                      font=dict(family='Inter', color='#4a4a6a'))
                    st.plotly_chart(fig, use_container_width=True)

# ==================== PAGE: BACKTEST ====================
elif menu == "📊 Backtest":
    st.markdown('<h1 class="cyber-header">📊 Backtest Engine</h1>', unsafe_allow_html=True)
    render_status_bar()
    st.markdown("""
    <div class="explainer">
    Simulate how a portfolio would have performed over a historical period using actual prices.
    Compares against Nifty 50 (^NSEI). Uses daily-rebalanced constant-weight assumption.
    </div>""", unsafe_allow_html=True)
    mode = st.radio("Backtest source", ["My Holdings", "Preset Portfolio", "Custom Selection"], horizontal=True)
    if mode == "My Holdings":
        sym_list = holdings_df[holdings_df['asset_type']=='Equity']['symbol'].tolist() if not holdings_df.empty else []
        wt_list = []
        if sym_list:
            eq = holdings_df[holdings_df['asset_type']=='Equity']
            total = (eq['quantity'] * eq['avg_price']).sum()
            for _, r in eq.iterrows():
                wt_list.append((r['quantity']*r['avg_price'])/total*100 if total > 0 else 0)
    elif mode == "Preset Portfolio":
        sym_list = [p[0] for p in PREDEFINED_PORTFOLIO]
        wt_list = [p[3] for p in PREDEFINED_PORTFOLIO]
    else:
        pick = st.multiselect("Select stocks", options=ALL_EQUITY, default=MIDCAP_STOCKS[:5] if MIDCAP_STOCKS else [])
        sym_list = pick; wt_list = [100/len(pick)]*len(pick) if pick else []
    c1, c2, c3 = st.columns(3)
    with c1: yrs = st.number_input("Years back", min_value=1, max_value=10, value=2, step=1)
    with c2: init = st.number_input("Initial investment ₹", min_value=10000, value=1000000, step=100000)
    with c3: run = st.button("▶ RUN BACKTEST", type="primary", use_container_width=True)
    if run and sym_list:
        with st.spinner(f"Running backtest on {len(sym_list)} stocks over {yrs} years..."):
            res = run_backtest(tuple(sym_list), tuple(wt_list), years=int(yrs), initial=float(init))
        if res is None: st.error("Could not fetch enough historical data.")
        elif isinstance(res, dict) and 'error' in res: st.error(f"Error: {res['error']}")
        else:
            c1, c2, c3, c4 = st.columns(4)
            with c1: st.metric("Final Value", f"₹{res['final_value']:,.0f}",
                                delta=f"{(res['final_value']/res['initial']-1)*100:+.1f}%")
            with c2: st.metric("CAGR", f"{res['cagr']:.2f}%")
            with c3: st.metric("Volatility", f"{res['vol']:.2f}%")
            with c4: st.metric("Max Drawdown", f"{res['max_dd']:.2f}%")
            st.metric("Sharpe Ratio", f"{res['sharpe']:.2f}")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=res['dates'], y=res['portfolio'], name='Portfolio',
                                      line=dict(color='#6366f1', width=3),
                                      fill='tozeroy', fillcolor='rgba(99,102,241,0.10)'))
            if res['benchmark'] is not None:
                fig.add_trace(go.Scatter(x=res['benchmark'].index, y=res['benchmark'].values,
                                          name='Nifty 50', line=dict(color='#a855f7', width=2, dash='dash')))
            fig.update_layout(template='plotly_white', height=500, paper_bgcolor='rgba(0,0,0,0)',
                              plot_bgcolor='rgba(0,0,0,0)', xaxis_title="Date", yaxis_title="Value (₹)",
                              font=dict(family='Inter', color='#4a4a6a'), hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)
            if res['benchmark'] is not None:
                port_ret = (res['final_value']/res['initial']-1)*100
                bench_ret = (res['benchmark'].iloc[-1]/res['initial']-1)*100
                diff = port_ret - bench_ret
                if diff > 0: st.success(f"✓ Portfolio outperformed Nifty 50 by {diff:.2f}%")
                else: st.warning(f"⚠ Portfolio underperformed Nifty 50 by {abs(diff):.2f}%")
    elif not sym_list: st.info("No stocks selected.")

# ==================== PAGE: SCENARIOS ====================
elif menu == "🔮 Scenarios":
    st.markdown('<h1 class="cyber-header">🔮 Future Scenarios</h1>', unsafe_allow_html=True)
    render_status_bar()
    if holdings_df.empty: st.info("Build portfolio first.")
    else:
        with st.spinner("Running 10,000 Monte Carlo simulations..."):
            pr, _, _ = calculate_portfolio_returns(holdings_df, '1y')
            if pr is not None:
                ar = pr.mean()*252; av = pr.std()*np.sqrt(252)
                init = (holdings_df['quantity']*holdings_df['avg_price']).sum()
                pct, paths = monte_carlo_projection(ar, av, 2, init)
                st.markdown(f"**Initial:** ₹{init:,.0f} | **Expected Return:** {ar*100:.1f}% | **Volatility:** {av*100:.1f}%")
                c1, c2, c3 = st.columns(3)
                with c1: st.markdown(f'<div class="glass-card"><div class="metric-label">P10 (BEAR)</div><div class="metric-value loss">₹{pct["P10 (Bear)"]:,.0f}</div><div class="metric-sub">Worst 10% scenarios</div></div>', unsafe_allow_html=True)
                with c2: st.markdown(f'<div class="glass-card"><div class="metric-label">P50 (BASE)</div><div class="metric-value">₹{pct["P50 (Base)"]:,.0f}</div><div class="metric-sub">Median outcome</div></div>', unsafe_allow_html=True)
                with c3: st.markdown(f'<div class="glass-card"><div class="metric-label">P90 (BULL)</div><div class="metric-value profit">₹{pct["P90 (Bull)"]:,.0f}</div><div class="metric-sub">Best 10% scenarios</div></div>', unsafe_allow_html=True)
                days = np.arange(paths.shape[0])
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=days, y=np.percentile(paths,90,axis=1), name='P90 Bull', line=dict(color='#10b981')))
                fig.add_trace(go.Scatter(x=days, y=np.percentile(paths,50,axis=1), name='P50 Base', line=dict(color='#6366f1', width=3)))
                fig.add_trace(go.Scatter(x=days, y=np.percentile(paths,10,axis=1), name='P10 Bear', line=dict(color='#ef4444'),
                                          fill='tonexty', fillcolor='rgba(99,102,241,0.08)'))
                fig.add_hline(y=17500000, line_dash="dot", line_color="#d97706", annotation_text="Target ₹1.75 Cr")
                fig.update_layout(template='plotly_white', height=500, paper_bgcolor='rgba(0,0,0,0)',
                                  plot_bgcolor='rgba(0,0,0,0)', font=dict(family='Inter', color='#4a4a6a'),
                                  xaxis_title="Trading Days", yaxis_title="Portfolio Value (₹)")
                st.plotly_chart(fig, use_container_width=True)
                prob = (paths[-1, :] >= 17500000).mean()*100
                st.markdown(f'<div class="cyber-subheader">PROBABILITY OF HITTING ₹1.75 CR: <span style="color:#6366f1;">{prob:.1f}%</span></div>', unsafe_allow_html=True)
                if prob < 30: st.warning("Low probability. Consider higher equity allocation or longer horizon.")
                elif prob < 60: st.info("Moderate probability. Stay disciplined with rebalancing.")
                else: st.success("Good probability. Your allocation is well-suited to the goal.")

# ==================== PAGE: SETTINGS ====================
elif menu == "⚙️ Settings":
    st.markdown('<h1 class="cyber-header">⚙ Settings</h1>', unsafe_allow_html=True)
    render_status_bar()
    st.markdown('<div class="cyber-subheader">DATA EXPORT</div>', unsafe_allow_html=True)
    if not holdings_df.empty:
        st.download_button("📥 HOLDINGS CSV", holdings_df.to_csv(index=False), "holdings.csv", "text/csv")
    if not snapshots_df.empty:
        st.download_button("📥 HISTORY CSV", snapshots_df.to_csv(index=False), "history.csv", "text/csv")
    st.markdown('<div class="cyber-subheader">UNIVERSE INFO</div>', unsafe_allow_html=True)
    st.markdown(f"""
    | Category | Count |
    |---|---|
    | 🟦 Large Cap | {len(LARGECAP_STOCKS)} |
    | 🟩 Mid Cap | {len(MIDCAP_STOCKS)} |
    | 🟧 Small Cap | {len(SMALLCAP_STOCKS)} |
    | 🥇 Gold / Silver | {len(COMMODITY_ASSETS)} |
    | 💰 Debt Instruments | {len(DEBT_INSTRUMENTS)} |
    | ⭐ Custom Added | {len(CUSTOM_SYMBOLS)} |
    | **Total Universe** | **{len(ALL_EQUITY)}** |
    """)
    st.markdown('<div class="cyber-subheader">⚠ DATA PERSISTENCE ON CLOUD</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="explainer">
    <b>Heads-up:</b> On Streamlit Community Cloud, the app's filesystem is temporary.
    Your portfolio data (holdings, snapshots) will be <b>reset when the app sleeps or redeploys</b>.<br><br>
    To keep your data permanently, export your holdings as CSV regularly (button above),
    or migrate to an external database like Supabase or Neon.
    </div>""", unsafe_allow_html=True)
    st.markdown('<div class="cyber-subheader">DANGER ZONE</div>', unsafe_allow_html=True)
    if st.button("🗑 CLEAR ALL DATA", type="secondary"):
        with engine.connect() as conn:
            for t in ['holdings','snapshots','cash_flows','forward_tests','custom_stocks']:
                conn.execute(text(f"DELETE FROM {t}"))
            conn.commit()
        st.cache_data.clear(); st.success("✓ Cleared"); st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("⚠ Educational tool only. Not investment advice.")