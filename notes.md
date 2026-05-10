Database: sc
User: scuser
Password: password

sudo mariadb -u scuser -p

TO DO
X Create watchlist_history table

Create update_watchlist python script
	schedule once/day run

Create golden_cross view

Visualise watchlist activity and highlight GC using Streamlit

X Create portfolio table

Create portfolio_history table
	trade_date (check? same as watchlist_history)
	symbol
	price

Create consolidated_portfolio view
	symbol
	avg_buy_price
	price
	pl_per
	pl_dol	

Create update_portfolio python script
	load current price into portfolio and portfolio history
	update max_price field on portfolio table

Create sell_recommendations view

Visualise portfolio activity with Streamlit
	portfolio status
	show sell recommendations

Scheduled job for daily database backup
