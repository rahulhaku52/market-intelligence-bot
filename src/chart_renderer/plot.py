import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import mplfinance as mpf
from io import BytesIO
import pandas as pd

def generate_chart(df, ticker, support, resistance):
    if df is None or df.empty:
        return None
    df.index = pd.to_datetime(df.index)
    ema20 = df['Close'].ewm(span=20).mean()
    ema50 = df['Close'].ewm(span=50).mean()
    apds = [
        mpf.make_addplot(ema20, color='blue', width=0.8, label='EMA20'),
        mpf.make_addplot(ema50, color='red', width=0.8, label='EMA50')
    ]
    fig, axlist = mpf.plot(df, type='candle', style='charles', volume=True,
                           addplot=apds, returnfig=True,
                           title=f'{ticker} - {df.index[-1].strftime("%Y-%m-%d %H:%M")}',
                           ylabel='Price', ylabel_lower='Volume')
    axlist[0].axhline(y=support, color='g', linestyle='--', label='Support')
    axlist[0].axhline(y=resistance, color='r', linestyle='--', label='Resistance')
    axlist[0].legend()
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf