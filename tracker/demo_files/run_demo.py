from datetime import date
from decimal import Decimal

from tracker.demo_files.db import init_db, get_session
from tracker.domain.db_models import PortfolioDB, PositionDB


def main():
    # 1️⃣ Make sure tables exist
    init_db()

    session = get_session()

    # 2️⃣ Create a portfolio
    portfolio = PortfolioDB(
        id="P_TEST",
        currency="EUR",
        benchmark="^GSPC",
        created_at=date.today(),
    )

    session.add(portfolio)

    # 3️⃣ Add positions
    position1 = PositionDB(
        portfolio_id="P_TEST",
        ticker="AAPL",
        shares=Decimal("2.5"),
    )

    position2 = PositionDB(
        portfolio_id="P_TEST",
        ticker="MSFT",
        shares=Decimal("1.0"),
    )

    session.add_all([position1, position2])

    # 4️⃣ Commit to database
    session.commit()

    # 5️⃣ Read back from DB
    loaded = session.query(PortfolioDB).filter_by(id="P_TEST").first()

    print("Portfolio loaded:")
    print("ID:", loaded.id)
    print("Currency:", loaded.currency)
    print("Benchmark:", loaded.benchmark)

    print("\nPositions:")
    for pos in loaded.positions:
        print("-", pos.ticker, pos.shares)

    session.close()


if __name__ == "__main__":
    main()