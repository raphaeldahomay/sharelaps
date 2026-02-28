from __future__ import annotations # It allows type hints to reference classes that are not yet fully defined
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

@dataclass(frozen=True)
class Position:
    ticker: str
    shares: Decimal

@dataclass(frozen=True)
class Portfolio:
    id: str
    currency: str            # "EUR", "USD", "CAD", ...
    benchmark: str           # e.g. "^GSPC" or "SPY"
    positions: list[Position]
    created_at: date

@dataclass
class TickerSnapshot:
    ticker: str
    shares: Decimal
    price: Decimal           # in portfolio currency
    value: Decimal           # shares * price

@dataclass
class PortfolioSnapshot:
    portfolio_id: str
    date: date
    tickers: list[TickerSnapshot]
    port_value: Decimal
    benchmark_true_value: Decimal | None = None
    benchmark_rel_value: Decimal | None = None