# 📊 Nifty 500 Market Performance Enterprise Workspace

A production-grade Streamlit terminal engineered to map daily market trends across all 500 Nifty constituents. This application follows a strict **Verification-First structural framework**, ensuring you can inspect the base equity index layout on your desktop screen before compiling the ReportLab accounting ledger and initiating downstream email operations via secure SMTP.

## About
Production-grade **Autonomous Financial Data Agent Workspace** built with **Streamlit** for **Nifty 500** constituents with automated reporting and data ingestion capabilities.

## ⭐ Show Your Support
If you like the UI design, dual-mode system architecture, or automated financial data engineering behind **Nifty 500 Market Performance Enterprise Workspace**, please consider giving this repository a **Star ⭐** on GitHub! It helps showcase this work and motivates future builds.


<img src="assets/desktop.png" width="100%" alt="Desktop Preview">

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
    %% Dual Entry Modes: Manual UI vs. Automated Scheduled Pipeline
    A[app.py Manual UI Boot] e1@-->|Step 1: On-Init Standby| B(src/data_engine.py: fetch_master_list)
    AUTO[GitHub Actions: Tue–Fri 5:00 PM IST / Manual Dispatch] e18@-->|Headless Cron Trigger| CRON(cron_job.py: Mon–Today Window)
    CRON e19@-->|Load Master Index| B

    %% Master List Data Sources
    B e2@-->|Pathway 1: Relative Disk| C{data/ind_nifty500list.csv}
    B e3@-->|Pathway 2: High-Availability Mirror| D[Raw GitHub CDN Stream]
    
    %% Manual Desktop Interface Rendering
    C e4@-->|Populate UI Frame| E[📋 Master Ledger Workspace]
    D e5@-->|Populate UI Frame| E
    E e6@-->|Interactive Desktop View| F[User Verification Review Phase]
    
    %% Live Processing Ingestion Execution (Both Modes)
    F e7@-->|Step 2: Manual Trigger| G[Execute Live Ingestion Button]
    G e8@-->|Parallel Batch Pooling| H(yfinance Multi-Thread Engine)
    CRON e20@-->|Automated Batch Pooling| H
    H e9@-->|Download Pricing Windows| I[Calculate Closes, Deltas & ₹ Filters]
    
    %% Downstream Document Output
    I e10@-->|Step 3: Render UI Metrics| J[Update Grid + Activate Charts]
    I e11@-->|Compile PDF Ledger| K(src/pdf_generator.py)
    K e12@-->|Build Multi-Page Report| L[Nifty500_Filtered / Automated_Report.pdf]
    
    %% Secure Single-Dispatch BCC Transmission Route
    J e13@-->|Step 4: Manual Dispatch| M[Dispatch PDF Report Button]
    L e14@-->|Attach Report Payload| M
    L e21@-->|Automated Headless Dispatch| O(src/email_service.py: Single BCC)
    M e15@-->|Read TOML Secrets| N{st.secrets gmail}
    N e16@-->|Route Secure TLS Packet| O
    CRON e22@-->|Read GitHub Secrets| O
    O e17@-->|Port 587 TLS: Single Email to All BCC| P["From/To: Sender | Hidden BCC: 1–100 Recipients"]

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
    e18@{ animate: true }
    e19@{ animate: true }
    e20@{ animate: true }
    e21@{ animate: true }
    e22@{ animate: true }

    %% Class Styling for Clean UI Nodes
    style AUTO fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px;
    style CRON fill:#ede7f6,stroke:#512da8,stroke-width:2px;
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

## ⚠️ Financial & Operational Disclaimer

For educational and research purposes only; not financial advice. Market data via `yfinance` may be delayed. Users must manage their own local credentials and comply with platform terms.

## ⭐ Support & Contribution

If you clone, test, or build upon this repository, please consider giving it a **Star (⭐)** on GitHub—it helps others discover the project and supports continued development.

* **Found a bug or have an idea?** Open an [Issue](https://github.com).
* **Want to improve the code?** Feel free to **Fork** this repository and submit a Pull Request.
Use code with caution.
Would you like me to paste the entire complete README.md from top to bottom with everything already in the exact right order so you can copy-paste the whole file at once?

* **Lead Architect & Developer:** [Srinivasta](https://github.com/SRINIVASTA)

### 🌐 Let’s Connect

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/srinivas-t-a-557637119/)
[![Kaggle](https://img.shields.io/badge/Kaggle-20BEFF?style=for-the-badge&logo=kaggle&logoColor=white)](https://www.kaggle.com/srinivasta)
[![Email](https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:tasrinivass@gmail.com)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/srinivasta)
[![Website](https://img.shields.io/badge/Website-000000?style=for-the-badge&logo=website&logoColor=white)](https://srinivasta.github.io)
