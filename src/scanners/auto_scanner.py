import yfinance as yf
from src.utils.logger import logger

# Nifty 200 stocks (as of 2025). You never need to touch this.
NIFTY200 = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS",
    "ICICIBANK.NS", "KOTAKBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS",
    "LT.NS", "AXISBANK.NS", "SUNPHARMA.NS", "BAJFINANCE.NS", "MARUTI.NS",
    "TITAN.NS", "ASIANPAINT.NS", "HCLTECH.NS", "WIPRO.NS", "NESTLEIND.NS",
    "POWERGRID.NS", "ULTRACEMCO.NS", "M&M.NS", "NTPC.NS", "DRREDDY.NS",
    "BAJAJFINSV.NS", "JSWSTEEL.NS", "TATAMOTORS.NS", "ONGC.NS", "COALINDIA.NS",
    "HEROMOTOCO.NS", "IOC.NS", "SHREECEM.NS", "BRITANNIA.NS", "DIVISLAB.NS",
    "CIPLA.NS", "UPL.NS", "EICHERMOT.NS", "TATASTEEL.NS", "HDFCLIFE.NS",
    "GRASIM.NS", "SBILIFE.NS", "APOLLOHOSP.NS", "BAJAJ-AUTO.NS", "PIDILITIND.NS",
    "MARICO.NS", "DABUR.NS", "GODREJCP.NS", "COLPAL.NS", "BERGEPAINT.NS",
    "INDUSINDBK.NS", "HDFC.NS", "TATACONSUM.NS", "TECHM.NS", "BPCL.NS",
    "HAL.NS", "ADANIENT.NS", "ADANIPORTS.NS", "AMBUJACEM.NS", "ZOMATO.NS",
    "DMART.NS", "GODREJPROP.NS", "VEDL.NS", "PFC.NS", "RECLTD.NS",
    "ABCAPITAL.NS", "CANBK.NS", "SAIL.NS", "PNB.NS", "BANKBARODA.NS",
    "BHEL.NS", "HINDZINC.NS", "MUTHOOTFIN.NS", "ICICIPRULI.NS", "SRTRANSFIN.NS",
    "BIOCON.NS", "TORNTPHARM.NS", "LUPIN.NS", "AUROPHARMA.NS", "GLAND.NS",
    "ABBOTINDIA.NS", "SANOFI.NS", "PGHH.NS", "GILLETTE.NS", "VBL.NS",
    "HAVELLS.NS", "SIEMENS.NS", "ABB.NS", "CUMMINSIND.NS", "BEL.NS",
    "BHARATFORG.NS", "TRENT.NS", "TVSMOTOR.NS", "EIHOTEL.NS", "INDHOTEL.NS",
    "PAGEIND.NS", "KAJARIACER.NS", "ASTRAL.NS", "POLYCAB.NS", "VOLTAS.NS",
    "BLUESTARCO.NS", "WHIRLPOOL.NS", "IFBIND.NS", "JKCEMENT.NS", "RAMCOCEM.NS",
    "DALBHARAT.NS", "JKLAKSHMI.NS", "ESSAR-RE.NS"  # ignore delisted, just example
]

def get_symbols():
    """Return the universe of stocks to scan."""
    return NIFTY200

def fetch_volume_batch(symbols, period="1mo"):
    """Download daily volume for a list of symbols in one call."""
    try:
        df = yf.download(tickers=symbols, period=period, group_by='ticker', threads=True, progress=False)
        return df
    except Exception as e:
        logger.error(f"Batch volume fetch failed: {e}")
        return None

def scan_volume_spikes(batch_data, min_ratio=2.0, top_n=5):
    """Return top N tickers with unusual volume."""
    spikes = []
    if batch_data is None:
        return spikes
    for ticker in batch_data.columns.levels[0]:
        try:
            df = batch_data[ticker].dropna()
            if len(df) < 20:
                continue
            avg_vol = df['Volume'].rolling(20).mean().iloc[-1]
            last_vol = df['Volume'].iloc[-1]
            if avg_vol == 0:
                continue
            ratio = last_vol / avg_vol
            if ratio >= min_ratio:
                spikes.append((ticker, ratio))
        except Exception:
            continue
    spikes.sort(key=lambda x: x[1], reverse=True)
    return [s[0] for s in spikes[:top_n]]
