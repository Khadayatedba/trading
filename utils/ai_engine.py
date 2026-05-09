"""LLM commentary on the latest snapshot of indicators for one ticker.

Uses the v1 OpenAI client (>=1.0) and a current model. Keeps prompts short
because we're calling this once per ticker.
"""

from __future__ import annotations

import pandas as pd
from openai import OpenAI


SYSTEM_PROMPT = (
    "You are a concise equity technical analyst. Given the latest indicator "
    "snapshot for a stock, write a 4-6 sentence assessment covering trend, "
    "momentum, volume confirmation, and a short-term outlook. End with a "
    "one-line caveat that this is not investment advice."
)


def generate_ai_analysis(
    client: OpenAI,
    symbol: str,
    latest: pd.Series,
    model: str = "gpt-4o-mini",
) -> str:
    user_prompt = (
        f"Symbol: {symbol}\n"
        f"Close: {float(latest['Close']):.2f}\n"
        f"EMA20: {float(latest['EMA20']):.2f}\n"
        f"EMA50: {float(latest['EMA50']):.2f}\n"
        f"RSI(14): {float(latest['RSI']):.2f}\n"
        f"Volume: {float(latest['Volume']):.0f}\n"
        f"Volume SMA20: {float(latest['Volume_SMA20']):.0f}\n"
        "\nProvide your analysis."
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.4,
        max_tokens=300,
    )

    return response.choices[0].message.content.strip()
