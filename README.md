Sentinel OTA Engine: Resilient Fleet Recovery Pipeline
The Sentinel OTA Engine is a high-throughput data engineering and automation pipeline designed to manage firmware deployment failures across a global fleet of 10,000+ IoT devices.

This system moves beyond basic troubleshooting by implementing Chaos Engineering and Parallel Sharding to detect, quarantine, and recover "bricked" or "partially updated" devices at scale.

Key Engineering Features
High-Throughput Parallelism: Utilizes Python’s ProcessPoolExecutor to shard fleet telemetry across multiple CPU cores, achieving processing speeds of 40,000+ devices/sec.

Relational Persistence: Migrated from flat-file storage to a SQLite backend, enabling advanced SQL Window Functions (RANK, PARTITION BY) for regional bottleneck analysis.

Chaos Engineering Suite: Integrated a custom chaos_injector.py to simulate real-world data corruption (NULL values, type mismatches, and signal drops).

Data Resilience & Triage: Engineered a robust sanitization layer that automatically quarantines corrupted telemetry into a Manual Triage queue without halting the deployment pipeline.

Executive Analytics: Includes a Jupyter Notebook dashboard for regional failure heatmapping and recovery ROI visualization.

Tech Stack
Backend: Python 3.12 (Pandas, Concurrent.Futures, Faker)

Database: SQLite3 (CTEs, Window Functions)

DevOps: Docker (Containerization), Unit Testing (Negative & Positive logic)

Analytics: Jupyter Notebook, Matplotlib, Seaborn

Project Structure
generator.py: Generates 10k synthetic telemetry records into SQL.

chaos_injector.py: Injects data corruption to test system resilience.

recovery_engine.py: Parallelized controller with live rich observability.

analytics_dashboard.ipynb: Executive reporting and failure visualization.

test_sentinel.py: Automated validation suite for the full pipeline.

How to Run & Validate
Follow the "Full Gauntlet" to see the engine's resilience in action:

Generate & Corrupt:

Bash
python generator.py
python chaos_injector.py
Execute Parallel Recovery:

Bash
python recovery_engine.py
Validate & Analyze:

Bash
python test_sentinel.py
# Open analytics_dashboard.ipynb to view regional heatmaps