"""
Global settings, constants, and status codes for the 30-Layer Indian Market Engine.
"""
from enum import Enum

class SignalStatus(str, Enum):
    VALID = "VALID"
    NO_TRADE = "NO_TRADE"
    DATA_REJECTED = "DATA_REJECTED"
    STALE_PRICE = "STALE_PRICE"
    SOURCE_MISMATCH = "SOURCE_MISMATCH"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    EVENT_LOCK = "EVENT_LOCK"
    LOW_RR = "LOW_RR"
    AUDIT_FAILED = "AUDIT_FAILED"
    DUPLICATE_SIGNAL = "DUPLICATE_SIGNAL"

class SessionState(str, Enum):
    PRE_MARKET = "PRE_MARKET"
    REGULAR = "REGULAR"
    POST_MARKET = "POST_MARKET"
    CLOSED = "CLOSED"
    HOLIDAY = "HOLIDAY"

# Thresholds
MIN_RISK_REWARD_ACCEPTABLE = 1.5
PREFERRED_RISK_REWARD = 2.0
HIGH_QUALITY_RISK_REWARD = 2.5

MAX_ALLOWED_PRICE_DEVIATION_BPS = 50.0  # 0.5% max price deviation between feeds
STALE_QUOTE_THRESHOLD_SECONDS = 300     # 5 minutes max age during REGULAR session
LEVEL_CLUSTER_THRESHOLD = 0.003          # 0.3% zone clustering threshold

DEFAULT_ACCOUNT_CAPITAL = 500000.0       # INR 5 Lakhs default for position sizing
DEFAULT_RISK_PER_TRADE_PCT = 1.0        # 1% risk per trade
