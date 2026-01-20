# Capital Operations Dashboard

An investor-grade, database-backed dashboard that replaces Excel-based fund tracking by providing cohort-level visibility into capital deployment, repayment velocity, and IRR performance.

## Features

- **Financing Dashboard**: Capital at work, IRR performance, deployment charts, cohort health matrix, cashflow matrix
- **Unit Economics Dashboard**: CAC payback, LTV:CAC ratios, cohort LTV curves, payback threshold visualization
- **Real Database**: SQLite with SQLAlchemy ORM - no hardcoded JSON
- **Modern UI**: Dark theme, Chart.js visualizations, Tailwind CSS
- **Cloud Ready**: Deployable on Render, Railway, or Fly.io

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.10+, FastAPI, SQLAlchemy |
| Database | SQLite |
| Frontend | HTML, CSS (Tailwind CDN), JavaScript, Chart.js |

## Project Structure

```
/backend
  ├── main.py          # FastAPI application
  ├── database.py      # SQLAlchemy configuration
  ├── models.py        # ORM models
  ├── seed.py          # Data seeding script
  └── requirements.txt # Python dependencies

/frontend
  ├── index.html       # Landing page
  ├── financing.html   # Financing dashboard
  └── unit-economics.html  # Unit economics dashboard
```

## Local Development

### Prerequisites
- Python 3.10 or higher
- pip

### Setup & Run

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Seed the database with demo data
python seed.py

# Start the server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Access the Application

- **Home**: http://localhost:8000/
- **Financing Dashboard**: http://localhost:8000/financing
- **Unit Economics**: http://localhost:8000/unit-economics

### API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/fund/overview` | Fund summary metrics |
| `GET /api/fund/cohorts` | Cohort listing with health status |
| `GET /api/fund/capital-deployment` | Monthly deployment data |
| `GET /api/fund/cashflows` | Full cashflow matrix |
| `GET /api/unit-economics` | CAC/LTV metrics |

---

## Cloud Deployment

### Option 1: Render

1. Push code to GitHub
2. Go to [render.com](https://render.com) and create a new Web Service
3. Connect your GitHub repository
4. Configure:
   - **Build Command**: `cd backend && pip install -r requirements.txt && python seed.py`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3
5. Deploy

### Option 2: Railway

1. Push code to GitHub
2. Go to [railway.app](https://railway.app) and create a new project
3. Connect your GitHub repository
4. Add a `Procfile` in the backend folder:
   ```
   web: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
5. Set build settings:
   - **Root Directory**: `/backend`
   - **Build Command**: `pip install -r requirements.txt && python seed.py`
6. Deploy

### Option 3: Fly.io

1. Install flyctl: https://fly.io/docs/hands-on/install-flyctl/

2. Create `fly.toml` in the backend folder:
   ```toml
   app = "capital-ops-dashboard"
   primary_region = "ord"

   [build]
     builder = "paketobuildpacks/builder:base"

   [env]
     PORT = "8080"

   [http_service]
     internal_port = 8080
     force_https = true

   [[services]]
     http_checks = []
     internal_port = 8080
     protocol = "tcp"
   ```

3. Create `Procfile` in backend:
   ```
   web: uvicorn main:app --host 0.0.0.0 --port 8080
   ```

4. Deploy:
   ```bash
   cd backend
   fly auth login
   fly launch
   fly deploy
   ```

---

## Database Schema

### Tables

**fund**
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| name | String | Fund name |
| capital_deployed | Float | Total capital deployed |
| principal_repaid | Float | Principal returned |
| net_exposure | Float | Current exposure |
| target_irr | Float | Target IRR % |
| current_irr | Float | Actual IRR % |

**cohort**
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| fund_id | Integer | FK to fund |
| cohort_month | String | Format: YYYY-MM |
| health_status | String | healthy, at_risk, underperforming |

**cashflow**
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| cohort_id | Integer | FK to cohort |
| month | Integer | Month number (1-7) |
| amount | Float | Cash amount |
| flow_type | String | deployment, repayment, capped |

**unit_metrics**
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| fund_id | Integer | FK to fund |
| cac_payback_months | Float | CAC recovery period |
| ltv_cac_3y | Float | 3-year LTV:CAC ratio |
| ltv_cac_5y | Float | 5-year LTV:CAC ratio |

---

## License

MIT License - see [LICENSE](LICENSE) for details.
