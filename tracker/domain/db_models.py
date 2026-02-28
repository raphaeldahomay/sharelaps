# db_models.py
from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import (
    Date,
    ForeignKey,
    String,
    UniqueConstraint,
    Index,
    Numeric,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# ----------------------------
# Base
# ----------------------------
class Base(DeclarativeBase):
    pass


# ----------------------------
# Tables
# ----------------------------
class PortfolioDB(Base):
    __tablename__ = "portfolios"

    # You used id: str in your dataclass, so keep it as a string primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(32), nullable=False)

    currency: Mapped[str] = mapped_column(String(8), nullable=False)      # "EUR", "USD", ...
    benchmark: Mapped[str] = mapped_column(String(32), nullable=False)    # "^GSPC", "SPY", ...
    created_at: Mapped[date] = mapped_column(Date, nullable=False)

    # Relationships
    positions: Mapped[list[PositionDB]] = relationship(
        back_populates="portfolio",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    snapshots: Mapped[list[PortfolioSnapshotDB]] = relationship(
        back_populates="portfolio",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class PositionDB(Base):
    __tablename__ = "positions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    portfolio_name: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("portfolios.name", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    ticker: Mapped[str] = mapped_column(String(16), nullable=False)
    shares: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)  # Decimal safe
    # This is a test db, but will have to handle the nullable=True
    # And retrieves the current mkt price in the future
    # Or retrieves the current date
    avg_buy_price: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    buy_date: Mapped[date] = mapped_column(Date, nullable=False)

    portfolio: Mapped[PortfolioDB] = relationship(back_populates="positions")

    # 1 ticker per portfolio (so you don't accidentally duplicate)
    __table_args__ = (
        UniqueConstraint("portfolio_name", "ticker", name="uq_positions_portfolio_ticker"),
        Index("ix_positions_portfolio_id_ticker", "portfolio_name", "ticker"),
    )


class PortfolioSnapshotDB(Base):
    __tablename__ = "portfolio_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    portfolio_name: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("portfolios.name", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    asof_date: Mapped[date] = mapped_column(Date, nullable=False)
    port_value: Mapped[Decimal] = mapped_column(Numeric(24, 8), nullable=False)
    benchmark_rel_value: Mapped[Decimal | None] = mapped_column(Numeric(24, 8), nullable=True)
    cash: Mapped[Decimal] = mapped_column(Numeric(20, 6), nullable=False, default=Decimal("0"))
    base_ccy: Mapped[str | None] = mapped_column(String(8), nullable=True)

    portfolio: Mapped[PortfolioDB] = relationship(back_populates="snapshots")

    tickers: Mapped[list[TickerSnapshotDB]] = relationship(
        back_populates="snapshot",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint("portfolio_name", "asof_date", name="uq_portfolio_snapshots_portfolio_date"),
        Index("ix_portfolio_snapshots_portfolio_date", "portfolio_name", "asof_date"),
    )


class TickerSnapshotDB(Base):
    __tablename__ = "ticker_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    snapshot_name: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("portfolio_snapshots.portfolio_name", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    ticker: Mapped[str] = mapped_column(String(16), nullable=False)

    shares: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(24, 8), nullable=False)  # in portfolio currency
    value: Mapped[Decimal] = mapped_column(Numeric(24, 8), nullable=False)  # shares * price
    fx_to_base: Mapped[Decimal] = mapped_column(Numeric(20, 10), nullable=False, default=Decimal("1"))

    snapshot: Mapped[PortfolioSnapshotDB] = relationship(back_populates="tickers")

    __table_args__ = (
        UniqueConstraint("snapshot_name", "ticker", name="uq_ticker_snapshots_snapshot_ticker"),
        Index("ix_ticker_snapshots_snapshot_ticker", "snapshot_name", "ticker"),
    )