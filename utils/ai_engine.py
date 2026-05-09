def generate_ai_analysis(
    client,
    symbol,
    latest
):

    prompt = f"""
    Analyze this stock technically.

    Symbol: {symbol}

    Price: {latest['Close']}
    RSI: {latest['RSI']}
    MACD: {latest['MACD']}
    EMA20: {latest['EMA20']}
    EMA50: {latest['EMA50']}
    Volume: {latest['Volume']}

    Give:
    1. Buy/Sell/Hold
    2. Momentum analysis
    3. Risk level
    4. Short-term outlook
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
