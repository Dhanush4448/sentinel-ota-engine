import pandas as pd
from faker import Faker
import random

fake = Faker()

def generate_fleet_data(records=5000):
    fleet = []
    regions = ['North America', 'Europe', 'India', 'South America']
    statuses = ['Success', 'Failed', 'Partial', 'Pending']
    
    for _ in range(records):
        region = random.choice(regions)
        # Creating a 'bias' for your analysis: India/Europe have more 'Partial' updates
        if region in ['India', 'Europe']:
            status = random.choices(statuses, weights=[40, 10, 40, 10])[0]
        else:
            status = random.choices(statuses, weights=[70, 10, 10, 10])[0]

        device_log = {
            "device_id": fake.uuid4(),
            "region": region,
            "firmware_version": f"v{random.randint(1, 3)}.{random.randint(0, 9)}",
            "battery_voltage": round(random.uniform(11.5, 14.2), 2),
            "signal_strength": random.randint(-110, -30),
            "update_status": status,
            "timestamp": fake.date_time_this_month().isoformat()
        }
        fleet.append(device_log)
    
    return pd.DataFrame(fleet)

if __name__ == "__main__":
    df = generate_fleet_data(10000)
    df.to_csv("ota_logs.csv", index=False)
    print("✅ Generated 10,000 device logs in ota_logs.csv")