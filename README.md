# 📊 Nifty 500 Market Performance Enterprise Workspace

A production-grade Streamlit terminal engineered to map daily market trends across all 500 Nifty constituents. This application follows a strict **Verification-First structural framework**, ensuring you can inspect the base equity index layout on your desktop screen before compiling the ReportLab accounting ledger and initiating downstream email operations via secure SMTP.

---

## 📂 System Architecture Repository Tree

```text
nifty500-market-matrix/
├── .streamlit/
│   └── secrets.toml          # Encrypted enterprise credentials & target email storage
├── data/
│   └── ind_nifty500list.csv  # High-speed local baseline ledger fallback (Auto-generated)
├── src/
│   ├── __init__.py           # Explicit package boundary initialization
│   ├── data_engine.py        # Core processing matrix bypassing firewall blocks (yfinance)
│   ├── email_service.py      # Secure SMTP distribution layer targeting port 587
│   └── pdf_generator.py      # Production ReportLab engine drafting landscape documents
├── app.py                    # Streamlit interface executing port 8501 runtimes
└── README.md                 # System operational manual with structural Mermaid diagrams
```

---

## 🛠️ Architecture & Core Components

```mermaid
flowchart TD
    %% Base Infrastructure Load
    A[app.py Platform Boot] e1@-->|Step 1: On-Init Standby| B(src/data_engine.py: fetch_master_list)
    B e2@-->|Pathway 1: Relative Disk| C{data/ind_nifty500list.csv}
    B e3@-->|Pathway 2: High-Availability Mirror| D[Raw GitHub CDN Stream]
    
    %% Desktop Interface Rendering
    C e4@-->|Populate Data Frame| E[📋 Master Ledger Workspace]
    D e5@-->|Populate Data Frame| E
    E e6@-->|Interactive Desktop View| F[User Verification Review Phase]
    
    %% Live Processing Ingestion Execution
    F e7@-->|Step 2: Trigger Action| G[Execute Live Ingestion Button]
    G e8@-->|Parallel Batch Pooling| H(yfinance Multi-Thread Engine)
    H e9@-->|Download 5d Pricing Windows| I[Calculate Closes & % Deltas]
    
    %% Downstream Document Output
    I e10@-->|Step 3: Render Metrics| J[Update Grid + Activate Charts]
    I e11@-->|Auto-Compile Binaries| K(src/pdf_generator.py)
    K e12@-->|Build Landscape Multi-Page Ledger| L[Nifty500_Master_Report.pdf]
    
    %% Secure Transmission Route
    J e13@-->|Step 4: Silent Dispatch| M[Dispatch PDF Report Button]
    L e14@-->|Step 4: Silent Dispatch| M
    M e15@-->|Extract Context via TOML Secrets| N{st.secrets gmail}
    N e16@-->|Route Secure TLS Packet| O(src/email_service.py)
    O e17@-->|Target Server: smtp.gmail.com| P["********@gmail.com"]

    %% Running Flow Animation Definitions
    e1@{ animate: true }
    e2@{ animate: true }
    e3@{ animate: true }
    e4@{ animate: true }
    e5@{ animate: true }
    e6@{ animate: true }
    e7@{ animate: true }
    e8@{ animate: true }
    e9@{ animate: true }
    e10@{ animate: true }
    e11@{ animate: true }
    e12@{ animate: true }
    e13@{ animate: true }
    e14@{ animate: true }
    e15@{ animate: true }
    e16@{ animate: true }
    e17@{ animate: true }

    %% Class Styling for Clean UI Nodes
    style E fill:#e1f5fe,stroke:#03a9f4,stroke-width:2px;
    style F fill:#fff9c4,stroke:#fbc02d,stroke-width:2px;
    style L fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px;
    style P fill:#ffebee,stroke:#c62828,stroke-width:2px;
```

---

## 🚀 Local Network Initialization

To spin up the server environment locally on port **`8501`**, execute the following sequence inside your project repository terminal:


### Boot Up the Streamlit Core Server
Run the platform using the explicit network flag to map the interface directly to port `8501`:

```bash
streamlit run app.py --server.port 8501 --server.address localhost
```

Once executed, open your desktop browser and navigate to the live deployment link:
🔗 **`http://localhost:8501`**

---

## ⚡ Operational Guidelines

1. **Phase 1 (Verification Standby):** On application boot, the master list of 500 scrips will instantly load onto the interactive desktop table grid. Use the inline search box to verify components or sectors before running calculations.
2. **Phase 2 (Live Sync):** Click **Execute Live Ingestion** in the sidebar. The system will leverage high-concurrency batch threads to map price deltas, paint color-coded trends (`🟢 Up` / `🔴 Down`), and generate a landscape PDF balance sheet.
3. **Phase 3 (Document Delivery):** Click **Dispatch PDF Report**. The core will match your binary workspace payload against your hidden `secrets.toml` recipients list and route the finished document out without exposing confidential data fields on-screen.
