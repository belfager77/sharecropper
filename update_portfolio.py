#!/usr/bin/env python3
"""
Script to:
- Fetch current prices for all held symbols (sell_date IS NULL) using yfinance.
- Insert today's date, symbol, and price into portfolio_history.
- Update portfolio.price to the current price for each held row.
- Update portfolio.max_price to max(current_price, existing max_price) for each held row.
"""

import pymysql
import yfinance as yf
from datetime import date
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Database connection parameters
DB_CONFIG = {
    'host': 'localhost',
    'user': 'scuser',
    'password': 'password',
    'database': 'sc',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_db_connection():
    """Create and return a database connection."""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        logging.info("Connected to MariaDB database 'sc'")
        return conn
    except pymysql.MySQLError as e:
        logging.error(f"Database connection failed: {e}")
        raise

def get_held_symbols(conn):
    """
    Fetch unique symbol values from portfolio where sell_date IS NULL.
    These represent currently held positions.
    """
    sql = """
        SELECT DISTINCT symbol
        FROM portfolio
        WHERE sell_date IS NULL
          AND symbol IS NOT NULL
          AND symbol != ''
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            symbols = [row['symbol'] for row in rows]
            logging.info(f"Found {len(symbols)} unique held symbols: {symbols}")
            return symbols
    except pymysql.MySQLError as e:
        logging.error(f"Failed to fetch symbols: {e}")
        raise

def get_current_price(symbol):
    """
    Retrieve the current price for a given symbol using yfinance.
    Returns the latest closing price or None if unavailable.
    """
    try:
        ticker = yf.Ticker(symbol)
        # Get the most recent day's data
        hist = ticker.history(period="1d")
        if hist.empty:
            logging.warning(f"No price data found for symbol: {symbol}")
            return None
        current_price = hist['Close'].iloc[-1]
        return round(current_price, 2)
    except Exception as e:
        logging.error(f"Error fetching price for {symbol}: {e}")
        return None

def insert_portfolio_history(conn, symbol, price, trade_date):
    """Insert a record into the portfolio_history table."""
    sql = """
        INSERT INTO portfolio_history (trade_date, symbol, price)
        VALUES (%s, %s, %s)
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (trade_date, symbol, price))
        conn.commit()
        logging.info(f"Inserted history: {trade_date}, {symbol}, {price}")
    except pymysql.MySQLError as e:
        logging.error(f"Failed to insert history for {symbol}: {e}")
        conn.rollback()

def update_current_price(conn, symbol, current_price):
    """
    Update portfolio.price for all held rows of the given symbol to the current price.
    """
    sql = """
        UPDATE portfolio
        SET price = %s
        WHERE symbol = %s
          AND sell_date IS NULL
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (current_price, symbol))
            affected = cursor.rowcount
        conn.commit()
        if affected > 0:
            logging.info(f"Updated price for {symbol} to {current_price} - {affected} row(s)")
        else:
            logging.debug(f"No rows updated for {symbol} (no held positions?)")
    except pymysql.MySQLError as e:
        logging.error(f"Failed to update price for {symbol}: {e}")
        conn.rollback()

def update_max_price(conn, symbol, current_price):
    """
    Update portfolio.max_price for all held rows of the given symbol.
    Sets max_price = max(existing max_price, current_price).
    Handles NULL max_price by treating it as 0 (so it becomes current_price).
    """
    sql = """
        UPDATE portfolio
        SET max_price = GREATEST(COALESCE(max_price, 0), %s)
        WHERE symbol = %s
          AND sell_date IS NULL
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (current_price, symbol))
            affected = cursor.rowcount
        conn.commit()
        if affected > 0:
            logging.info(f"Updated max_price for {symbol} to {current_price} (if greater) - {affected} row(s)")
        else:
            logging.debug(f"No rows updated for {symbol} (no held positions?)")
    except pymysql.MySQLError as e:
        logging.error(f"Failed to update max_price for {symbol}: {e}")
        conn.rollback()

def main():
    """Main workflow: fetch held symbols, get prices, insert history, update price and max_price."""
    conn = None
    try:
        conn = get_db_connection()
        symbols = get_held_symbols(conn)

        if not symbols:
            logging.info("No held symbols found. Exiting.")
            return

        today = date.today()
        for symbol in symbols:
            current_price = get_current_price(symbol)
            if current_price is None:
                logging.warning(f"Skipping {symbol} due to missing price.")
                continue

            # 1. Insert into portfolio_history
            insert_portfolio_history(conn, symbol, current_price, today)

            # 2. Update portfolio.price with the current price
            update_current_price(conn, symbol, current_price)

            # 3. Update portfolio.max_price only if current price is greater
            update_max_price(conn, symbol, current_price)

    except Exception as e:
        logging.error(f"Script failed: {e}")
    finally:
        if conn:
            conn.close()
            logging.info("Database connection closed.")

if __name__ == "__main__":
    main()