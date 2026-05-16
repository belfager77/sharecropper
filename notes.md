Database: sc
User: scuser
Password: password

sudo mariadb -u scuser -p

TO DO
X Create watchlist_history table

Create update_watchlist python script
	schedule once/day run

X Create golden_cross view

Visualise watchlist activity and highlight GC using Streamlit
	Fix this error:
	Please replace `use_container_width` with `width`

X Create portfolio table

X Create portfolio_history table

X Modify portfolio_history table to show share values and add portfolio name

X Create consolidated_portfolio view

Create update_portfolio python script
	schedule once/day run

X Create sell_recommendations view

Scheduled job for daily database backup
