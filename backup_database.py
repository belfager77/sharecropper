#!/usr/bin/env python3

import os
import subprocess
from datetime import datetime

# Database configuration
DB_NAME = "sc"
DB_USER = "scuser"
DB_PASSWORD = "password"

# Backup directory
BACKUP_DIR = "/home/simon/mariadb_backups"

# Ensure backup directory exists
os.makedirs(BACKUP_DIR, exist_ok=True)

# Create timestamped backup filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = os.path.join(BACKUP_DIR, f"{DB_NAME}_backup_{timestamp}.sql")

# mysqldump command
command = [
    "mysqldump",
    "-u", DB_USER,
    f"-p{DB_PASSWORD}",
    DB_NAME
]

try:
    with open(backup_file, "w") as outfile:
        result = subprocess.run(
            command,
            stdout=outfile,
            stderr=subprocess.PIPE,
            text=True
        )

    if result.returncode == 0:
        print(f"Backup completed successfully: {backup_file}")
    else:
        print("Backup failed.")
        print(result.stderr)

except Exception as e:
    print(f"An error occurred: {e}")