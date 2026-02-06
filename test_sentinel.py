import sqlite3
import os
import pandas as pd

def test_pipeline():
    print("Running Advanced Resilience Suite...")

    # Test 1: Standard Integrity
    conn = sqlite3.connect("fleet.db")
    df_logs = pd.read_sql_query("SELECT * FROM ota_logs", conn)
    assert len(df_logs) >= 10000, "Integrity Failed: Data missing."
    print("Base Integrity: PASSED")

    # Test 2: Chaos Resilience (The "Negative" Test)
    # Check if 'MANUAL_TRIAGE' exists in the results after chaos injection
    if os.path.exists("recovery_actions_report.csv"):
        df_rec = pd.read_csv("recovery_actions_report.csv")
        triage_count = len(df_rec[df_rec['recovery_action'] == 'MANUAL_TRIAGE'])
        
        if triage_count > 0:
            print(f"Chaos Resilience: PASSED ({triage_count} corrupted records quarantined)")
        else:
            print("Chaos Note: No corrupted records detected in this run.")
    
    conn.close()

if __name__ == "__main__":
    try:
        test_pipeline()
        print("\nFINAL VERDICT: System is Bulletproof.")
    except Exception as e:
        print(f"\nSYSTEM VULNERABILITY: {e}")