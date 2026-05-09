# app.py
# AI-Based Stock Screener using Streamlit + OpenAI
# Run:
# pip install streamlit yfinance pandas ta openai plotly
# streamlit run app.py

import streamlit as st
import pandas as pd
import yfinance as yf
import ta
from openai import OpenAI
import plotly.graph_objects as go

st.set_page_config(page_title="AI Stock Screener", layout="wide")

st.title("📈 AI-Based Stock Screener")

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.header("Configuration")

api_key = st.sidebar.text_input(
    "Enter OpenAI API Key",
    type="password"
)

tickers_input = st.sidebar.text_area(
    "Enter Stock Symbols (comma separated)",
    value="RELIANCE.NS,TCS.NS,INFY.NS,HDFCBANK.NS"
)

period = st.sidebar.selectbox(
    "Select Period",
    ["3mo", "6mo", "1y"],
    index=1
)

run_scan = st.sidebar.button("Run AI Screening")

# -----------------------------
# AI Function
# -----------------------------
def get_ai_analysis(client, stock_data, symbol):

    latest = stock_data.iloc[-1]

    prompt = f"""
    Analyze this stock technically.

    Stock: {symbol}

    Current Price: {latest['Close']}
    RSI: {latest['RSI']}
    MACD: {latest['MACD']}
    Volume: {latest['Volume']}
    50 EMA: {latest['EMA50']}
    20 EMA: {latest['EMA20']}

    Give:
    1. Buy / Sell / Hold
    2. Short reasoning
    3. Risk level
    4. Momentum strength
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content

# -----------------------------
# Stock Data Function
# -----------------------------
def fetch_stock_data(symbol, period):

    df = yf.download(symbol, period=period)

    if df.empty:
        return None

    df.dropna(inplace=True)

    # Indicators
    df["RSI"] = ta.momentum.RSIIndicator(df["Close"]).rsi()

    macd = ta.trend.MACD(df["Close"])
    df["MACD"] = macd.macd()

    df["EMA20"] = ta.trend.EMAIndicator(
        df["Close"], window=20
    ).ema_indicator()

    df["EMA50"] = ta.trend.EMAIndicator(
        df["Close"], window=50
    ).ema_indicator()

    return df

# -----------------------------
# Main Logic
# -----------------------------
if run_scan:

    if not api_key:
        st.error("Please enter OpenAI API Key")
        st.stop()

    client = OpenAI(api_key=api_key)

    tickers = [
        t.strip().upper()
        for t in tickers_input.split(",")
    ]

    results = []

    for symbol in tickers:

        st.subheader(f"📊 {symbol}")

        try:

            df = fetch_stock_data(symbol, period)

            if df is None:
                st.warning(f"No data found for {symbol}")
                continue

            latest = df.iloc[-1]

            # Basic Conditions
            trend = (
                latest["Close"] > latest["EMA50"]
            )

            momentum = (
                latest["RSI"] > 55
            )

            volume_strength = (
                latest["Volume"] >
                df["Volume"].rolling(20).mean().iloc[-1]
            )

            score = 0

            if trend:
                score += 30

            if momentum:
                score += 30

            if volume_strength:
                score += 20

            if latest["EMA20"] > latest["EMA50"]:
                score += 20

            signal = "HOLD"

            if score >= 80:
                signal = "STRONG BUY"
            elif score >= 60:
                signal = "BUY"
            elif score < 40:
                signal = "SELL"

            # Display Metrics
            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Price", round(float(latest["Close"]), 2))
            col2.metric("RSI", round(float(latest["RSI"]), 2))
            col3.metric("AI Score", score)
            col4.metric("Signal", signal)

            # Chart
            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df["Close"],
                    mode='lines',
                    name='Close Price'
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df["EMA20"],
                    mode='lines',
                    name='EMA20'
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df["EMA50"],
                    mode='lines',
                    name='EMA50'
                )
            )

            fig.update_layout(
                height=400,
                title=f"{symbol} Price Chart"
            )

            st.plotly_chart(fig, use_container_width=True)

            # AI Analysis
            with st.spinner(f"Generating AI analysis for {symbol}..."):

                analysis = get_ai_analysis(
                    client,
                    df,
                    symbol
                )

            st.markdown("### 🤖 AI Analysis")
            st.write(analysis)

            results.append({
                "Symbol": symbol,
                "Price": round(float(latest["Close"]), 2),
                "RSI": round(float(latest["RSI"]), 2),
                "AI Score": score,
                "Signal": signal
            })

        except Exception as e:
            st.error(f"Error processing {symbol}: {e}")

    # Final Table
    if results:

        st.markdown("---")
        st.header("📋 Final Screening Results")

        results_df = pd.DataFrame(results)

        results_df = results_df.sort_values(
            by="AI Score",
            ascending=False
        )

        st.dataframe(
            results_df,
            use_container_width=True
        )
