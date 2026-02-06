import pandas as pd
import os

def run_recovery():
    print(" Sentinel Recovery Engine: Scanning for fleet anomalies...")
    
    if not os.path.exists("ota_logs.csv"):
        print(" Error: ota_logs.csv not found. Run 'python generator.py' first.")
        return

    # Load the fleet logs
    df = pd.read_csv("ota_logs.csv")
    
    # Logic: Identify devices stuck in 'Partial' state
    # We use battery voltage as a safety gate for recovery
    to_fix = df[df['update_status'] == 'Partial'].copy()
    
    # If battery > 12.5V, we can safely attempt a 'RETRY'
    # If battery <= 12.5V, we must 'ROLLBACK' to prevent a bricked device
    to_fix['recovery_action'] = to_fix['battery_voltage'].apply(
        lambda x: 'RETRY_UPDATE' if x > 12.5 else 'FORCE_ROLLBACK'
    )
    
    # Save the intervention report
    to_fix.to_csv("recovery_actions.csv", index=False)
    print(f" Success: Processed {len(to_fix)} recovery actions.")
    print(" Results saved to: recovery_actions.csv")

if __name__ == "__main__":
    run_recovery()