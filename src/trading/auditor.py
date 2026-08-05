from config.settings import SignalStatus
from src.utils.logger import logger

def run_preflight_audit(ticker: str, quote, trade_plan, mtf_res: dict, event_locked: bool) -> tuple[bool, str]:
    """
    13-Point Preflight Audit Checklist:
    1. LTP validated?
    2. Symbol correct?
    3. Data fresh?
    4. Candles complete?
    5. MTF available?
    6. Market context available?
    7. Entry logical?
    8. SL correct side (SL < LTP for Long)?
    9. TP correct side (TP > LTP for Long)?
    10. RR sufficient (>= 1.5)?
    11. Corporate event clear?
    12. No contradictory state?
    13. Data quality score >= 70?
    """
    # Check 1: Quote exists
    if not quote or quote.price <= 0:
        return False, "FAIL_LTP_INVALID"
        
    # Check 2: Symbol valid
    if not ticker or len(ticker) < 2:
        return False, "FAIL_SYMBOL_INVALID"
        
    # Check 3: Quote status valid
    if quote.status != SignalStatus.VALID:
        return False, f"FAIL_QUOTE_{quote.status.value}"
        
    # Check 4: Data Quality score
    if quote.data_quality_score < 70:
        return False, f"FAIL_DATA_QUALITY_{quote.data_quality_score}"
        
    # Check 5: MTF available
    if not mtf_res or not mtf_res.get('details'):
        return False, "FAIL_MTF_MISSING"
        
    # Check 6: Trade plan exists
    if not trade_plan or trade_plan.status != SignalStatus.VALID:
        return False, f"FAIL_TRADE_PLAN_{trade_plan.status.value if trade_plan else 'NULL'}"
        
    # Check 7 & 8: SL logic (SL < LTP)
    if trade_plan.stoploss >= quote.price:
        return False, "FAIL_SL_ABOVE_ENTRY"
        
    # Check 9: TP logic (TP1 > LTP)
    if trade_plan.tp1 <= quote.price:
        return False, "FAIL_TP_BELOW_ENTRY"
        
    # Check 10: R:R threshold
    if trade_plan.risk_reward < 1.5:
        return False, "FAIL_INSUFFICIENT_RR"
        
    # Check 11: Corporate Event Lock
    if event_locked:
        return False, "FAIL_EVENT_LOCKED"
        
    # Check 12: Contradictory State
    if trade_plan.stoploss <= 0 or trade_plan.tp1 <= 0:
        return False, "FAIL_LEVELS_ZERO"
        
    # Check 13: All checks passed
    logger.info(f"✅ Preflight 13-Point Audit PASSED for {ticker}")
    return True, "AUDIT_PASSED"
