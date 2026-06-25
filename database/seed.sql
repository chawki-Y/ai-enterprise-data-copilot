INSERT INTO counterparties (name, country, credit_rating, sector) VALUES
('BNP Paribas', 'France', 'A+', 'Bank'),
('Goldman Sachs', 'United States', 'A', 'Bank'),
('Nomura International', 'Japan', 'A-', 'Broker Dealer'),
('Qatar National Bank', 'Qatar', 'A', 'Bank'),
('BlackRock Fund Advisors', 'United States', 'AA-', 'Asset Manager'),
('Societe Generale', 'France', 'A', 'Bank');

INSERT INTO books (name, desk, region) VALUES
('IR_EUR_SWAP', 'Rates', 'EMEA'),
('FX_G10_FORWARD', 'FX', 'Global'),
('EQ_INDEX_DELTA1', 'Equities', 'EMEA'),
('CR_CASH_BONDS', 'Credit', 'EMEA');

INSERT INTO portfolios (name, strategy, base_currency) VALUES
('Alpha Rates Carry', 'Rates Carry', 'EUR'),
('Global FX Hedge', 'Currency Overlay', 'USD'),
('Equity Index Flow', 'Client Flow', 'EUR'),
('Credit Income', 'Investment Grade Credit', 'USD');

INSERT INTO instruments (symbol, name, asset_class, currency, maturity_date) VALUES
('EURIRS5Y', 'EUR 5Y Interest Rate Swap', 'Rates', 'EUR', NULL),
('USDJPY-FWD-1M', 'USD/JPY 1M FX Forward', 'FX', 'USD', NULL),
('SX5E-FUT-JUN26', 'Euro Stoxx 50 Future Jun 2026', 'Equity', 'EUR', NULL),
('FR001400Q5A2', 'French OAT 2034', 'Bond', 'EUR', '2034-05-25'),
('US91282CHT18', 'US Treasury 10Y', 'Bond', 'USD', '2033-11-15');

INSERT INTO users (username, full_name, role, desk) VALUES
('apatel', 'Ava Patel', 'Trader', 'Rates'),
('mchen', 'Maya Chen', 'Trader', 'FX'),
('enassar', 'Elias Nassar', 'Operations Analyst', 'Operations'),
('orivera', 'Omar Rivera', 'Trade Support', 'Equities');

INSERT INTO trades (
    trade_id, instrument_id, counterparty_id, book_id, portfolio_id, booked_by_user_id,
    trade_date, settlement_date, side, quantity, price, notional, market_value, pnl, status
) VALUES
('TRD-2026-0001', 1, 1, 1, 1, 1, CURRENT_DATE, CURRENT_DATE + INTERVAL '2 days', 'Buy', 25000000, 98.4512, 25000000, 24612800, 182400, 'Pending Validation'),
('TRD-2026-0002', 2, 2, 2, 2, 2, CURRENT_DATE, CURRENT_DATE + INTERVAL '1 day', 'Sell', 18000000, 157.82, 18000000, -18120500, -42700, 'Validated'),
('TRD-2026-0003', 3, 5, 3, 3, 4, CURRENT_DATE - INTERVAL '1 day', CURRENT_DATE + INTERVAL '2 days', 'Buy', 2500, 5135.50, 12838750, 12910250, 71500, 'Validated'),
('TRD-2026-0004', 4, 6, 4, 4, 1, CURRENT_DATE - INTERVAL '3 days', CURRENT_DATE - INTERVAL '1 day', 'Buy', 10000000, 101.225, 10122500, 10084000, -38500, 'Pending Validation'),
('TRD-2026-0005', 5, 3, 4, 4, 1, CURRENT_DATE - INTERVAL '5 days', CURRENT_DATE, 'Sell', 15000000, 96.875, 14531250, -14480000, 51250, 'Validated'),
('TRD-2026-0006', 2, 4, 2, 2, 2, CURRENT_DATE - INTERVAL '7 days', CURRENT_DATE - INTERVAL '2 days', 'Buy', 22000000, 157.11, 22000000, 22145900, 145900, 'Validated');

INSERT INTO settlements (trade_id, counterparty_id, settlement_date, status, cash_amount, currency, failure_reason) VALUES
(1, 1, CURRENT_DATE + INTERVAL '2 days', 'Pending', 25000000, 'EUR', NULL),
(2, 2, CURRENT_DATE + INTERVAL '1 day', 'Matched', 18000000, 'USD', NULL),
(3, 5, CURRENT_DATE + INTERVAL '2 days', 'Pending', 12838750, 'EUR', NULL),
(4, 6, CURRENT_DATE - INTERVAL '1 day', 'Failed', 10122500, 'EUR', 'SSI mismatch'),
(5, 3, CURRENT_DATE, 'Failed', 14531250, 'USD', 'Insufficient securities'),
(6, 4, CURRENT_DATE - INTERVAL '2 days', 'Settled', 22000000, 'USD', NULL);

INSERT INTO market_prices (instrument_id, price_date, close_price, source) VALUES
(1, CURRENT_DATE, 98.7312, 'Refinitiv'),
(2, CURRENT_DATE, 157.64, 'Bloomberg'),
(3, CURRENT_DATE, 5164.10, 'Eurex'),
(4, CURRENT_DATE, 100.84, 'Bloomberg'),
(5, CURRENT_DATE, 96.53, 'TreasuryDirect');
