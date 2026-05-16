#!/bin/bash

# Check if MariaDB is already running
if systemctl is-active --quiet mariadb; then
    echo "MariaDB is already running."
else
    echo "Starting MariaDB..."
    systemctl start mariadb
fi

# Run the Python scripts
py update_watchlist.py
py update_portfolio.py

# Ask user whether to stop MariaDB
read -p "MariaDB is running. Do you want to stop it? (y/n): " answer
case "$answer" in
    [Yy]*)
        systemctl stop mariadb
        echo "MariaDB stopped."
        ;;
    [Nn]*)
        echo "MariaDB left running."
        ;;
    *)
        echo "Invalid response. MariaDB left running."
        ;;
esac
