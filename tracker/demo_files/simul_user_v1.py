from datetime import date
from decimal import Decimal

from tracker.domain.db_models import PortfolioDB, PositionDB
from tracker.demo_files.db import get_session


def new_user_first_port():

    session = get_session()

    action = input("hi there! What would you like to do: \
                   create a portfolio (1), update an existing portfolio (2)")
    
    if action == "1":
        infos = input("Enter your information in the same order indicated, separated with a comma:\
                      port_name, currency, benchmark:")
        
        infos_adj = [i.strip() for i in infos.split(",")]

        portfolio = PortfolioDB(
        name=infos_adj[0],
        currency=infos_adj[1],
        benchmark=infos_adj[2],
        created_at=date.today(),
        )

        session.add(portfolio)

        print(f"Perfect, your portfolio {infos_adj[0]} is now created.")

        pos = int(input("How many positions would you like to enter?:"))

        for _ in range(pos):

            pos_infos = input("Enter your position infos following the same order, separated with a comma:\
                              ticker, shares, Avg Buy Price")
            
            pos_infos_adj = [i.strip() for i in pos_infos.split(",")]

            position_ = PositionDB(
            portfolio_id=infos_adj[0], # check whether that one is mandatory or not
            ticker=pos_infos_adj[0],
            shares=Decimal(pos_infos_adj[1]),
            avg_buy_price=Decimal(pos_infos_adj[2]),
            buy_date=date.today() # Will have to develop the logic to convert str date into datetime date
            )

            session.add(position_)
        
        session.commit()

        print("congrats, your first portfolio is ready!")

        session.close()


if __name__ == "__main__":
    new_user_first_port()

