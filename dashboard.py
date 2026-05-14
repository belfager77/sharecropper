import pymysql
import pandas as pd
import streamlit as st
import plotly.express as px

DB_CONFIG = {
    'host': 'localhost',
    'database': 'sc',
    'user': 'scuser',
    'password': 'password',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
}


def get_df(sql):
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
        return pd.DataFrame(rows)
    finally:
        conn.close()


st.set_page_config(page_title="Sharecropper", layout="wide")

# --- Portfolio Live ---
st.header("Portfolio")
portfolio_live = get_df("SELECT * FROM portfolio_live")
if not portfolio_live.empty:
    st.dataframe(
        portfolio_live,
        column_config={
            "buy_value": st.column_config.NumberColumn("Buy Value", format="$%.2f"),
            "value": st.column_config.NumberColumn("Value", format="$%.2f"),
            "buy_price": st.column_config.NumberColumn("Buy Price", format="$%.2f"),
            "profit_and_loss": st.column_config.NumberColumn("P&L", format="$%.2f"),
            "percentage_return": st.column_config.NumberColumn("Return %", format="%.2f%%"),
        },
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No portfolio data.")

# --- Portfolio History Chart ---
st.header("Portfolio History")
portfolio_history = get_df(
    "SELECT trade_date, name, SUM(value) as value "
    "FROM portfolio_history GROUP BY trade_date, name ORDER BY trade_date"
)
if not portfolio_history.empty:
    names = sorted(portfolio_history["name"].unique())
    selected_name = st.selectbox("Select holding", names, key="ph_name")
    filtered = portfolio_history[portfolio_history["name"] == selected_name]
    fig = px.line(filtered, x="trade_date", y="value", labels={"trade_date": "", "value": "Portfolio Value"})
    fig.update_xaxes(tickformat="%d-%m-%Y")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No portfolio history data.")

# --- Sell Recommendations ---
st.header("Sell Recommendations")
sell_recs = get_df("SELECT * FROM sell_recommendations")
if not sell_recs.empty:
    st.dataframe(
        sell_recs,
        column_config={
            "buy_price": st.column_config.NumberColumn("Buy Price", format="$%.2f"),
            "price": st.column_config.NumberColumn("Price", format="$%.2f"),
            "value": st.column_config.NumberColumn("Value", format="$%.2f"),
            "profit_and_loss": st.column_config.NumberColumn("P&L", format="$%.2f"),
            "percentage_return": st.column_config.NumberColumn("Return %", format="%.2f%%"),
        },
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No sell recommendations.")

# --- Watchlist History Chart ---
st.header("Watchlist History")
watchlist_history = get_df(
    "SELECT trade_date, symbol, price, `50dma`, `200dma` FROM watchlist_history ORDER BY trade_date"
)
if not watchlist_history.empty:
    symbols = sorted(watchlist_history["symbol"].unique())
    selected_symbol = st.selectbox("Select symbol", symbols, key="wh_symbol")
    filtered = watchlist_history[watchlist_history["symbol"] == selected_symbol]
    melted = filtered.melt(id_vars="trade_date", value_vars=["price", "50dma", "200dma"],
                           var_name="Series", value_name="Price")
    fig = px.line(melted, x="trade_date", y="Price", color="Series",
                  labels={"trade_date": ""})
    fig.update_xaxes(tickformat="%d-%m-%Y")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No watchlist history data.")

# --- Buy Recommendations ---
st.header("Buy Recommendations")
buy_recs = get_df("SELECT * FROM buy_recommendations")
if not buy_recs.empty:
    st.dataframe(
        buy_recs,
        column_config={
            "price": st.column_config.NumberColumn("Price", format="$%.2f"),
            "50dma": st.column_config.NumberColumn("50 DMA", format="$%.2f"),
            "200dma": st.column_config.NumberColumn("200 DMA", format="$%.2f"),
        },
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No buy recommendations.")
