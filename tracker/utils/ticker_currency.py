def infer_ticker_currency(ticker: str) -> str:
    """
    Heuristic mapping based on common Yahoo ticker suffixes.
    Extend as needed.
    """
    suffix_map = {
        ".PA": "EUR", ".DE": "EUR", ".MI": "EUR", ".AS": "EUR", ".BR": "EUR",
        ".TO": "CAD",
        ".L": "GBP",
    }
    dot = ticker.rfind(".")
    if dot == -1:
        return "USD"
    return suffix_map.get(ticker[dot:], "USD")