from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from forex_python.converter import CurrencyRates

class FxProvider:
    def get_rate(self, from_ccy: str, to_ccy: str) -> Decimal:
        raise NotImplementedError

@dataclass
class CachedFxProvider(FxProvider):
    """
    Caches FX rates for the runtime to avoid repeated network calls.
    """
    _cr: CurrencyRates = CurrencyRates()
    _cache: dict[tuple[str, str], Decimal] = None

    def __post_init__(self):
        if self._cache is None:
            self._cache = {}

    def get_rate(self, from_ccy: str, to_ccy: str) -> Decimal:
        if from_ccy == to_ccy:
            return Decimal("1")
        key = (from_ccy, to_ccy)
        if key in self._cache:
            return self._cache[key]
        rate = self._cr.get_rate(from_ccy, to_ccy)
        d = Decimal(str(rate))
        self._cache[key] = d
        return d