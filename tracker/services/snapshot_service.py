from __future__ import annotations
from datetime import date, datetime
from decimal import Decimal
import pandas as pd

from tracker.domain.models import Portfolio, PortfolioSnapshot, TickerSnapshot
from tracker.providers.yahoo_prices import YahooPriceProvider
from tracker.providers.fx import FxProvider
from tracker.utils.decimals import quantize_decimal
from tracker.utils.ticker_currency import infer_ticker_currency

def _ensure_date(d) -> date:
    if isinstance(d, datetime):
        return d.date()
    return d


def _get_latest_trading_date(history: pd.DataFrame, any_ticker: str) -> date:
    # history index differs depending on return shape; handle common yahooquery patterns
    if isinstance(history.index, pd.MultiIndex):
        dates = history.loc[any_ticker].index
        return _ensure_date(dates.max())
    return _ensure_date(history.index.max())


def _price_on_date(history: pd.DataFrame, ticker: str, d: date) -> Decimal | None:
    """
    Returns adjclose for a ticker at date d.
    If missing, returns None.
    """
    try:
        if isinstance(history.index, pd.MultiIndex):
            row = history.loc[(ticker, pd.Timestamp(d))]
            val = row["adjclose"]
        else:
            # less common shape
            val = history.loc[pd.Timestamp(d)]["adjclose"]
        # val can be scalar or series
        if hasattr(val, "iloc"):
            val = val.iloc[0]
        if pd.isna(val):
            return None
        return Decimal(str(val))
    except Exception:
        return None


def build_snapshots(
    portfolio: Portfolio,
    start: date,
    end: date | None,
    price_provider: YahooPriceProvider,
    fx: FxProvider,
    price_places: int = 4,
    value_places: int = 2,
) -> list[PortfolioSnapshot]:
    """
    Pure backend engine:
    - fetches prices (tickers + benchmark)
    - computes per-day portfolio snapshots in portfolio currency
    - computes benchmark_true_value and a relative benchmark series starting at port_value on first day
    """
    tickers = [p.ticker for p in portfolio.positions]
    if not tickers:
        return []

    # Fetch once
    hist = price_provider.history(tickers, start=start, end=end)
    if isinstance(hist, dict):
        raise RuntimeError("Price history fetch failed (yahooquery returned dict error).")

    bench_hist = price_provider.history([portfolio.benchmark], start=start, end=end)
    if isinstance(bench_hist, dict):
        raise RuntimeError("Benchmark history fetch failed (yahooquery returned dict error).")

    latest = _get_latest_trading_date(hist, tickers[0])

    # Build date range from available data rather than naive calendar days
    if isinstance(hist.index, pd.MultiIndex):
        date_index = hist.loc[tickers[0]].index
        dates = sorted({_ensure_date(d) for d in date_index})
    else:
        dates = sorted({_ensure_date(d) for d in hist.index})

    # If user passed end=None, keep all fetched dates up to latest
    dates = [d for d in dates if d <= latest]
    if end is not None:
        dates = [d for d in dates if d <= end]
    dates = [d for d in dates if d >= start]

    # Precompute FX rates per ticker currency (tiny optimization)
    # because suffix-based currency is constant per ticker
    ticker_ccy = {t: infer_ticker_currency(t) for t in tickers}
    fx_rate = {t: fx.get_rate(ticker_ccy[t], portfolio.currency) for t in tickers}

    # Benchmark is usually in USD, but you can extend this if needed
    bench_from = infer_ticker_currency(portfolio.benchmark)
    bench_fx = fx.get_rate(bench_from, portfolio.currency)

    snapshots: list[PortfolioSnapshot] = []

    first_bench_true = None
    first_port_value = None

    for d in dates:
        ticker_snaps: list[TickerSnapshot] = []
        total_value = Decimal("0")

        for pos in portfolio.positions:
            px = _price_on_date(hist, pos.ticker, d)
            if px is None:
                continue

            px_ccy = px * fx_rate[pos.ticker]
            px_ccy = quantize_decimal(px_ccy, price_places)

            val = px_ccy * pos.shares
            val = quantize_decimal(val, value_places)

            ticker_snaps.append(
                TickerSnapshot(
                    ticker=pos.ticker,
                    shares=pos.shares,
                    price=px_ccy,
                    value=val,
                )
            )
            total_value += val

        total_value = quantize_decimal(total_value, value_places)

        bench_px = _price_on_date(bench_hist, portfolio.benchmark, d)
        bench_true = None
        if bench_px is not None:
            bench_true = quantize_decimal(bench_px * bench_fx, price_places)

        snap = PortfolioSnapshot(
            portfolio_id=portfolio.id,
            asof_date=d,
            tickers=ticker_snaps,
            port_value=total_value,
            benchmark_rel_value=None,
        )

        # Benchmark relative series: start at port_value on first available day
        if first_port_value is None:
            first_port_value = total_value
            first_bench_true = bench_true

        if first_bench_true is not None and bench_true is not None and first_bench_true != 0:
            rate = (bench_true - first_bench_true) / first_bench_true
            snap.benchmark_rel_value = quantize_decimal(first_port_value * (Decimal("1") + rate), value_places)

        snapshots.append(snap)

    return snapshots