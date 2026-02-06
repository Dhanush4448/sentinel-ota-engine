import pandas as pd
import os

def test_pipeline():
    print(" Running Unit Tests...")

    # Test 1: Data Generation
    assert os.path.exists("ota_logs.csv"), "Step 1 Failed: ota_logs.csv was not created."
    df_logs = pd.read_csv("ota_logs.csv")
    assert len(df_logs) >= 10000, "Step 1 Failed: Dataset size is incorrect."
    print("Data Generation: PASSED")

    # Test 2: Recovery Logic Integrity
    assert os.path.exists("recovery_actions.csv"), "Step 2 Failed: recovery_actions.csv not found."
    df_rec = pd.read_csv("recovery_actions.csv")
    
    # Check if low battery logic is enforced
    low_batt_failures = df_rec[(df_rec['battery_voltage'] <= 12.5) & (df_rec['recovery_action'] != 'FORCE_ROLLBACK')]
    assert len(low_batt_failures) == 0, "Step 2 Failed: Logic Error! Low battery devices were not rolled back."
    print("Recovery Logic: PASSED")

if __name__ == "__main__":
    try:
        test_pipeline()
        print("\n ALL SYSTEMS GO: The Sentinel Engine is fully functional.")
    except AssertionError as e:
        print(f"\n SYSTEM FAILURE: {e}")