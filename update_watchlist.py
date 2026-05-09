#!/usr/bin/env python3
"""
Script to update watchlist history with current prices and moving averages.
Connects to MariaDB 'sc', reads symbols from 'watchlist', fetches price data via yfinance,
calculates 50 and 200 day SMAs using TA-Lib, and inserts into 'watchlist_history'.

Uses PyMySQL for database connectivity.
"""

import datetime
import sys
import pymysql
from pymysql import MySQLError
import yfinance as yf
import talib
import numpy as np
import pandas as pd

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'sc',
    'user': 'scuser',
    'password': 'password',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor  # optional, can be removed if preferred
}

# Number of days of historical data needed for 200-day SMA (plus buffer)
HISTORY_DAYS = 250  # 200-day SMA + buffer

def get_db_connection():
    """Create and return a database connection using PyMySQL."""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        return conn
    except MySQLError as e:
        print(f"Error connecting to MariaDB: {e}")
        sys.exit(1)

def get_symbols(conn):
    """Fetch all symbols from watchlist table."""
    symbols = []
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT symbol FROM watchlist")
            rows = cursor.fetchall()
            # rows are tuples by default unless DictCursor is used
            symbols = [row['symbol'] for row in rows]
    except MySQLError as e:
        print(f"Error fetching symbols: {e}")
    return symbols

def get_price_and_smas(symbol):
    """
    Fetch current price and compute 50/200 day simple moving averages.
    Returns tuple (current_price, sma50, sma200) or (None, None, None) on failure.
    """
    try:
        # Download historical data (including today)
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=f"{HISTORY_DAYS}d")
        
        if hist.empty:
            print(f"No data found for symbol {symbol}")
            return None, None, None
        
        # Use 'Close' prices for SMA calculation
        close_prices = hist['Close'].values
        
        # Ensure enough data for 200-day SMA
        if len(close_prices) < 200:
            print(f"Not enough data for {symbol} (need 200 days, got {len(close_prices)})")
            return None, None, None
        
        # Calculate SMAs using TA-Lib (expects numpy array)
        sma50 = talib.SMA(close_prices, timeperiod=50)[-1]
        sma200 = talib.SMA(close_prices, timeperiod=200)[-1]
        
        # Current price is the last closing price
        current_price = close_prices[-1]
        
        # Convert numpy types to Python float for DB insertion
        return float(current_price), float(sma50), float(sma200)
    
    except Exception as e:
        print(f"Error processing {symbol}: {e}")
        return None, None, None

def insert_history(conn, symbol, current_price, sma50, sma200):
    """Insert a record into watchlist_history."""
    today = datetime.date.today()
    try:
        with conn.cursor() as cursor:
            insert_sql = """
                INSERT INTO watchlist_history 
                (trade_date, symbol, price, 50dma, 200dma)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (today, symbol, current_price, sma50, sma200))
            conn.commit()
            print(f"Inserted {symbol}: price={current_price}, MA50={sma50:.2f}, MA200={sma200:.2f}")
    except MySQLError as e:
        print(f"Error inserting {symbol}: {e}")
        conn.rollback()

def main():
    """Main execution flow."""
    conn = get_db_connection()
    try:
        symbols = get_symbols(conn)
        if not symbols:
            print("No symbols found in watchlist.")
            return
        
        print(f"Processing {len(symbols)} symbols...")
        for symbol in symbols:
            print(f"Fetching data for {symbol}...")
            current_price, sma50, sma200 = get_price_and_smas(symbol)
            if current_price is not None:
                insert_history(conn, symbol, current_price, sma50, sma200)
            else:
                print(f"Skipping {symbol} due to missing data.")
    finally:
        conn.close()
        print("Database connection closed.")

if __name__ == "__main__":
    main()
