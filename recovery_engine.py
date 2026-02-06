import sqlite3
import pandas as pd

def run_recovery():
    print("Sentinel Recovery Engine: Scanning SQL Database...")
    
    # Connect to the SQLite database
    conn = sqlite3.connect('fleet.db')
    
    # Load only the devices that need fixing (Filtering at the SQL level is faster!)
    query = "SELECT * FROM ota_logs WHERE update_status = 'Partial'"
    df_to_fix = pd.read_sql_query(query, conn)
    
    if df_to_fix.empty:
        print("No 'Partial' states found. Fleet is healthy.")
        conn.close()
        return

    # Logic: Apply the safety gates
    df_to_fix['recovery_action'] = df_to_fix['battery_voltage'].apply(
        lambda x: 'RETRY_UPDATE' if x > 12.5 else 'FORCE_ROLLBACK'
    )
    
    # Save the action report to a database table instead of a CSV
    df_to_fix.to_sql('recovery_actions', conn, if_exists='replace', index=False)
    
    # Also save a local CSV for the human-readable report
    df_to_fix.to_csv("recovery_actions_report.csv", index=False)
    
    print(f"Success: Processed {len(df_to_fix)} recovery actions.")
    print("Database Updated: Table 'recovery_actions' is now live.")
    
    conn.close()

if __name__ == "__main__":
    run_recovery()