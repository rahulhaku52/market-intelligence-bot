import numpy as np

def find_levels(series, window=5, cluster_threshold=0.02):
    # Identify local maxima (resistance) and minima (support)
    maxima = []
    minima = []
    for i in range(window, len(series)-window):
        if all(series[i] >= series[i-j] for j in range(1, window+1)) and all(series[i] >= series[i+j] for j in range(1, window+1)):
            maxima.append(series[i])
        if all(series[i] <= series[i-j] for j in range(1, window+1)) and all(series[i] <= series[i+j] for j in range(1, window+1)):
            minima.append(series[i])
    # Cluster nearby levels
    maxima = cluster_levels(maxima, cluster_threshold)
    minima = cluster_levels(minima, cluster_threshold)
    return minima, maxima  # support (minima), resistance (maxima)

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