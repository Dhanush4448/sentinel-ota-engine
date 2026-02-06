import sqlite3
import pandas as pd
from concurrent.futures import ProcessPoolExecutor
import time
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.console import Console

console = Console()

def process_device_batch(batch):
    # Simulate a tiny bit of work so the progress bar is visible
    time.sleep(0.1) 
    batch['recovery_action'] = batch['battery_voltage'].apply(
        lambda x: 'RETRY_UPDATE' if x > 12.5 else 'FORCE_ROLLBACK'
    )
    return batch

def run_parallel_recovery():
    console.print("[bold cyan]🚀 Sentinel High-Throughput Engine[/bold cyan] | [yellow]Mode: Parallel Sharding[/yellow]")
    
    conn = sqlite3.connect('fleet.db')
    df_to_fix = pd.read_sql_query("SELECT * FROM ota_logs WHERE update_status = 'Partial'", conn)
    
    if df_to_fix.empty:
        console.print("[bold green]✅ Fleet is healthy. No actions required.[/bold green]")
        return

    num_shards = 4
    chunks = [df_to_fix[i::num_shards] for i in range(num_shards)]
    
    start_time = time.time()

    

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        
        main_task = progress.add_task("[green]Processing Shards...", total=num_shards)
        
        with ProcessPoolExecutor() as executor:
            futures = [executor.submit(process_device_batch, chunk) for chunk in chunks]
            results = []
            for future in futures:
                results.append(future.result())
                progress.advance(main_task)

    final_df = pd.concat(results)
    final_df.to_sql('recovery_actions', conn, if_exists='replace', index=False)
    
    duration = round(time.time() - start_time, 4)
    throughput = round(len(df_to_fix)/duration, 2)

    console.print(f"\n[bold green]⚡ Parallel Execution Complete![/bold green]")
    console.print(f"⏱️  [bold]Time:[/bold] {duration}s | 🚀 [bold]Throughput:[/bold] {throughput} devices/sec\n")
    conn.close()

if __name__ == "__main__":
    run_parallel_recovery()