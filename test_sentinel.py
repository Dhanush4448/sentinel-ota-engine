import sqlite3
import os
import pandas as pd

def test_pipeline():
    print("Running SQL-Integrated Unit Tests...")

    # Test 1: Database Existence
    assert os.path.exists("fleet.db"), "Step 1 Failed: fleet.db was not created."
    
    conn = sqlite3.connect("fleet.db")
    df_logs = pd.read_sql_query("SELECT * FROM ota_logs", conn)
    assert len(df_logs) >= 10000, "Step 1 Failed: SQL Table has incorrect row count."
    print("SQL Data Ingestion: PASSED")

    # Test 2: Recovery Logic Validation (From Database)
    # This checks the new report file created by the engine
    assert os.path.exists("recovery_actions_report.csv"), "Step 2 Failed: Recovery report not found."
    df_rec = pd.read_csv("recovery_actions_report.csv")
    
    # Logic Check: High battery must be RETRY, Low battery must be ROLLBACK
    logic_errors = df_rec[
        ((df_rec['battery_voltage'] > 12.5) & (df_rec['recovery_action'] != 'RETRY_UPDATE')) |
        ((df_rec['battery_voltage'] <= 12.5) & (df_rec['recovery_action'] != 'FORCE_ROLLBACK'))
    ]
    
    assert len(logic_errors) == 0, f"Step 2 Failed: Logic Error found in {len(logic_errors)} rows."
    print("SQL-to-Logic Mapping: PASSED")
    conn.close()

if __name__ == "__main__":
    try:
        test_pipeline()
        print("\nMISSION SUCCESS: The Sentinel SQL Engine is battle-ready.")
    except AssertionError as e:
        print(f"\nVALIDATION FAILURE: {e}")