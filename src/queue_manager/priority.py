def sort_by_priority(signals):
    # signals is list of dicts with 'priority' key
    return sorted(signals, key=lambda x: x['priority'], reverse=True)