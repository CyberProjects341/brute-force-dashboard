# Real-Time SOC Brute Force Detection Dashboard 
<img width="1920" height="1080" alt="dashboard-preview" src="https://github.com/user-attachments/assets/3f05b36a-b80e-4d36-acf0-8734d04067a8" />


An interactive Security Operations Center (SOC) monitoring platform engineered with Python (Flask), SQLite, and Leaflet.js to ingest, parse, aggregate, and geolocate Windows Event ID 4625 (Failed Logon) audit telemetry in real time.

* **Live GitHub Repository:** [https://github.com/Welcome2020/brute-force-dashboard](https://github.com/Welcome2020/brute-force-dashboard)

---

## The 5 Ws of the Project

* **Who:** Built for SOC Analysts (Tier 1/2), Threat Detection Engineers, and Incident Responders defending Active Directory domains, VPN concentrators, and perimeter infrastructure.
* **What:** An end-to-end detection pipeline that parses Event ID 4625 records, resolves attacking public IP coordinates via external Geo-IP APIs, categorizes failure sub-status hex codes, and highlights high-risk privilege escalation targets (`Administrator`, `root`).
* **When:** Active during distributed brute-force attacks, horizontal password spraying, credential-stuffing campaigns, and dictionary authentication floods.
* **Where:** Deployed across enterprise Windows endpoints, perimeter firewalls, exposed Remote Desktop Protocol (RDP) gateways, and Active Directory Domain Controllers (AD DCs).
* **Why:** Raw security event logs produce severe alert fatigue in high-throughput environments. This platform surfaces actionable signals by correlating volume anomalies, geographical dispersion, and low-level NTSTATUS failure codes to distinguish real attacks from benign user errors.

---

## Technical Challenges & Engineering Solutions

### 1. Cloud-Sync File Lock & Virtual Environment Corruption
* **Problem:** Initially initializing Python's virtual environment (`venv`) inside a cloud-synced storage directory (Google Drive) caused file-locking race conditions during package installation, corrupting `pip` binaries and throwing `ModuleNotFoundError: No module named 'pip._internal.utils.inject_securetransport'`.
* **Resolution:** Re-located the active execution workspace to a dedicated local directory (`C:\MyCyberProjects\`), re-initialized the virtual environment cleanly, and upgraded pip through Python's bootstrap engine (`ensurepip`).

### 2. Windows PowerShell Quoting & Execution Aliasing
* **Problem:** PowerShell threw parser errors (`Unexpected token '-m' in expression or statement`) when passing flags behind quoted Python executable paths, while Windows App Execution Aliases redirected calls to the Microsoft Store stub.
* **Resolution:** Disabled the Windows App Execution Aliases for Python and standardized script invocation using PowerShell's call operator (`&`) with the explicit interpreter path: `& "C:\Users\...\python.exe" -m pip install <package>`.

### 3. Synchronous Geo-IP Latency & Rate-Limit Resilience
* **Problem:** Querying the third-party Geo-IP endpoint (`ip-api.com`) synchronously during event ingestion risked blocking the Flask server thread if network latency spiked or HTTP rate limits (429 Too Many Requests) were reached.
* **Resolution:** Implemented defensive `try/except` exception handling with a strict 3-second network timeout, safely falling back to `"Unknown"` / `(0.0, 0.0)` coordinates to prevent dashboard crashes.

### 4. Differentiating True Brute Force from Benign User Typos
* **Problem:** Alerting purely on failed login volume results in high false-positive rates caused by regular users mistyping passwords or expired mobile Active Directory profiles.
* **Resolution:** Structured the ingestion schema to capture specific Sub-Status hex codes and distinct targeted user ratios:
  * `0xC000006A`: Bad password (user typo or password guessing).
  * `0xC0000064`: User name does not exist (account enumeration or spray).
  * `0xC0000234`: Account locked out (exceeded failed attempt threshold).

---

## System Architecture

```text
[Windows Event Telemetry / Mock Generator]
                    │
                    ▼
[Flask Backend Engine (app.py)] ───► [Geo-IP Resolution (ip-api.com)]
                    │
                    ▼
          [SQLite Database (database.db)]
                    │
                    ▼
[REST Endpoint: /api/data (JSON Response)]
                    │
                    ▼
[Leaflet.js UI + CSS (Auto-Polling every 5s)]

Installation & Setup
1. Clone the Repository

git clone [https://github.com/Welcome2020/brute-force-dashboard.git](https://github.com/Welcome2020/brute-force-dashboard.git)
cd SOC Brute Force Detection Dashboard

2. Environment Setup & Dependencies

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1   # Linux/macOS: source venv/bin/activate

# Install required packages
pip install -r requirements.txt

3. Run the Dashboard

python app.py or you can run py app.py
