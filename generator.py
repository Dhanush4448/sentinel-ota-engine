import psycopg2
import random
import os
from faker import Faker

def generate_fleet_data(num_devices=10000):
    fake = Faker()
    DB_HOST = os.getenv("DB_HOST")
    DB_PASS = os.getenv("DB_PASS")
    DB_PORT = int(os.getenv("DB_PORT", "5432"))
    
    if not DB_HOST or not DB_PASS:
        raise ValueError("DB_HOST and DB_PASS environment variables must be set")

    print(f"Connecting to PostgreSQL at {DB_HOST}:{DB_PORT}...")
    
    conn = None
    cursor = None
    
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database="postgres",
            user="postgres",
            password=DB_PASS,
            connect_timeout=10,
        )
        cursor = conn.cursor()

        # Step 1: Create the table immediately
        print("Creating 'ota_logs' table...")
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
        total_inserted = 0
        
        for i in range(0, num_devices, batch_size):
            try:
                batch = []
                current_batch_size = min(batch_size, num_devices - i)
                
                for _ in range(current_batch_size):
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
                total_inserted += current_batch_size
                print(f"Progress: {total_inserted}/{num_devices} records injected...")
                
            except psycopg2.Error as e:
                conn.rollback()
                print(f"Error inserting batch at offset {i}: {e}")
                raise

        # Verify insertion
        cursor.execute("SELECT COUNT(*) FROM ota_logs")
        count = cursor.fetchone()[0]
        print(f"\nVerification: {count} records in database.")
        
        if count != num_devices:
            print(f"Warning: Expected {num_devices} records but found {count}")

        cursor.close()
        conn.close()
        print("Final Success: All records are in the cloud!")

    except psycopg2.OperationalError as e:
        print(f"Database connection error: {e}")
        print("Please verify:")
        print("  - Cloud SQL instance is running")
        print("  - DB_HOST and DB_PASS are correct")
        print("  - Your IP is whitelisted in Cloud SQL firewall rules")
        if conn:
            conn.close()
        exit(1)
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback()
            conn.close()
        exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        if conn:
            conn.rollback()
            conn.close()
        exit(1)

if __name__ == "__main__":
    generate_fleet_data()