import sqlite3
import random
from faker import Faker

def generate_fleet_data(num_devices=10000):
    fake = Faker()
    db_name = "fleet.db"
    
    print(f"Generating telemetry for {num_devices} devices...")
    
    # Connect to (or create) the SQL database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Create a clean table for our logs
    cursor.execute("DROP TABLE IF EXISTS ota_logs")
    cursor.execute('''
        CREATE TABLE ota_logs (
            device_id TEXT PRIMARY KEY,
            region TEXT,
            battery_voltage REAL,
            signal_strength INTEGER,
            update_status TEXT
        )
    ''')

    regions = ['North America', 'Europe', 'India', 'Middle East', 'Asia-Pacific']
    fleet_data = []

    for _ in range(num_devices):
        device_id = f"DEV-{fake.unique.hexify(text='^^^^^^^^')}"
        region = random.choice(regions)
        
        # Logic: We intentionally lower battery/signal in certain regions to simulate 'Partial' failures
        if region in ['India', 'Middle East'] and random.random() < 0.35:
            update_status = "Partial"
            battery_voltage = round(random.uniform(11.8, 12.4), 2)  # Critical battery
        else:
            update_status = random.choice(["Success", "Success", "Partial"]) # 66% base success
            battery_voltage = round(random.uniform(12.5, 14.2), 2)

        signal_strength = random.randint(10, 100)
        
        fleet_data.append((device_id, region, battery_voltage, signal_strength, update_status))

    # Bulk insert for efficiency (Senior move)
    cursor.executemany('INSERT INTO ota_logs VALUES (?,?,?,?,?)', fleet_data)
    
    conn.commit()
    conn.close()
    print(f"Success: {num_devices} records injected into '{db_name}'")

if __name__ == "__main__":
    generate_fleet_data()