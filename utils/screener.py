"""
Stock data loader + technical indicators.

Implements EMA, RSI, and volume SMA without depending on `ta` (which is
broken on numpy>=2 because it imports numpy.NaN). Also flattens the
multi-index column structure that yfinance returns for single-ticker
downloads in newer versions.
"""

from __future__ import annotations

import pandas as pd
import yfinance as yf


def _flatten_columns(df: pd.DataFrame) -> pd.DataFrame:
    """yfinance >= 0.2.40 returns a MultiIndex (Price, Ticker) for downloads.
    Collapse it down to single-level columns: Open/High/Low/Close/Volume."""
    if isinstance(df.columns, pd.MultiIndex):
        df = df.copy()
        df.columns = df.columns.get_level_values(0)
    return df


def _ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False, min_periods=span).mean()


def _rsi(series: pd.Series, length: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    # Wilder's smoothing
    avg_gain = gain.ewm(alpha=1 / length, adjust=False, min_periods=length).mean()
    avg_loss = loss.ewm(alpha=1 / length, adjust=False, min_periods=length).mean()
    rs = avg_gain / avg_loss.replace(0, pd.NA)
    rsi = 100 - (100 / (1 + rs))
    return rsi.astype("float64")


def fetch_stock_data(symbol: str, period: str) -> pd.DataFrame | None:
    """Download OHLCV from Yahoo Finance and append technical indicators.

    Returns None if the download is empty.
    """
    try:
        df = yf.download(
            symbol,
            period=period,
            interval="1d",
            auto_adjust=True,
            progress=False,
            threads=False,
        )
    except Exception:
        return None

    if df is None or df.empty:
        return None

    df = _flatten_columns(df)

    # Sanity check
    needed = {"Close", "Volume"}
    if not needed.issubset(df.columns):
        return None

    df["EMA20"] = _ema(df["Close"], 20)
    df["EMA50"] = _ema(df["Close"], 50)
    df["RSI"] = _rsi(df["Close"], 14)
    df["Volume_SMA20"] = df["Volume"].rolling(window=20, min_periods=20).mean()

    return df
