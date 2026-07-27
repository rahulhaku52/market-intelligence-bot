def volume_score(df):
    if df.empty or 'Volume' not in df.columns:
        return 50
    vol = df['Volume']
    avg20 = vol.rolling(20).mean().iloc[-1]
    last_vol = vol.iloc[-1]
    ratio = last_vol / avg20 if avg20 > 0 else 1
    if ratio > 2.0:
        return 90   # strong volume confirmation
    elif ratio > 1.2:
        return 70
    elif ratio < 0.5:
        return 30   # very low volume
    else:
        return 50