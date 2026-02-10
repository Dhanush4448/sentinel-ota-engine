import psycopg2
import os
import multiprocessing

def process_shard(shard_id, offset, limit):
    """Parallel worker: Finds 'Partial' status and updates to 'Recovered'"""
    try:
        # Connect using the whitelisted IP and May 2026 project credentials
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "104.198.157.118"),
            database="postgres",
            user="postgres",
            password=os.getenv("DB_PASS")
        )
        cursor = conn.cursor()
        
        # Target the 'Partial' failures within this specific shard
        query = "SELECT device_id FROM ota_logs WHERE update_status = 'Partial' LIMIT %s OFFSET %s"
        cursor.execute(query, (limit, offset))
        failures = cursor.fetchall()
        
        if not failures:
            return f"Shard {shard_id}: No 'Partial' failures to recover."

        # Perform the recovery update
        for device in failures:
            cursor.execute("UPDATE ota_logs SET update_status = 'Recovered' WHERE device_id = %s", (device[0],))
            
        conn.commit()
        cursor.close()
        conn.close()
        return f"Shard {shard_id}: Successfully recovered {len(failures)} devices."
    
    except Exception as e:
        return f"Shard {shard_id} Failed: {e}"

if __name__ == "__main__":
    print("Initializing Sentinel Parallel Recovery Engine...")
    
    # Configuration for 10,000 records
    total_records = 10000
    num_workers = 4
    shard_size = total_records // num_workers

    # Launching the parallel pool for your MSCS portfolio project
    with multiprocessing.Pool(processes=num_workers) as pool:
        tasks = [(i, i * shard_size, shard_size) for i in range(num_workers)]
        results = pool.starmap(process_shard, tasks)
        
    print("\n--- Final Recovery Report ---")
    print("\n".join(results))