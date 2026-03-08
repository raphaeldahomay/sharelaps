from datetime import date
from decimal import Decimal

from tracker.domain.db_models import PortfolioDB, PositionDB, PortfolioSnapshotDB, TickerSnapshotDB
from tracker.demo_files.db import get_session
from sqlalchemy.exc import IntegrityError
import random
import time
from datetime import datetime
from tracker.demo_files.db import del_db
from tracker.demo_files.db import init_db


def testing_user_power_v2():

    loop = True

    while loop == True:
        session = get_session()

        action_1 = input("what to do: 1 (create port), 2 (delete all tables), \
        3 (init_db): ")
        
        if action_1 == "1":
            try:
                infos = input(
                    "Enter: port_name, currency, benchmark (comma-separated): "
                )
                name, currency, benchmark = [x.strip() for x in infos.split(",")]

                portfolio = PortfolioDB(
                    name=name,
                    currency=currency,
                    benchmark=benchmark,
                    created_at=date.today(),
                )

                session.add(portfolio)
                session.flush()  # <-- makes portfolio.id available (if autoincrement/uuid default is DB-side)

                n = int(input("How many positions?: "))

                init_port_value = 0

                for _ in range(n):
                    pos_infos = input("Enter: ticker, shares, avg_buy_price: ")
                    ticker, shares, avg_buy = [x.strip() for x in pos_infos.split(",")]

                    tick_val = Decimal(shares) * Decimal(random.uniform(1,200))
                    init_port_value += tick_val

                    session.add(
                        PositionDB(
                            portfolio_name=portfolio.name,  # ✅ correct FK
                            ticker=ticker.upper(),
                            shares=Decimal(shares),
                            avg_buy_price=Decimal(avg_buy),
                            buy_date=date.today(),
                        )
                    )

                    session.add(
                        TickerSnapshotDB(
                            snapshot_name=portfolio.name,
                            ticker=ticker.upper(),
                            shares=Decimal(shares),
                            price=Decimal(random.uniform(1,200)),
                            value=tick_val
                        )
                    )

                session.add(
                    PortfolioSnapshotDB(
                        portfolio_name=name,
                        asof_date=datetime.now(),
                        port_value=init_port_value,
                    )
                )

                session.commit()
                print(f"✅ Portfolio '{portfolio.name}' created with {n} positions.")
                session.close()

            except (ValueError, IntegrityError) as e:
                session.rollback()
                raise

        elif action_1 == "2":
            del_db()

        elif action_1 == "3":
            init_db()

        else:
            loop = False
            continue


if __name__ == "__main__":
    testing_user_power_v2()