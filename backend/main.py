import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from database import get_db, engine, Base
from models import Fund, Cohort, Cashflow, UnitMetrics

app = FastAPI(title="Capital Ops Dashboard", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.exists(FRONTEND_PATH):
    app.mount("/static", StaticFiles(directory=FRONTEND_PATH), name="static")


@app.on_event("startup")
async def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/")
async def index():
    return FileResponse(os.path.join(FRONTEND_PATH, "index.html"))


@app.get("/financing")
async def financing():
    return FileResponse(os.path.join(FRONTEND_PATH, "financing.html"))


@app.get("/unit-economics")
async def unit_economics():
    return FileResponse(os.path.join(FRONTEND_PATH, "unit-economics.html"))


@app.get("/api/fund/overview")
async def fund_overview(db: Session = Depends(get_db)):
    funds = db.query(Fund).all()
    
    if not funds:
        raise HTTPException(status_code=404, detail="No funds found")
    
    n = len(funds)
    total_deployed = sum(f.capital_deployed for f in funds)
    total_repaid = sum(f.principal_repaid for f in funds)
    total_exposure = sum(f.net_exposure for f in funds)
    avg_target = sum(f.target_irr for f in funds) / n
    avg_current = sum(f.current_irr for f in funds) / n
    
    return {
        "summary": {
            "total_capital_deployed": total_deployed,
            "total_principal_repaid": total_repaid,
            "total_net_exposure": total_exposure,
            "average_target_irr": round(avg_target, 1),
            "average_current_irr": round(avg_current, 1),
            "irr_variance": round(avg_target - avg_current, 1)
        },
        "funds": [{
            "id": f.id,
            "name": f.name,
            "capital_deployed": f.capital_deployed,
            "principal_repaid": f.principal_repaid,
            "net_exposure": f.net_exposure,
            "target_irr": f.target_irr,
            "current_irr": f.current_irr,
            "irr_achievement": round((f.current_irr / f.target_irr) * 100, 1)
        } for f in funds]
    }


@app.get("/api/fund/cohorts")
async def fund_cohorts(db: Session = Depends(get_db)):
    funds = db.query(Fund).all()
    
    out = []
    for fund in funds:
        cohorts = db.query(Cohort).filter(Cohort.fund_id == fund.id).order_by(Cohort.cohort_month).all()
        
        counts = {"healthy": 0, "at_risk": 0, "underperforming": 0}
        for c in cohorts:
            if c.health_status in counts:
                counts[c.health_status] += 1
        
        out.append({
            "fund_id": fund.id,
            "fund_name": fund.name,
            "health_summary": counts,
            "cohorts": [{"id": c.id, "cohort_month": c.cohort_month, "health_status": c.health_status} for c in cohorts]
        })
    
    return {"data": out}


@app.get("/api/fund/capital-deployment")
async def capital_deployment(db: Session = Depends(get_db)):
    cohorts = db.query(Cohort).all()
    
    by_month = {}
    for cohort in cohorts:
        deps = db.query(Cashflow).filter(Cashflow.cohort_id == cohort.id, Cashflow.flow_type == "deployment").all()
        for cf in deps:
            by_month[cohort.cohort_month] = by_month.get(cohort.cohort_month, 0) + abs(cf.amount)
    
    months = sorted(by_month.keys())
    deployments = [by_month[m] for m in months]
    cumulative = [sum(deployments[:i+1]) for i in range(len(months))]
    
    return {"months": months, "deployments": deployments, "cumulative": cumulative}


@app.get("/api/fund/cashflows")
async def cashflows(db: Session = Depends(get_db)):
    funds = db.query(Fund).all()
    
    out = []
    for fund in funds:
        cohorts = db.query(Cohort).filter(Cohort.fund_id == fund.id).order_by(Cohort.cohort_month).all()
        
        cohort_data = []
        for cohort in cohorts:
            cfs = db.query(Cashflow).filter(Cashflow.cohort_id == cohort.id).order_by(Cashflow.month).all()
            cohort_data.append({
                "cohort_id": cohort.id,
                "cohort_month": cohort.cohort_month,
                "health_status": cohort.health_status,
                "cashflows": [{"month": cf.month, "amount": cf.amount, "flow_type": cf.flow_type} for cf in cfs]
            })
        
        out.append({"fund_id": fund.id, "fund_name": fund.name, "cohorts": cohort_data})
    
    return {"data": out}


@app.get("/api/unit-economics")
async def unit_economics_data(db: Session = Depends(get_db)):
    funds = db.query(Fund).all()
    
    out = []
    for fund in funds:
        m = db.query(UnitMetrics).filter(UnitMetrics.fund_id == fund.id).first()
        if m:
            out.append({
                "fund_id": fund.id,
                "fund_name": fund.name,
                "cac_payback_months": m.cac_payback_months,
                "ltv_cac_3y": m.ltv_cac_3y,
                "ltv_cac_5y": m.ltv_cac_5y,
                "payback_status": "on_track" if m.cac_payback_months <= 15 else "delayed",
                "ltv_trajectory": [
                    {"year": 1, "ratio": round(m.ltv_cac_3y * 0.33, 2)},
                    {"year": 2, "ratio": round(m.ltv_cac_3y * 0.67, 2)},
                    {"year": 3, "ratio": m.ltv_cac_3y},
                    {"year": 4, "ratio": round((m.ltv_cac_3y + m.ltv_cac_5y) / 2, 2)},
                    {"year": 5, "ratio": m.ltv_cac_5y},
                ]
            })
    
    if out:
        avg_payback = sum(r["cac_payback_months"] for r in out) / len(out)
        avg_3y = sum(r["ltv_cac_3y"] for r in out) / len(out)
        avg_5y = sum(r["ltv_cac_5y"] for r in out) / len(out)
    else:
        avg_payback = avg_3y = avg_5y = 0
    
    return {
        "summary": {
            "average_cac_payback": round(avg_payback, 1),
            "average_ltv_cac_3y": round(avg_3y, 2),
            "average_ltv_cac_5y": round(avg_5y, 2),
            "payback_threshold": 15
        },
        "funds": out
    }


@app.get("/api/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
