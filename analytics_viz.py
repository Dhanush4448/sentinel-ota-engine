import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def connect_to_cloud_sql():
    """Establish connection to Cloud SQL PostgreSQL instance"""
    DB_HOST = os.getenv("DB_HOST")
    DB_PASS = os.getenv("DB_PASS")
    DB_PORT = int(os.getenv("DB_PORT", "5432"))
    
    if not DB_HOST or not DB_PASS:
        raise ValueError("DB_HOST and DB_PASS environment variables must be set")
    
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database="postgres",
        user="postgres",
        password=DB_PASS
    )
    return conn

def generate_recovery_action_distribution(conn, output_file='recovery_action_distribution.png'):
    """Generate recovery status distribution chart"""
    query = """
    SELECT update_status, COUNT(*) as count
    FROM ota_logs
    GROUP BY update_status
    """
    
    df = pd.read_sql_query(query, conn)
    
    plt.figure(figsize=(10, 6))
    # df is already aggregated; use a simple bar chart for reliability across seaborn/matplotlib versions
    df = df.sort_values("count", ascending=False)
    plt.bar(df["update_status"], df["count"], color=["#3B82F6"] * len(df))
    plt.title('Fleet Update Status Distribution')
    plt.ylabel('Number of Devices')
    plt.xlabel('Update Status')
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"Recovery action distribution chart saved to {output_file}")
    plt.close()

def generate_regional_heatmap(conn, output_file='regional_heatmap.png'):
    """Generate regional update status heatmap"""
    query = """
    WITH RegionalStats AS (
        SELECT 
            region,
            update_status,
            COUNT(*) as count,
            SUM(COUNT(*)) OVER(PARTITION BY region) as total
        FROM ota_logs
        GROUP BY 1, 2
    )
    SELECT region, update_status, ROUND((count*1.0/total)*100, 2) as percentage
    FROM RegionalStats
    """
    
    stats_df = pd.read_sql_query(query, conn)
    pivot_df = stats_df.pivot(index='region', columns='update_status', values='percentage')
    
    plt.figure(figsize=(12, 6))
    sns.heatmap(pivot_df, annot=True, cmap='YlOrRd', fmt='.2f', cbar_kws={'label': 'Percentage'})
    plt.title('Regional Update Status Heatmap (%)')
    plt.ylabel('Region')
    plt.xlabel('Update Status')
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"Regional heatmap saved to {output_file}")
    plt.close()

def generate_summary_statistics(conn):
    """Print summary statistics from the database"""
    query = """
    SELECT 
        update_status,
        COUNT(*) as device_count,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
    FROM ota_logs
    GROUP BY update_status
    ORDER BY device_count DESC
    """
    
    df = pd.read_sql_query(query, conn)
    print("\n--- Fleet Update Status Summary ---")
    print(df.to_string(index=False))
    
    query_regional = """
    SELECT 
        region,
        COUNT(*) as total_devices,
        SUM(CASE WHEN update_status = 'Partial' THEN 1 ELSE 0 END) as partial_count,
        SUM(CASE WHEN update_status = 'Recovered' THEN 1 ELSE 0 END) as recovered_count,
        SUM(CASE WHEN update_status = 'Success' THEN 1 ELSE 0 END) as success_count
    FROM ota_logs
    GROUP BY region
    ORDER BY total_devices DESC
    """
    
    df_regional = pd.read_sql_query(query_regional, conn)
    print("\n--- Regional Breakdown ---")
    print(df_regional.to_string(index=False))

if __name__ == "__main__":
    print("Initializing Sentinel Analytics Visualization...")
    
    try:
        conn = connect_to_cloud_sql()
        print("Connected to Cloud SQL successfully.")
        
        # Generate summary statistics
        generate_summary_statistics(conn)
        
        # Generate visualizations
        generate_recovery_action_distribution(conn)
        generate_regional_heatmap(conn)
        
        conn.close()
        print("\nAnalytics visualization complete!")
        
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
