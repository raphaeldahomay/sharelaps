from __future__ import annotations
from datetime import date
from yahooquery import Ticker
import pandas as pd

class YahooPriceProvider:
    def history(self, tickers: list[str], start: str, end: str | None = None) -> pd.DataFrame:
        """
        Returns yahooquery history dataframe (often MultiIndex: (symbol, date)).
        """
        t = Ticker(tickers)
        return t.history(start=start, end=end)