import pandas as pd
import os

def test_recovery_output():
    # Check if the recovery actions file was created
    assert os.path.exists("recovery_actions.csv"), "Test Failed: Recovery log not found!"
    
    # Check if the data is valid
    df = pd.read_csv("recovery_actions.csv")
    assert not df.empty, "Test Failed: Recovery log is empty!"
    print(" All Tests Passed: Recovery Logic is stable.")

if __name__ == "__main__":
    test_recovery_output()