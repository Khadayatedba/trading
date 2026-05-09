import streamlit as st
import pandas as pd
from openai import OpenAI

from utils.screener import fetch_stock_data
from utils.ai_engine import generate_ai_analysis
from utils.charts import plot_chart

st.set_page_config(
    page_title="AI Stock Screener",
    layout="wide"
)

st.title("📈 AI-Based Stock Screener")

# ----------------------------------
# Sidebar
# ----------------------------------

st.sidebar.header("Settings")

api_key = st.sidebar.text_input(
    "OpenAI API Key",
    type="password"
)

tickers_input = st.sidebar.text_area(
    "Stock Symbols",
    value="RELIANCE.NS,TCS.NS,INFY.NS,HDFCBANK.NS"
)

period = st.sidebar.selectbox(
    "Historical Period",
    ["3mo", "6mo", "1y"],
    index=1
)

run_scan = st.sidebar.button("Run AI Scan")

# ----------------------------------
# Main
# ----------------------------------

if run_scan:

    if not api_key:
        st.error("Please enter OpenAI API Key")
        st.stop()

    client = OpenAI(api_key=api_key)

    tickers = [
        x.strip().upper()
        for x in tickers_input.split(",")
    ]

    final_results = []

    for symbol in tickers:

        st.markdown("---")
        st.subheader(f"📊 {symbol}")

        try:

            df = fetch_stock_data(symbol, period)

            if df is None or df.empty:
                st.warning(f"No data for {symbol}")
                continue

            latest = df.iloc[-1]

            score = 0

            if latest["Close"] > latest["EMA50"]:
                score += 30

            if latest["RSI"] > 55:
                score += 25

            if latest["Volume"] > latest["Volume_SMA20"]:
                score += 20

            if latest["EMA20"] > latest["EMA50"]:
                score += 25

            if score >= 80:
                signal = "STRONG BUY"
            elif score >= 60:
                signal = "BUY"
            elif score >= 40:
                signal = "HOLD"
            else:
                signal = "SELL"

            # Metrics
            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                "Price",
                round(float(latest["Close"]), 2)
            )

            c2.metric(
                "RSI",
                round(float(latest["RSI"]), 2)
            )

            c3.metric(
                "AI Score",
                score
            )

            c4.metric(
                "Signal",
                signal
            )

            # Chart
            plot_chart(df, symbol)

            # AI Analysis
            with st.spinner("Generating AI analysis..."):

                ai_text = generate_ai_analysis(
                    client,
                    symbol,
                    latest
                )

            st.markdown("### 🤖 AI Analysis")
            st.write(ai_text)

            final_results.append({
                "Symbol": symbol,
                "Price": round(float(latest["Close"]), 2),
                "RSI": round(float(latest["RSI"]), 2),
                "AI Score": score,
                "Signal": signal
            })

        except Exception as e:
            st.error(f"Error processing {symbol}: {e}")

    # Summary Table
    if final_results:

        st.markdown("---")
        st.header("📋 Screening Summary")

        result_df = pd.DataFrame(final_results)

        result_df = result_df.sort_values(
            by="AI Score",
            ascending=False
        )

        st.dataframe(
        result_df,
        width="stretch"
        )
        )
