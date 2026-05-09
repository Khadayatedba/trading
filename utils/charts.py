import plotly.graph_objects as go
import streamlit as st

def plot_chart(df, symbol):

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["Close"],
            mode="lines",
            name="Close"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["EMA20"],
            mode="lines",
            name="EMA20"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["EMA50"],
            mode="lines",
            name="EMA50"
        )
    )

    fig.update_layout(
        title=f"{symbol} Chart",
        height=450
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )
