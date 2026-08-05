from config.settings import DEFAULT_ACCOUNT_CAPITAL, DEFAULT_RISK_PER_TRADE_PCT

def calculate_position_size(entry: float, stoploss: float, capital: float = DEFAULT_ACCOUNT_CAPITAL, risk_pct: float = DEFAULT_RISK_PER_TRADE_PCT) -> dict:
    if entry <= 0 or stoploss <= 0 or entry <= stoploss:
        return {'risk_per_share': 0.0, 'max_quantity': 0, 'capital_required': 0.0, 'max_loss': 0.0}
        
    risk_per_share = entry - stoploss
    max_loss_allowed = capital * (risk_pct / 100.0)
    
    quantity = int(max_loss_allowed / risk_per_share)
    capital_required = round(quantity * entry, 2)
    max_loss = round(quantity * risk_per_share, 2)
    
    return {
        'risk_per_share': round(risk_per_share, 2),
        'max_quantity': quantity,
        'capital_required': capital_required,
        'max_loss': max_loss
    }
