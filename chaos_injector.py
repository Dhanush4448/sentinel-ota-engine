import sqlite3
import random

def inject_chaos():
    print("Initializing Chaos Injector: Corrupting Fleet Data...")
    conn = sqlite3.connect('fleet.db')
    cursor = conn.cursor()

    # 1. Inject NULL values (Missing data)
    cursor.execute("""
        UPDATE ota_logs 
        SET battery_voltage = NULL 
        WHERE rowid IN (SELECT rowid FROM ota_logs ORDER BY RANDOM() LIMIT 50)
    """)
    
    # 2. Inject Out-of-Bounds data (Negative signal strength)
    cursor.execute("""
        UPDATE ota_logs 
        SET signal_strength = -999 
        WHERE rowid IN (SELECT rowid FROM ota_logs ORDER BY RANDOM() LIMIT 50)
    """)

    # 3. Inject Garbage Strings (Data type corruption)
    cursor.execute("""
        UPDATE ota_logs 
        SET battery_voltage = 'UNKNOWN' 
        WHERE rowid IN (SELECT rowid FROM ota_logs ORDER BY RANDOM() LIMIT 50)
    """)

    conn.commit()
    conn.close()
    print("Chaos Deployed: Missing values and corrupted strings injected.")

if __name__ == "__main__":
    inject_chaos()