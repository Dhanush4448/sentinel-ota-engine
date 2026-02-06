\# Sentinel OTA Engine: Fleet Reliability \& Recovery Pipeline 🛡️



\## 📌 Project Overview

The \*\*Sentinel OTA Engine\*\* is an end-to-end data engineering and automation pipeline designed to manage Over-the-Air (OTA) firmware deployments for a global fleet of 10,000+ IoT devices. 



This project addresses a critical industry pain point: \*\*Partial Update Failures\*\*. Instead of manual troubleshooting, this system automates the detection and recovery of "bricked" or "partially updated" devices using telemetry-driven logic.



---



\## 🏗️ System Architecture





1\. \*\*Telemetry Generation:\*\* A Python-based engine simulates real-world device behavior, including battery health, signal strength, and firmware versioning.

2\. \*\*Analytical Layer:\*\* Utilizes \*\*SQL CTEs and Window Functions\*\* to rank regional deployment bottlenecks and identify failure clusters.

3\. \*\*Automated Recovery:\*\* A decision-making controller that triggers \*\*Retries\*\* or \*\*Rollbacks\*\* based on edge-case telemetry (e.g., preventing a rollback if battery voltage is too low).



---



\## 🛠️ Tech Stack \& Skills

\* \*\*Language:\*\* Python 3.12 (Pandas, Faker)

\* \*\*Data Engineering:\*\* SQL (GCP BigQuery syntax), CTEs, Window Functions (`RANK()`, `PARTITION BY`)

\* \*\*DevOps/CI:\*\* Git Hygiene, Virtual Environments (`venv`), Unit Testing

\* \*\*Concepts:\*\* IoT Fleet Management, OTA Workflows, Incident Automation



---



\## 🚀 Key Features

\* \*\*Synthetic Fleet Simulation:\*\* Generates 10,000+ records with regional failure biases to test scalability.

\* \*\*Edge-Case Recovery:\*\* Implements logic to handle "Partially Updated" states—the most complex failure in OTA deployments.

\* \*\*Reliability Dashboarding:\*\* Structured SQL queries ready for visualization in tools like \*\*Looker Studio\*\* or \*\*Tableau\*\*.



---



\## 📂 Project Structure

\* `generator.py`: The heart of the data pipeline; creates the synthetic telemetry dataset.

\* `recovery\_engine.py`: The automation controller that processes logs and decides on recovery actions.

\* `analysis\_queries.sql`: Advanced SQL for identifying fleet-wide trends.

\* `test\_engine.py`: Basic unit tests to ensure recovery logic integrity.



---



\## 📈 Impact \& Use Case

This architecture mimics systems used at scale by automotive and IoT leaders. By automating the recovery of "Partial" states, the system demonstrates a theoretical \*\*90% reduction in manual configuration time\*\* for fleet engineers.

