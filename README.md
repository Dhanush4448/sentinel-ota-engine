Sentinel OTA Engine: Resilient Fleet Recovery Pipeline
The Sentinel OTA Engine is a high-throughput data engineering and automation pipeline designed to manage firmware deployment failures across a global fleet of 10,000+ IoT devices in a distributed cloud environment.

Originally a local prototype, this system has been re-engineered for Enterprise Cloud Deployment on Google Cloud Platform (GCP). It utilizes Parallel Sharding and Batch Transaction Logic to detect and recover "partially updated" devices at scale across global regions.

Key Engineering Features
Cloud-Native Persistence: Migrated the backend from SQLite to a managed Google Cloud SQL (PostgreSQL) instance. Implemented secure CIDR-based firewall whitelisting and remote SSL handshakes for enterprise-grade security.

High-Throughput Parallelism: Utilizes Python’s multiprocessing library to shard fleet telemetry across multiple CPU cores. By establishing independent secure connections for each worker, the engine bypasses the Global Interpreter Lock (GIL) to achieve massive concurrency.

Resilient "Progressive Batch" Ingestion: Engineered a robust generator.py that handles network latency and socket timeouts by utilizing atomic commits in 500-record chunks, ensuring data integrity across a 10,000-record dataset.

Automated State Recovery: A parallelized controller that performs targeted cloud updates, transitioning thousands of devices from "Partial" failure to "Recovered" status based on real-time telemetry analysis.

Strategic Cost Management: Implemented a cloud-cost optimization workflow, utilizing activation-policy management and final de-provisioning to maintain a $0.00 project footprint when idle.

Tech Stack
Cloud Infrastructure: Google Cloud Platform (GCP), Cloud SQL (PostgreSQL)

Backend: Python 3.12 (psycopg2-binary, multiprocessing, Faker)

DevOps: GCloud CLI, Network Firewalls (Ingress/Egress rules), Environment Variable Security

Analytics: SQL (Window Functions, Aggregations), Matplotlib, Seaborn

Project Structure
generator.py: Batch-processes 10k synthetic telemetry records into the cloud with progressive progress tracking.

recovery_engine.py: Multi-core parallel controller that shards the cloud dataset and executes high-speed recovery updates.

analytics_viz.py: Generates regional heatmaps and deployment success visualizations from live cloud data.

requirements.txt: Manages environment dependencies for secure local-to-cloud communication.

How to Run & Validate
GCP Setup: Ensure your Cloud SQL instance is active and your current public IP is whitelisted.

Generate Cloud Fleet:

PowerShell
$env:DB_HOST="YOUR_CLOUD_IP"
$env:DB_PASS="YOUR_PASSWORD"
python -m generator
Execute Parallel Recovery:

PowerShell
python -m recovery_engine
Validate & Analyze: Run the following query in Google Cloud Query Studio to confirm the 100% recovery rate:

SQL
SELECT update_status, count(*) FROM ota_logs GROUP BY update_status;