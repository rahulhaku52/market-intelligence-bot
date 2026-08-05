def format_telegram_report(analysis: dict) -> str:
    ticker = analysis['ticker']
    plan = analysis['trade_plan']
    quote = analysis['quote']
    pos = analysis['position_size']
    explanation = analysis['explanation']
    calib = analysis['calibration']
    
    reasons_formatted = "\n".join([f"• {r}" for r in analysis.get('reasons', ['Multi-timeframe trend confluence', 'Support zone cluster alignment'])])
    
    report = (
        f"📈 <b>{ticker}</b> ({analysis['sector']})\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>Timeframe:</b> Daily / 1H Swing\n"
        f"<b>Bias:</b> {analysis['trend']} (Confluence Score: {analysis['setup_score']}/100)\n\n"
        f"🎯 <b>TRADE PLAN</b>\n"
        f"<b>Entry Zone:</b> {plan.entry_zone}\n"
        f"<b>Stop Loss:</b> ₹{plan.stoploss:.2f}\n"
        f"<b>Target 1 (TP1):</b> ₹{plan.tp1:.2f}\n"
        f"<b>Target 2 (TP2):</b> ₹{plan.tp2:.2f}\n"
        f"<b>Target 3 (TP3):</b> ₹{plan.tp3:.2f}\n"
        f"<b>Risk / Reward:</b> {plan.risk_reward:.2f}R\n"
        f"<b>Invalidation:</b> {plan.invalidation_text}\n\n"
        f"💰 <b>POSITION SIZING (₹5L Capital @ 1% Risk)</b>\n"
        f"• Max Qty: <b>{pos['max_quantity']} shares</b>\n"
        f"• Capital Req: <b>₹{pos['capital_required']:,.2f}</b>\n"
        f"• Max Risk: <b>₹{pos['max_loss']:,.2f}</b>\n\n"
        f"📝 <b>RATIONALE</b>\n"
        f"{explanation}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔎 <b>DATA INTEGRITY</b>\n"
        f"Price: ₹{quote.price:.2f}\n"
        f"Price Type: {quote.price_type}\n"
        f"Quote Age: {quote.age_seconds} sec\n"
        f"Validated Sources: {quote.sources_count}/2\n"
        f"Price Deviation: {quote.deviation_bps:.1f} bps\n"
        f"Data Quality: {quote.data_quality_score}/100\n\n"
        f"📊 <b>MODEL STATUS</b>\n"
        f"Setup Score: {analysis['setup_score']}/100\n"
        f"Historical Calibration: {calib}\n"
        f"Risk Level: {analysis['risk_level']}\n"
        f"R:R Quality: {plan.risk_reward:.2f}R\n"
        f"━━━━━━━━━━━━━━━━━━━━━━"
    )
    return report
