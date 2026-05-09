Database: sc
User: scuser
Password: password

sudo mariadb -u scuser -p

TO DO
Create watchlist_history table
	date
	symbol
	price
	200dSMA
	50dSMA

Create update_watchlist python script
	gets current price (yfinance)
	calculates 200dSMA, 50dSMA using TA-lib
	inserts one row into watchlist_history for every record in watchlist
	schedule once/day run

Visualise watchlist activity and highlight GC using Streamlit
