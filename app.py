import streamlit as st
import pandas as pd
from openai import OpenAI

from utils.screener import fetch_stock_data
from utils.charts import plot_chart
from utils.ai_engine import generate_ai_analysis


st.set_page_config(
    page_title="AI Stock Screener",
    layout="wide",
)

st.title("📈 AI-Based Stock Screener")
st.caption(
    "For educational and research purposes only. This is not investment advice. "
    "Verify all signals independently before trading."
)

# Required indicator columns produced by utils.screener.fetch_stock_data
REQUIRED_COLS = ["Close", "EMA20", "EMA50", "RSI", "Volume", "Volume_SMA20"]

# ----------------------------------------
# Sidebar
# ----------------------------------------
st.sidebar.header("Configuration")

api_key = st.sidebar.text_input(
    "OpenAI API Key (optional, for AI commentary)",
    type="password",
)

tickers_input = st.sidebar.text_area(
    "Enter NSE Stock Symbols (comma-separated)",
    value="RELIANCE.NS,TCS.NS,INFY.NS,HDFCBANK.NS",
)

period = st.sidebar.selectbox(
    "Select Historical Period",
    ["3mo", "6mo", "1y"],
    index=1,
)

include_ai = st.sidebar.checkbox(
    "Include AI written analysis",
    value=True,
    help="Requires OpenAI API key. Uncheck for technical-only screening.",
)

run_scan = st.sidebar.button("Run AI Screening")


# ----------------------------------------
# Cached data fetch
# ----------------------------------------
@st.cache_data(ttl=900, show_spinner=False)
def cached_fetch(symbol: str, period: str):
    """Wrap the loader so repeated clicks reuse the same data for 15 minutes."""
    return fetch_stock_data(symbol, period)


def classify(score: int) -> str:
    if score >= 80:
        return "STRONG BUY"
    if score >= 60:
        return "BUY"
    if score >= 40:
        return "HOLD"
    return "SELL"


def compute_score(latest: pd.Series) -> int:
    score = 0
    if latest["Close"] > latest["EMA50"]:
        score += 30  # Trend
    if latest["RSI"] > 55:
        score += 25  # Momentum
    if latest["Volume"] > latest["Volume_SMA20"]:
        score += 20  # Volume
    if latest["EMA20"] > latest["EMA50"]:
        score += 25  # EMA crossover
    return score


# ----------------------------------------
# Main Logic
# ----------------------------------------
if run_scan:
    client = None
    if include_ai:
        if not api_key:
            st.error(
                "AI commentary is enabled but no OpenAI API key was provided. "
                "Either add a key or uncheck 'Include AI written analysis'."
            )
            st.stop()
        client = OpenAI(api_key=api_key)

    tickers = [
        t.strip().upper()
        for t in tickers_input.split(",")
        if t.strip()
    ]

    if not tickers:
        st.warning("Please enter at least one ticker symbol.")
        st.stop()

    final_results = []

    progress = st.progress(0.0, text="Starting scan...")

    for i, symbol in enumerate(tickers, start=1):
        progress.progress(
            (i - 1) / len(tickers),
            text=f"Processing {symbol} ({i}/{len(tickers)})",
        )

        st.markdown("---")
        st.subheader(f"📊 {symbol}")

        try:
            df = cached_fetch(symbol, period)

            if df is None or df.empty:
                st.warning(f"No data found for {symbol}")
                continue

            missing = [c for c in REQUIRED_COLS if c not in df.columns]
            if missing:
                st.warning(
                    f"Skipping {symbol}: missing indicator columns {missing}. "
                    "Try a longer period."
                )
                continue

            # Drop rows where any indicator is still NaN (warm-up period)
            df_valid = df.dropna(subset=REQUIRED_COLS)
            if df_valid.empty:
                st.warning(
                    f"Not enough data to compute indicators for {symbol}. "
                    "Try a longer period."
                )
                continue

            latest = df_valid.iloc[-1]

            score = compute_score(latest)
            signal = classify(score)

            # ------------------------
            # Metrics
            # ------------------------
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Price", round(float(latest["Close"]), 2))
            c2.metric("RSI", round(float(latest["RSI"]), 2))
            c3.metric("AI Score", score)
            c4.metric("Signal", signal)

            # ------------------------
            # Chart
            # ------------------------
            plot_chart(df, symbol)

            # ------------------------
            # AI Analysis (optional)
            # ------------------------
            if include_ai and client is not None:
                with st.spinner(f"Generating AI analysis for {symbol}..."):
                    try:
                        ai_response = generate_ai_analysis(
                            client, symbol, latest
                        )
                        st.markdown("### 🤖 AI Analysis")
                        st.write(ai_response)
                    except Exception as e:
                        st.warning(
                            f"AI analysis failed for {symbol}: {e}"
                        )

            final_results.append(
                {
                    "Symbol": symbol,
                    "Price": round(float(latest["Close"]), 2),
                    "RSI": round(float(latest["RSI"]), 2),
                    "AI Score": score,
                    "Signal": signal,
                }
            )

        except Exception as e:
            st.error(f"Error processing {symbol}: {e}")

    progress.progress(1.0, text="Scan complete")

    # ----------------------------------------
    # Final Summary
    # ----------------------------------------
    if final_results:
        st.markdown("---")
        st.header("📋 Final Screening Results")
        result_df = (
            pd.DataFrame(final_results)
            .sort_values(by="AI Score", ascending=False)
            .reset_index(drop=True)
        )
        st.dataframe(result_df, use_container_width=True)
