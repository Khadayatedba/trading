import ta

def apply_indicators(df):

    close = df["Close"].squeeze()
    volume = df["Volume"].squeeze()

    # RSI
    df["RSI"] = ta.momentum.RSIIndicator(
        close
    ).rsi()

    # MACD
    macd = ta.trend.MACD(close)

    df["MACD"] = macd.macd()

    # EMA
    df["EMA20"] = ta.trend.EMAIndicator(
        close,
        window=20
    ).ema_indicator()

    df["EMA50"] = ta.trend.EMAIndicator(
        close,
        window=50
    ).ema_indicator()

    # Volume SMA
    df["Volume_SMA20"] = volume.rolling(
        20
    ).mean()

    df.dropna(inplace=True)

    return df
