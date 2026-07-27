import numpy as np
from sklearn.linear_model import LinearRegression
# সরল ট্রেন্ডলাইন: last N points use করে slope বের করা
def trendline_slope(prices, last_n=10):
    if len(prices) < last_n: return 0
    y = prices[-last_n:].values.reshape(-1,1)
    x = np.arange(last_n).reshape(-1,1)
    model = LinearRegression().fit(x, y)
    return model.coef_[0][0]