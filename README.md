Sentinel OTA Engine: Resilient Fleet Recovery Pipeline
The Sentinel OTA Engine is a high-throughput data engineering and automation pipeline designed to manage firmware deployment failures across a global fleet of 10,000+ IoT devices in a distributed cloud environment.

Originally a local prototype, this system has been re-engineered for Enterprise Cloud Deployment on Google Cloud Platform (GCP). It utilizes Parallel Sharding and Batch Transaction Logic to detect and recover "partially updated" devices at scale across global regions.

Key Engineering Features
Cloud-Native Persistence: Migrated the backend from SQLite to a managed Google Cloud SQL (PostgreSQL) instance. Implemented secure CIDR-based firewall whitelisting and remote SSL handshakes for enterprise-grade security.

High-Throughput Parallelism: Utilizes Python’s multiprocessing library to shard fleet telemetry across multiple CPU cores. By establishing independent secure connections for each worker, the engine bypasses the Global Interpreter Lock (GIL) to achieve massive concurrency.

Resilient "Progressive Batch" Ingestion: Engineered a robust generator.py that handles network latency and socket timeouts by utilizing atomic commits in 500-record chunks, ensuring data integrity across a 10,000-record dataset.

Automated State Recovery: A parallelized controller that performs targeted cloud updates, transitioning thousands of devices from "Partial" failure to "Recovered" status based on real-time telemetry analysis.

Firmware Security Verification: Cryptographic signature verification and per-chunk integrity checks detect tampered firmware BEFORE installation. Implements RSA-PSS signatures and SHA-256 hashing to prevent man-in-the-middle attacks and malicious code injection.

Strategic Cost Management: Implemented a cloud-cost optimization workflow, utilizing activation-policy management and final de-provisioning to maintain a $0.00 project footprint when idle.

Tech Stack
Cloud Infrastructure: Google Cloud Platform (GCP), Cloud SQL (PostgreSQL)

Backend: Python 3.12 (psycopg2-binary, multiprocessing, Faker, cryptography)

DevOps: GCloud CLI, Network Firewalls (Ingress/Egress rules), Environment Variable Security

Analytics: SQL (Window Functions, Aggregations), Matplotlib, Seaborn

Project Structure

**Cloud SQL Components (Production):**
- generator.py: Batch-processes 10k synthetic telemetry records into Cloud SQL with progressive progress tracking (500-record batches).
- recovery_engine.py: Multi-core parallel controller that shards the cloud dataset and executes high-speed recovery updates using 4 worker processes.
- analytics_viz.py: Generates regional heatmaps and deployment success visualizations from live Cloud SQL data.
- firmware_verifier.py: Cryptographic firmware verification module with RSA signatures and SHA-256 chunk integrity checks.
- ota_update_pipeline.py: Secure OTA update pipeline integrating firmware verification before installation.

**Local SQLite Components (Legacy/Testing):**
- chaos_injector.py: Legacy tool for injecting test chaos scenarios into local SQLite database (fleet.db).
- test_sentinel.py: Pipeline integrity tests for local SQLite database.
- test_engine.py: Tests recovery output CSV files.
- analytics_dashboard.ipynb: Jupyter notebook for interactive analysis of local SQLite data.

**Configuration:**
- requirements.txt: Manages environment dependencies for secure local-to-cloud communication.
- Dockerfile: Containerizes the application and runs test_sentinel.py on startup.

How to Run & Validate

**Prerequisites:**
- Python 3.12+
- Google Cloud SQL (PostgreSQL) instance active
- Your public IP whitelisted in Cloud SQL firewall rules
- Environment variables set: `DB_HOST` and `DB_PASS`

**Installation:**
```bash
pip install -r requirements.txt
```

**GCP Cloud SQL Workflow:**

1. **Set Environment Variables:**
   ```powershell
   $env:DB_HOST="YOUR_CLOUD_IP"
   $env:DB_PASS="YOUR_PASSWORD"
   ```

2. **Generate Cloud Fleet:**
   ```bash
   python generator.py
   ```
   This creates the `ota_logs` table and inserts 10,000 synthetic device records in batches of 500.

3. **Execute Parallel Recovery:**
   ```bash
   python recovery_engine.py
   ```
   This uses 4 parallel workers to recover devices with "Partial" status.

4. **Generate Analytics Visualizations:**
   ```bash
   python analytics_viz.py
   ```
   This generates:
   - Recovery status distribution chart (`recovery_action_distribution.png`)
   - Regional heatmap (`regional_heatmap.png`)
   - Summary statistics printed to console

**Validation:**
Run the following query in Google Cloud Query Studio or via psql to confirm recovery rates:
```sql
SELECT update_status, count(*) FROM ota_logs GROUP BY update_status;
```

**Firmware Security Verification:**
The system includes cryptographic verification to detect tampered firmware BEFORE installation:
```bash
python firmware_verifier.py  # Run security tests
python ota_update_pipeline.py  # Example secure update pipeline
```
See `SECURITY_FIRMWARE.md` for detailed security architecture and threat model.

**Local SQLite Testing (Legacy):**
For local testing with SQLite, use:
- `chaos_injector.py`: Injects test chaos scenarios
- `test_sentinel.py`: Runs pipeline integrity tests
- `analytics_dashboard.ipynb`: Interactive Jupyter notebook analysis