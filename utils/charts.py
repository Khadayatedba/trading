"""Plotly candlestick + EMA chart for the screener."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def plot_chart(df: pd.DataFrame, symbol: str) -> None:
    fig = go.Figure()

    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Price",
        )
    )

    if "EMA20" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["EMA20"],
                mode="lines",
                name="EMA 20",
                line=dict(width=1.5),
            )
        )

    if "EMA50" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["EMA50"],
                mode="lines",
                name="EMA 50",
                line=dict(width=1.5),
            )
        )

    fig.update_layout(
        title=f"{symbol} — Price & EMAs",
        xaxis_rangeslider_visible=False,
        height=450,
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )

    st.plotly_chart(fig, use_container_width=True)
