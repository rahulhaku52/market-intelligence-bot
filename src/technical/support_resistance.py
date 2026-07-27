import numpy as np

def find_levels(series, window=5, cluster_threshold=0.02):
    if len(series) < window * 2:
        return [], []

    prices = series.values  # numpy array
    maxima = []
    minima = []

    for i in range(window, len(prices) - window):
        # Check local max
        is_max = True
        for j in range(1, window + 1):
            if prices[i] < prices[i - j] or prices[i] < prices[i + j]:
                is_max = False
                break
        if is_max:
            maxima.append(prices[i])

        # Check local min
        is_min = True
        for j in range(1, window + 1):
            if prices[i] > prices[i - j] or prices[i] > prices[i + j]:
                is_min = False
                break
        if is_min:
            minima.append(prices[i])

    maxima = cluster_levels(maxima, cluster_threshold)
    minima = cluster_levels(minima, cluster_threshold)

    return minima, maxima  # supports, resistances

def cluster_levels(levels, threshold):
    if not levels:
        return []
    levels = sorted(set(levels))
    clustered = []
    current = levels[0]
    for lvl in levels[1:]:
        if lvl - current > threshold * current:
            clustered.append(current)
            current = lvl
    clustered.append(current)
    return clustered
