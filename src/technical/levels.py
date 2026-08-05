import numpy as np
import pandas as pd
from config.settings import LEVEL_CLUSTER_THRESHOLD

class LevelZone:
    def __init__(self, price_min, price_max, center_price, confluence_score, level_type, sources):
        self.price_min = price_min
        self.price_max = price_max
        self.center_price = center_price
        self.confluence_score = confluence_score
        self.level_type = level_type  # 'SUPPORT' or 'RESISTANCE'
        self.sources = sources        # List of source names

def cluster_price_levels(raw_levels: list[tuple[float, str]], threshold: float = LEVEL_CLUSTER_THRESHOLD) -> list[dict]:
    if not raw_levels:
        return []
        
    sorted_levels = sorted(raw_levels, key=lambda x: x[0])
    clusters = []
    
    current_group = [sorted_levels[0]]
    
    for level in sorted_levels[1:]:
        group_avg = sum(item[0] for item in current_group) / len(current_group)
        if abs(level[0] - group_avg) / group_avg <= threshold:
            current_group.append(level)
        else:
            clusters.append(current_group)
            current_group = [level]
    clusters.append(current_group)
    
    result_zones = []
    for grp in clusters:
        prices = [item[0] for item in grp]
        sources = [item[1] for item in grp]
        center = float(np.mean(prices))
        result_zones.append({
            'center_price': round(center, 2),
            'min_price': round(min(prices), 2),
            'max_price': round(max(prices), 2),
            'confluence': len(grp),
            'sources': list(set(sources))
        })
        
    return result_zones

def find_dynamic_levels(df_daily: pd.DataFrame, df_weekly: pd.DataFrame, ltp: float):
    """
    Computes all structural technical levels and clusters them relative to current LTP.
    Returns: (supports, resistances)
    """
    raw_levels = []
    
    if df_daily is not None and not df_daily.empty:
        # Prev Day High / Low / Close
        pd_high = float(df_daily['High'].iloc[-2]) if len(df_daily) >= 2 else float(df_daily['High'].iloc[-1])
        pd_low = float(df_daily['Low'].iloc[-2]) if len(df_daily) >= 2 else float(df_daily['Low'].iloc[-1])
        pd_close = float(df_daily['Close'].iloc[-2]) if len(df_daily) >= 2 else float(df_daily['Close'].iloc[-1])
        
        raw_levels.append((pd_high, 'Prev Day High'))
        raw_levels.append((pd_low, 'Prev Day Low'))
        
        # Pivot Points (Standard)
        pivot = (pd_high + pd_low + pd_close) / 3.0
        r1 = 2 * pivot - pd_low
        s1 = 2 * pivot - pd_high
        r2 = pivot + (pd_high - pd_low)
        s2 = pivot - (pd_high - pd_low)
        
        raw_levels.extend([(pivot, 'Pivot'), (r1, 'Pivot R1'), (s1, 'Pivot S1'), (r2, 'Pivot R2'), (s2, 'Pivot S2')])
        
        # 52W High / Low
        h52 = float(df_daily['High'].max())
        l52 = float(df_daily['Low'].min())
        raw_levels.append((h52, '52W High'))
        raw_levels.append((l52, '52W Low'))
        
        # Fibonacci Retracement on 52W range
        diff = h52 - l52
        if diff > 0:
            for fib in [0.236, 0.382, 0.500, 0.618, 0.786]:
                raw_levels.append((l52 + fib * diff, f'Fib {int(fib*100)}%'))
                
    if df_weekly is not None and not df_weekly.empty:
        pw_high = float(df_weekly['High'].iloc[-2]) if len(df_weekly) >= 2 else float(df_weekly['High'].iloc[-1])
        pw_low = float(df_weekly['Low'].iloc[-2]) if len(df_weekly) >= 2 else float(df_weekly['Low'].iloc[-1])
        raw_levels.append((pw_high, 'Prev Week High'))
        raw_levels.append((pw_low, 'Prev Week Low'))
        
    # Add Psychological Round Numbers near LTP
    round_base = 100.0 if ltp >= 1000 else (10.0 if ltp >= 100 else 1.0)
    round_below = np.floor(ltp / round_base) * round_base
    round_above = np.ceil(ltp / round_base) * round_base
    raw_levels.append((round_below, 'Psychological Round Number'))
    raw_levels.append((round_above, 'Psychological Round Number'))

    # Separate into raw supports (< LTP) and raw resistances (> LTP)
    raw_supports = [item for item in raw_levels if item[0] < ltp]
    raw_resistances = [item for item in raw_levels if item[0] > ltp]
    
    clustered_supports = cluster_price_levels(raw_supports)
    clustered_resistances = cluster_price_levels(raw_resistances)
    
    # Sort supports descending (closest to LTP first)
    supports = sorted(clustered_supports, key=lambda x: x['center_price'], reverse=True)
    # Sort resistances ascending (closest to LTP first)
    resistances = sorted(clustered_resistances, key=lambda x: x['center_price'])
    
    return supports[:3], resistances[:3]
