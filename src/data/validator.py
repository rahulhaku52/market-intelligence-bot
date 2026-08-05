"""
General data validator to ensure data integrity across inputs.
"""
from config.settings import SignalStatus

def validate_data_pipeline(validated_quote, candles_dict) -> tuple[bool, SignalStatus]:
    if not validated_quote or validated_quote.status != SignalStatus.VALID:
        status = validated_quote.status if validated_quote else SignalStatus.DATA_REJECTED
        return False, status
        
    if not candles_dict or candles_dict.get('1D') is None or candles_dict.get('1W') is None:
        return False, SignalStatus.INSUFFICIENT_DATA
        
    return True, SignalStatus.VALID
