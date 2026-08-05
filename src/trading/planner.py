from config.settings import (
    MIN_RISK_REWARD_ACCEPTABLE, PREFERRED_RISK_REWARD, HIGH_QUALITY_RISK_REWARD, SignalStatus
)

class TradePlan:
    def __init__(self, entry_zone, stoploss, tp1, tp2, tp3, risk_reward, invalidation_text, status):
        self.entry_zone = entry_zone
        self.stoploss = stoploss
        self.tp1 = tp1
        self.tp2 = tp2
        self.tp3 = tp3
        self.risk_reward = risk_reward
        self.invalidation_text = invalidation_text
        self.status = status

def calculate_trade_plan(ltp: float, supports: list, resistances: list, atr_val: float, vix_multiplier: float = 1.0) -> TradePlan:
    if ltp <= 0 or atr_val <= 0:
        return TradePlan("N/A", 0, 0, 0, 0, 0.0, "Invalid Data", SignalStatus.INSUFFICIENT_DATA)
        
    # Structural StopLoss: Nearest support below LTP minus ATR buffer adjusted for India VIX
    if supports:
        nearest_support = supports[0]['center_price']
    else:
        nearest_support = ltp * 0.96
        
    atr_buffer = atr_val * 1.0 * vix_multiplier
    stoploss = round(max(nearest_support - atr_buffer, ltp * 0.90), 2)
    risk_per_share = ltp - stoploss
    
    if risk_per_share <= 0:
        return TradePlan("N/A", 0, 0, 0, 0, 0.0, "Invalid Risk Distance", SignalStatus.LOW_RR)

    # Targets (TP1, TP2, TP3)
    if resistances:
        tp1 = round(max(resistances[0]['center_price'], ltp + 1.5 * risk_per_share), 2)
        if len(resistances) >= 2:
            tp2 = round(max(resistances[1]['center_price'], ltp + 2.5 * risk_per_share), 2)
        else:
            tp2 = round(ltp + 2.5 * risk_per_share, 2)
        if len(resistances) >= 3:
            tp3 = round(max(resistances[2]['center_price'], ltp + 4.0 * risk_per_share), 2)
        else:
            tp3 = round(ltp + 4.0 * risk_per_share, 2)
    else:
        tp1 = round(ltp + 1.5 * risk_per_share, 2)
        tp2 = round(ltp + 2.5 * risk_per_share, 2)
        tp3 = round(ltp + 4.0 * risk_per_share, 2)

    # Path Obstruction & Feasibility Check
    reward_tp1 = tp1 - ltp
    rr_tp1 = round(reward_tp1 / risk_per_share, 2)
    
    if rr_tp1 < MIN_RISK_REWARD_ACCEPTABLE:
        return TradePlan(
            entry_zone=f"₹{ltp:.2f}",
            stoploss=stoploss,
            tp1=tp1, tp2=tp2, tp3=tp3,
            risk_reward=rr_tp1,
            invalidation_text=f"Close below ₹{stoploss:.2f}",
            status=SignalStatus.LOW_RR
        )
        
    entry_zone = f"₹{round(ltp * 0.995, 2):.2f} - ₹{round(ltp * 1.005, 2):.2f}"
    invalidation_text = f"Daily close below ₹{stoploss:.2f} (Structural Invalidation)"
    
    return TradePlan(
        entry_zone=entry_zone,
        stoploss=stoploss,
        tp1=tp1, tp2=tp2, tp3=tp3,
        risk_reward=rr_tp1,
        invalidation_text=invalidation_text,
        status=SignalStatus.VALID
    )
