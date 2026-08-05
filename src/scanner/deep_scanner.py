from src.scanner.prescanner import load_universe, run_fast_prescan

def get_target_scan_candidates(mode: str) -> list[str]:
    symbols = load_universe()
    if not symbols:
        return []
    candidates = run_fast_prescan(symbols, top_n=30)
    return candidates
