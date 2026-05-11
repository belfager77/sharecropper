#!/usr/bin/env python3

import mysql.connector
import yfinance as yf
from datetime import date
from decimal import Decimal

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "scuser",
    "password": "password",
    "database": "sc"
}


def get_current_price(symbol):
    """
    Retrieve the current stock price using yfinance.
    """
    try:
        ticker = yf.Ticker(symbol)

        # Try fast_info first
        current_price = ticker.fast_info.get("lastPrice")

        # Fallback to history if needed
        if current_price is None:
            hist = ticker.history(period="1d")
            if not hist.empty:
                current_price = hist["Close"].iloc[-1]

        if current_price is not None:
            return round(float(current_price), 2)

    except Exception as e:
        print(f"Error retrieving price for {symbol}: {e}")

    return None


def update_portfolio_prices(cursor, conn):
    """
    Update current prices and max prices for open positions.
    """

    query = """
        SELECT name, symbol, price, max_price
        FROM portfolio
        WHERE sell_date IS NULL
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    for row in rows:
        name, symbol, old_price, max_price = row

        current_price = get_current_price(symbol)

        if current_price is None:
            print(f"Skipping {symbol} - no price found")
            continue

        print(f"Updating {symbol}: {old_price} -> {current_price}")

        # Update price
        update_query = """
            UPDATE portfolio
            SET price = %s
            WHERE name = %s
              AND symbol = %s
              AND sell_date IS NULL
        """

        cursor.execute(update_query, (
            current_price,
            name,
            symbol
        ))

        # Update max_price if current price is higher
        if max_price is None or Decimal(str(current_price)) > max_price:

            max_update_query = """
                UPDATE portfolio
                SET max_price = %s
                WHERE name = %s
                  AND symbol = %s
                  AND sell_date IS NULL
            """

            cursor.execute(max_update_query, (
                current_price,
                name,
                symbol
            ))

            print(f"Updated max_price for {symbol} to {current_price}")

    conn.commit()


def insert_portfolio_history(cursor, conn):
    """
    Insert daily portfolio history records.
    """

    query = """
        SELECT
            name,
            symbol,
            SUM(quantity) AS total_quantity
        FROM portfolio
        GROUP BY name, symbol
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    today = date.today()

    for row in rows:
        name, symbol, total_quantity = row

        current_price = get_current_price(symbol)

        if current_price is None:
            print(f"Skipping history insert for {symbol} - no price found")
            continue

        value = round(float(total_quantity) * current_price, 2)

        insert_query = """
            INSERT INTO portfolio_history
            (
                trade_date,
                name,
                symbol,
                price,
                value
            )
            VALUES (%s, %s, %s, %s, %s)
        """

        cursor.execute(insert_query, (
            today,
            name,
            symbol,
            current_price,
            value
        ))

        print(
            f"Inserted history: "
            f"{today}, {name}, {symbol}, "
            f"price={current_price}, value={value}"
        )

    conn.commit()


def main():

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        print("Connected to database")

        # Step 1-3
        update_portfolio_prices(cursor, conn)

        # Step 4
        insert_portfolio_history(cursor, conn)

        print("Processing completed successfully")

    except mysql.connector.Error as err:
        print(f"Database error: {err}")

    except Exception as e:
        print(f"Unexpected error: {e}")

    finally:
        try:
            cursor.close()
            conn.close()
            print("Database connection closed")
        except:
            pass


if __name__ == "__main__":
    main()