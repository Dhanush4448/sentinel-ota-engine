import psycopg2
import random
import os
from faker import Faker

def generate_fleet_data(num_devices=10000):
    fake = Faker()
    DB_HOST = os.getenv("DB_HOST", "104.198.157.118")
    DB_PASS = os.getenv("DB_PASS")

    print(f"Connecting to Cloud SQL at {DB_HOST}...")
    
    try:
        conn = psycopg2.connect(
            dsn=f"dbname='postgres' user='postgres' host='{DB_HOST}' password='{DB_PASS}' connect_timeout=10"
        )
        cursor = conn.cursor()

        # Step 1: Create the table immediately
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
        conn.commit() # Save the table structure first
        print("Table 'ota_logs' created successfully.")

        regions = ['North America', 'Europe', 'India', 'Middle East', 'Asia-Pacific']
        
        # Step 2: Insert in batches of 500
        batch_size = 500
        for i in range(0, num_devices, batch_size):
            batch = []
            for _ in range(batch_size):
                device_id = f"DEV-{fake.unique.hexify(text='^^^^^^^^')}"
                batch.append((
                    device_id, 
                    random.choice(regions), 
                    round(random.uniform(11.8, 14.2), 2), 
                    random.randint(10, 100), 
                    random.choice(["Success", "Success", "Partial"])
                ))
            
            cursor.executemany('INSERT INTO ota_logs VALUES (%s,%s,%s,%s,%s)', batch)
            conn.commit() # Commit every 500 rows
            print(f"Progress: {i + batch_size}/{num_devices} records injected...")

        cursor.close()
        conn.close()
        print("Final Success: All 10,000 records are in the cloud!")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_fleet_data()