Sentinel OTA Engine: Resilient Fleet Recovery Pipeline
The Sentinel OTA Engine is a high-throughput data engineering pipeline designed to automate the recovery of Over-the-Air (OTA) firmware failures for a global fleet of 10,000+ IoT devices.

Key Architectural Upgrades
This project has been engineered to go beyond basic scripting, implementing "Senior-level" system design principles:

Parallel Sharding: Utilizes Python's ProcessPoolExecutor to bypass the GIL, sharding the fleet into parallel streams for high-throughput processing.

Database-First Persistence: Replaced legacy CSV handling with a relational SQLite backend, utilizing SQL Window Functions (RANK, PARTITION BY) for regional bottleneck analysis.

Chaos Engineering: Includes a custom chaos_injector.py suite that simulates real-world data corruption (NULL values, type mismatches, and out-of-bounds telemetry).

Data Sanitization & Resilience: Implemented robust sanitization using pandas to quarantine corrupted data into a "Manual Triage" queue without halting the pipeline.

Live Observability: Integrated a real-time CLI dashboard using the rich library to monitor processing speed and shard health.

Tech Stack
Language: Python 3.12 (Pandas, Concurrent.Futures, Faker)

Database: SQLite3 (Relational persistence & CTE analysis)

DevOps: Docker (Containerization), Unit Testing (Negative & Positive testing)

Observability: Rich (CLI Dashboards)

System Structure
generator.py: Injects 10k telemetry records into the SQL database.

chaos_injector.py: Simulates "Dirty Data" by corrupting the database state.

recovery_engine.py: The high-speed parallel controller that cleans and fixes the fleet.

test_sentinel.py: Advanced test suite validating base integrity and chaos resilience.

How to Run & Validate
Follow the "Full Gauntlet" to see the resilience in action:

Initialize & Corrupt:

Bash
python generator.py      # Create clean fleet data
python chaos_injector.py # Intentionally break data integrity
Execute Parallel Recovery:

Bash
python recovery_engine.py
Validate Resilience:

Bash
python test_sentinel.py  # Confirms that 'dirty' data was quarantined, not crash