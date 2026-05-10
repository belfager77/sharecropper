import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error

# Database connection parameters
DB_CONFIG = {
    "host": "localhost",
    "user": "scuser",
    "password": "password",
    "database": "sc"
}

st.title("Portfolio View")

@st.cache_data(ttl=600)
def fetch_portfolio_data():
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            query = "SELECT * FROM portfolio_view"
            df = pd.read_sql(query, conn)
            return df
    except Error as e:
        st.error(f"Database error: {e}")
        return None
    finally:
        if conn and conn.is_connected():
            conn.close()

data = fetch_portfolio_data()

if data is not None and not data.empty:
    if 'profit_and_loss' in data.columns:
        # Columns to format with 2 decimal places
        decimal_cols = ['price', 'buy_price', 'profit_and_loss', 'percentage_return']
        existing_decimal_cols = [col for col in decimal_cols if col in data.columns]

        # Columns to center justify
        center_cols = ['quantity', 'price', 'buy_price', 'profit_and_loss', 'percentage_return']
        existing_center_cols = [col for col in center_cols if col in data.columns]

        # Function to color rows based on profit_and_loss
        def highlight_profit_loss(row):
            if row['profit_and_loss'] > 0:
                color = 'lightgreen'
            elif row['profit_and_loss'] < 0:
                color = 'lightcoral'
            else:
                color = 'white'
            return [f'background-color: {color}'] * len(row)

        # Apply formatting and row highlighting
        styled_df = data.style.format(
            {col: "{:.2f}" for col in existing_decimal_cols},
            na_rep="-"
        ).apply(highlight_profit_loss, axis=1)

        # Center justify selected columns (including headers)
        if existing_center_cols:
            styles = []
            for col in existing_center_cols:
                idx = data.columns.get_loc(col)  # 0-based column index
                # Header style
                styles.append({
                    'selector': f'th.col_level0:nth-child({idx+1})',
                    'props': [('text-align', 'center')]
                })
                # Data cells style
                styles.append({
                    'selector': f'tbody td:nth-child({idx+1})',
                    'props': [('text-align', 'center')]
                })
            styled_df = styled_df.set_table_styles(styles)

        st.dataframe(styled_df, use_container_width=True)

        # Total profit & loss
        total_profit_loss = data['profit_and_loss'].sum()
        total_color = "green" if total_profit_loss > 0 else "red" if total_profit_loss < 0 else "black"
        st.metric(
            label="Total Profit & Loss",
            value=f"${total_profit_loss:,.2f}",
            delta=None
        )
        #st.markdown(
        #    f"<h3 style='text-align: right; color: {total_color};'>Total P&L: ${total_profit_loss:,.2f}</h3>",
        #    unsafe_allow_html=True
        #)

    else:
        st.error("The view 'portfolio_view' does not contain a 'profit_and_loss' column.")
elif data is not None and data.empty:
    st.info("The portfolio_view view returned no records.")