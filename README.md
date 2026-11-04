# 📊 Nifty 500 Market Performance Enterprise Workspace

A production-grade Streamlit terminal engineered to map daily market trends across all 500 Nifty constituents. This application follows a strict **Verification-First structural framework**, ensuring you can inspect the base equity index layout on your desktop screen before compiling the ReportLab accounting ledger and initiating down-stream email operations via secure SMTP.

---

## 🛠️ Architecture & Core Components

```mermaid
graph TD
    %% Base Infrastructure Load
    A[app.py Platform Boot] -->|Step 1: On-Init Standby| B(src/data_engine.py: fetch_master_list)
    B -->|Pathway 1: Relative Disk| C{data/ind_nifty500list.csv}
    B -->|Pathway 2: High-Availability Mirror| D[Raw GitHub CDN Stream]
    
    %% Desktop Interface Rendering
    C & D -->|Populate Data Frame| E[📋 Master Ledger Workspace]
    E -->|Interactive Desktop View| F[User Verification Review Phase]
    
    %% Live Processing Ingestion Execution
    F -->|Step 2: Trigger Action| G[Execute Live Ingestion Button]
    G -->|Parallel Batch Pooling| H(yfinance Multi-Thread Engine)
    H -->|Download 5d Pricing Windows| I[Calculate Closes & % Deltas]
    
    %% Downstream Document Output
    I -->|Step 3: Render Metrics| J[Update Grid + Activate Charts]
    I -->|Auto-Compile Binaries| K(src/pdf_generator.py)
    K -->|Build Landscape Multi-Page Ledger| L[Nifty500_Master_Report.pdf]
    
    %% Secure Transmission Route
    J & L -->|Step 4: Silent Dispatch| M[Dispatch PDF Report Button]
    M -->|Extract Context via TOML Secrets| N{st.secrets gmail}
    N -->|Route Secure TLS Packet| O(src/email_service.py)
    O -->|Target Server: ://gmail.com| P[hisrinivas1972@gmail.com]

    %% Class Styling for Clean UI Nodes
    style E fill:#e1f5fe,stroke:#03a9f4,stroke-width:2px;
    style F fill:#fff9c4,stroke:#fbc02d,stroke-width:2px;
    style L fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px;
    style P fill:#ffebee,stroke:#c62828,stroke-width:2px;
```

---

## 🚀 Local Network Initialization

To spin up the server environment locally on port **`8056`**, execute the following sequence inside your project repository terminal:

### 1. Set Up Environment Variables
Create a local folder named `.streamlit` and save your private relay endpoints inside `secrets.toml`:

```toml
# .streamlit/secrets.toml
[gmail]
username = "your-automated-system@gmail.com"
app_password = "xxxx xxxx xxxx xxxx" # 16-digit Google App Password
to_email = "***********@gmail.com"
```

### 2. Boot Up the Streamlit Core Server
Run the platform using the explicit network flag to map the interface directly to port `8056`:

```bash
streamlit run app.py --server.port 8056 --server.address localhost
```

Once executed, open your desktop browser and navigate to:
🔗 **`http://localhost:8506`**

---

## ⚡ Operational Guidelines

1. **Phase 1 (Verification Standby):** On application boot, the master list of 500 scrips will instantly load onto the interactive desktop table grid. Use the inline search box to verify components or sectors before running calculations.
2. **Phase 2 (Live Sync):** Click **Execute Live Ingestion** in the sidebar. The system will leverage high-concurrency batch threads to map price deltas, paint color-coded trends (`🟢 Up` / `🔴 Down`), and generate a landscape PDF balance sheet.
3. **Phase 3 (Document Delivery):** Click **Dispatch PDF Report**. The core will match your binary workspace payload against your hidden `secrets.toml` recipients list and route the finished document out without exposing confidential data fields on-screen.
