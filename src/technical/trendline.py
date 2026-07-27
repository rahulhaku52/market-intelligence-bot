import numpy as np

def trendline_slope(series, last_n=10):
    """
    Calculate the slope of the linear trendline over the last N points.
    Returns a float: positive = uptrend, negative = downtrend.
    """
    if len(series) < last_n:
        return 0
    y = series[-last_n:].values
    x = np.arange(last_n)
    slope, _ = np.polyfit(x, y, 1)  # degree 1 polynomial
    return slope
