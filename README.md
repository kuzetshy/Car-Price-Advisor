# Car Price Advisor 🚗📉

An automated Machine Learning ecosystem designed to collect automotive market data, manage it within a robust relational database, and leverage gradient boosting to accurately predict car market values.

The project is built using Object-Oriented Programming (OOP) principles and clean modular architecture, moving away from monolithic local scripts into a scalable production-ready structure.

## 🎯 Project Goals & Capabilities
- **Automated Web Scraping:** Robust parsing scripts to extract real-time vehicle data.
- **Production-Ready Database Layer:** Fully migrated from raw files to **PostgreSQL**, managed via **SQLAlchemy ORM** using the Repository (DAO) pattern.
- **Containerized Infrastructure:** Production database environment orchestrated using **Docker & Docker Compose**.
- **Robust ML Pipeline:** Fully automated pipeline covering data loading directly from PostgreSQL, advanced preprocessing (handling anomalies, currency normalization), and feature engineering.

---

## 🏗️ Architecture & Project Structure

## 🏗️ Project Structure

```text
Car-Price-Advisor/
├── app/                       # Main application package
│   ├── api/                   # Web interface layer (FastAPI endpoints and schemas)
│   │   ├── endpoints.py       # Request handling and model inference logic
│   │   └── schemas.py         # Inbound data validation using Pydantic
│   ├── database/              # Database infrastructure (PostgreSQL + SQLAlchemy)
│   │   ├── models.py          # Database tables definition (ORM models)
│   │   ├── repository.py      # Repository (DAO) pattern implementation for data access
│   │   └── session.py         # Database engine and sessionmaker configuration
│   ├── ml/                    # Machine Learning components
│   │   ├── preprocessing.py   # OOP classes for data loading, cleaning, and feature engineering
│   │   └── train_pipeline.py  # Orchestration script to trigger CatBoost training
│   ├── services/              # Core business logic
│   │   └── parser.py          # Web scraping module for listing collection
│   └── utils/                 # Shared helper utilities
│       ├── config_loader.py   # Secure YAML configuration reader logic
│       └── logger.py          # Centralized logging configuration
├── config/                    # Configuration management directory
│   ├── settings.example.yaml  # Shared structural template for public settings
│   └── settings.yaml          # Local runtime config with sensitive credentials (git-ignored)
├── data/                      # Local data storage (git-ignored)
│   ├── cleaned/               # Processed datasets optimized for training
│   └── raw/                   # Raw files and local data caches
├── models/                    # Directory for storing trained model binaries (.cbm)
├── notebooks/                 # Jupyter notebooks for R&D and EDA
├── reports/                   # Performance evaluation artifacts and analytics
│   ├── catboost_info/         # Detailed metric logs generated during training
│   └── figures/               # Generated HTML charts and visualizations
├── scripts/                   # Operational automation scripts
│   └── run_scraping.py        # Independent entry point for scheduled scraping
├── .env                       # Secret environment variables and DB passwords (git-ignored)
├── Dockerfile                 # Application container build instructions
├── docker-compose.yml         # Docker orchestration manifest for database services
├── main.py                    # Main application entry point
└── requirements.txt           # Managed project dependencies list


🗺️ Project Roadmap
[x] Phase 1: Architecture & OOP Refactoring (Rebuilt project layout, implemented classes for loaders and preprocessors)
[x] Phase 2: PostgreSQL Migration & Docker Setup (Moved from SQLite, containerized database, integrated SQLAlchemy)
[ ] Phase 3: Code Consolidation & Automated Ingestion (Transfer remaining inference/advisor logic from notebooks, set up Cron for the scraper)
[ ] Phase 4: Production Model Tracking (Resolve model binary deployment limits on Git)
[ ] Phase 5: FastAPI Deployment (Build endpoints for /predict and /advisor)
[ ] Phase 6: Advanced Text Analytics (LLM Layer) (Extract features from descriptions, build an AI Advisor)
[ ] Phase 7: Web User Interface (Build a website or dashboard to interact with the API)


---

⚙️ Quick Start:
1) Configure Environment:
    cp .env.example .env
    cp config/settings.example.yaml config/settings.yaml

2) Launch Infrastructure:
    docker-compose up -d

3) Install Dependencies:
    pip install -r requirements.txt

4) Run Ingestion:
    python scripts/run_scraping.py

5) Run ML Pipeline:
    python -m app.ml.train_pipeline

