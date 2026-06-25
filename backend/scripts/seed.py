from datetime import date, timedelta
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.database import Base, SessionLocal, engine
from app.models import (
    Book,
    Counterparty,
    Instrument,
    MarketPrice,
    Portfolio,
    QueryHistory,
    Settlement,
    Trade,
    User,
)


def seed() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        counterparties = [
            Counterparty(name="BNP Paribas", country="France", credit_rating="A+", sector="Bank"),
            Counterparty(name="Goldman Sachs", country="United States", credit_rating="A", sector="Bank"),
            Counterparty(name="Nomura International", country="Japan", credit_rating="A-", sector="Broker Dealer"),
            Counterparty(name="Qatar National Bank", country="Qatar", credit_rating="A", sector="Bank"),
            Counterparty(name="BlackRock Fund Advisors", country="United States", credit_rating="AA-", sector="Asset Manager"),
            Counterparty(name="Societe Generale", country="France", credit_rating="A", sector="Bank"),
        ]
        books = [
            Book(name="IR_EUR_SWAP", desk="Rates", region="EMEA"),
            Book(name="FX_G10_FORWARD", desk="FX", region="Global"),
            Book(name="EQ_INDEX_DELTA1", desk="Equities", region="EMEA"),
            Book(name="CR_CASH_BONDS", desk="Credit", region="EMEA"),
        ]
        portfolios = [
            Portfolio(name="Alpha Rates Carry", strategy="Rates Carry", base_currency="EUR"),
            Portfolio(name="Global FX Hedge", strategy="Currency Overlay", base_currency="USD"),
            Portfolio(name="Equity Index Flow", strategy="Client Flow", base_currency="EUR"),
            Portfolio(name="Credit Income", strategy="Investment Grade Credit", base_currency="USD"),
        ]
        instruments = [
            Instrument(symbol="EURIRS5Y", name="EUR 5Y Interest Rate Swap", asset_class="Rates", currency="EUR"),
            Instrument(symbol="USDJPY-FWD-1M", name="USD/JPY 1M FX Forward", asset_class="FX", currency="USD"),
            Instrument(symbol="SX5E-FUT-JUN26", name="Euro Stoxx 50 Future Jun 2026", asset_class="Equity", currency="EUR"),
            Instrument(symbol="FR001400Q5A2", name="French OAT 2034", asset_class="Bond", currency="EUR", maturity_date=date(2034, 5, 25)),
            Instrument(symbol="US91282CHT18", name="US Treasury 10Y", asset_class="Bond", currency="USD", maturity_date=date(2033, 11, 15)),
        ]
        users = [
            User(username="apatel", full_name="Ava Patel", role="Trader", desk="Rates"),
            User(username="mchen", full_name="Maya Chen", role="Trader", desk="FX"),
            User(username="enassar", full_name="Elias Nassar", role="Operations Analyst", desk="Operations"),
            User(username="orivera", full_name="Omar Rivera", role="Trade Support", desk="Equities"),
        ]
        db.add_all(counterparties + books + portfolios + instruments + users)
        db.flush()

        today = date.today()
        trades = [
            Trade(
                trade_id="TRD-2026-0001",
                instrument_id=instruments[0].id,
                counterparty_id=counterparties[0].id,
                book_id=books[0].id,
                portfolio_id=portfolios[0].id,
                booked_by_user_id=users[0].id,
                trade_date=today,
                settlement_date=today + timedelta(days=2),
                side="Buy",
                quantity=25_000_000,
                price=98.4512,
                notional=25_000_000,
                market_value=24_612_800,
                pnl=182_400,
                status="Pending Validation",
            ),
            Trade(
                trade_id="TRD-2026-0002",
                instrument_id=instruments[1].id,
                counterparty_id=counterparties[1].id,
                book_id=books[1].id,
                portfolio_id=portfolios[1].id,
                booked_by_user_id=users[1].id,
                trade_date=today,
                settlement_date=today + timedelta(days=1),
                side="Sell",
                quantity=18_000_000,
                price=157.82,
                notional=18_000_000,
                market_value=-18_120_500,
                pnl=-42_700,
                status="Validated",
            ),
            Trade(
                trade_id="TRD-2026-0003",
                instrument_id=instruments[2].id,
                counterparty_id=counterparties[4].id,
                book_id=books[2].id,
                portfolio_id=portfolios[2].id,
                booked_by_user_id=users[3].id,
                trade_date=today - timedelta(days=1),
                settlement_date=today + timedelta(days=2),
                side="Buy",
                quantity=2_500,
                price=5135.50,
                notional=12_838_750,
                market_value=12_910_250,
                pnl=71_500,
                status="Validated",
            ),
            Trade(
                trade_id="TRD-2026-0004",
                instrument_id=instruments[3].id,
                counterparty_id=counterparties[5].id,
                book_id=books[3].id,
                portfolio_id=portfolios[3].id,
                booked_by_user_id=users[0].id,
                trade_date=today - timedelta(days=3),
                settlement_date=today - timedelta(days=1),
                side="Buy",
                quantity=10_000_000,
                price=101.225,
                notional=10_122_500,
                market_value=10_084_000,
                pnl=-38_500,
                status="Pending Validation",
            ),
            Trade(
                trade_id="TRD-2026-0005",
                instrument_id=instruments[4].id,
                counterparty_id=counterparties[2].id,
                book_id=books[3].id,
                portfolio_id=portfolios[3].id,
                booked_by_user_id=users[0].id,
                trade_date=today - timedelta(days=5),
                settlement_date=today,
                side="Sell",
                quantity=15_000_000,
                price=96.875,
                notional=14_531_250,
                market_value=-14_480_000,
                pnl=51_250,
                status="Validated",
            ),
            Trade(
                trade_id="TRD-2026-0006",
                instrument_id=instruments[1].id,
                counterparty_id=counterparties[3].id,
                book_id=books[1].id,
                portfolio_id=portfolios[1].id,
                booked_by_user_id=users[1].id,
                trade_date=today - timedelta(days=7),
                settlement_date=today - timedelta(days=2),
                side="Buy",
                quantity=22_000_000,
                price=157.11,
                notional=22_000_000,
                market_value=22_145_900,
                pnl=145_900,
                status="Validated",
            ),
        ]
        db.add_all(trades)
        db.flush()

        settlements = [
            Settlement(trade_id=trades[0].id, counterparty_id=counterparties[0].id, settlement_date=trades[0].settlement_date, status="Pending", cash_amount=25_000_000, currency="EUR"),
            Settlement(trade_id=trades[1].id, counterparty_id=counterparties[1].id, settlement_date=trades[1].settlement_date, status="Matched", cash_amount=18_000_000, currency="USD"),
            Settlement(trade_id=trades[2].id, counterparty_id=counterparties[4].id, settlement_date=trades[2].settlement_date, status="Pending", cash_amount=12_838_750, currency="EUR"),
            Settlement(trade_id=trades[3].id, counterparty_id=counterparties[5].id, settlement_date=trades[3].settlement_date, status="Failed", cash_amount=10_122_500, currency="EUR", failure_reason="SSI mismatch"),
            Settlement(trade_id=trades[4].id, counterparty_id=counterparties[2].id, settlement_date=trades[4].settlement_date, status="Failed", cash_amount=14_531_250, currency="USD", failure_reason="Insufficient securities"),
            Settlement(trade_id=trades[5].id, counterparty_id=counterparties[3].id, settlement_date=trades[5].settlement_date, status="Settled", cash_amount=22_000_000, currency="USD"),
        ]
        prices = [
            MarketPrice(instrument_id=instruments[0].id, price_date=today, close_price=98.7312, source="Refinitiv"),
            MarketPrice(instrument_id=instruments[1].id, price_date=today, close_price=157.64, source="Bloomberg"),
            MarketPrice(instrument_id=instruments[2].id, price_date=today, close_price=5164.10, source="Eurex"),
            MarketPrice(instrument_id=instruments[3].id, price_date=today, close_price=100.84, source="Bloomberg"),
            MarketPrice(instrument_id=instruments[4].id, price_date=today, close_price=96.53, source="TreasuryDirect"),
        ]
        db.add_all(settlements + prices)
        db.query(QueryHistory).delete()
        db.commit()
        print("Seeded capital markets demo data.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
