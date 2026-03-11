import psycopg2
import os
import multiprocessing

def process_shard(shard_id, offset, limit):
    """Parallel worker: Finds 'Partial' status and updates to 'Recovered'"""
    conn = None
    cursor = None
    
    try:
        DB_HOST = os.getenv("DB_HOST")
        DB_PASS = os.getenv("DB_PASS")
        DB_PORT = int(os.getenv("DB_PORT", "5432"))
        
        if not DB_HOST or not DB_PASS:
            return f"Shard {shard_id} Failed: DB_HOST and DB_PASS environment variables must be set"
        
        # Connect using the whitelisted IP and project credentials
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database="postgres",
            user="postgres",
            password=DB_PASS,
            connect_timeout=10
        )
        cursor = conn.cursor()
        
        # Target the 'Partial' failures within this specific shard
        query = "SELECT device_id FROM ota_logs WHERE update_status = 'Partial' LIMIT %s OFFSET %s"
        cursor.execute(query, (limit, offset))
        failures = cursor.fetchall()
        
        if not failures:
            cursor.close()
            conn.close()
            return f"Shard {shard_id}: No 'Partial' failures to recover."

        # Perform the recovery update
        updated_count = 0
        for device in failures:
            cursor.execute("UPDATE ota_logs SET update_status = 'Recovered' WHERE device_id = %s", (device[0],))
            updated_count += cursor.rowcount
            
        conn.commit()
        cursor.close()
        conn.close()
        return f"Shard {shard_id}: Successfully recovered {len(failures)} devices (updated {updated_count} rows)."
    
    except psycopg2.OperationalError as e:
        error_msg = f"Shard {shard_id} Connection Failed: {e}"
        if conn:
            conn.close()
        return error_msg
    except psycopg2.Error as e:
        error_msg = f"Shard {shard_id} Database Error: {e}"
        if conn:
            conn.rollback()
            conn.close()
        return error_msg
    except Exception as e:
        error_msg = f"Shard {shard_id} Unexpected Error: {e}"
        if conn:
            try:
                conn.rollback()
                conn.close()
            except:
                pass
        return error_msg

if __name__ == "__main__":
    print("Initializing Sentinel Parallel Recovery Engine...")
    
    # Validate environment variables
    DB_HOST = os.getenv("DB_HOST")
    DB_PASS = os.getenv("DB_PASS")
    DB_PORT = int(os.getenv("DB_PORT", "5432"))
    
    if not DB_HOST or not DB_PASS:
        print("Error: DB_HOST and DB_PASS environment variables must be set")
        exit(1)
    
    # Configuration for 10,000 records
    total_records = 10000
    num_workers = 4
    shard_size = total_records // num_workers

    print(f"Using {num_workers} parallel workers with shard size of {shard_size}")
    print(f"Connecting to PostgreSQL at {DB_HOST}:{DB_PORT}...\n")

    # Launching the parallel pool
    try:
        with multiprocessing.Pool(processes=num_workers) as pool:
            tasks = [(i, i * shard_size, shard_size) for i in range(num_workers)]
            results = pool.starmap(process_shard, tasks)
            
        print("\n--- Final Recovery Report ---")
        print("\n".join(results))
        
        # Summary statistics
        success_count = sum(1 for r in results if "Successfully recovered" in r)
        failed_count = sum(1 for r in results if "Failed" in r)
        print(f"\nSummary: {success_count} shards succeeded, {failed_count} shards failed")
        
    except Exception as e:
        print(f"Error during parallel processing: {e}")
        exit(1)