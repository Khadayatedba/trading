import yfinance as yf
import pandas as pd
from utils.indicators import apply_indicators

def fetch_stock_data(symbol, period):

    df = yf.download(
        symbol,
        period=period,
        auto_adjust=True,
        progress=False,
        threads=False
    )

    if df.empty:
        return None

    df = df.copy()

    # Flatten MultiIndex if exists
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = apply_indicators(df)

    return df
