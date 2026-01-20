import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import engine, Base, SessionLocal
from models import Fund, Cohort, Cashflow, UnitMetrics


def seed():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Fund 1: Growth Capital
        gcf = Fund(
            name="Growth Capital Fund I",
            capital_deployed=12500000.00,
            principal_repaid=4200000.00,
            net_exposure=8300000.00,
            target_irr=18.0,
            current_irr=16.4
        )
        db.add(gcf)
        db.flush()
        
        db.add(UnitMetrics(
            fund_id=gcf.id,
            cac_payback_months=14.2,
            ltv_cac_3y=2.8,
            ltv_cac_5y=4.1
        ))
        
        gcf_cohorts = [
            ("2024-01", "healthy"),
            ("2024-02", "healthy"),
            ("2024-03", "at_risk"),
            ("2024-04", "healthy"),
            ("2024-05", "underperforming"),
            ("2024-06", "healthy"),
        ]
        
        cf_patterns = {
            "healthy": [
                (1, -100000, "deployment"),
                (2, -50000, "deployment"),
                (3, 15000, "repayment"),
                (4, 18000, "repayment"),
                (5, 22000, "repayment"),
                (6, 25000, "repayment"),
                (7, 28000, "capped"),
            ],
            "at_risk": [
                (1, -100000, "deployment"),
                (2, -75000, "deployment"),
                (3, 8000, "repayment"),
                (4, 10000, "repayment"),
                (5, 12000, "repayment"),
                (6, 14000, "repayment"),
                (7, 15000, "repayment"),
            ],
            "underperforming": [
                (1, -100000, "deployment"),
                (2, -80000, "deployment"),
                (3, 5000, "repayment"),
                (4, 6000, "repayment"),
                (5, 7000, "repayment"),
                (6, 8000, "repayment"),
                (7, 9000, "repayment"),
            ],
        }
        
        for month_str, status in gcf_cohorts:
            c = Cohort(fund_id=gcf.id, cohort_month=month_str, health_status=status)
            db.add(c)
            db.flush()
            
            for m, amt, ftype in cf_patterns[status]:
                db.add(Cashflow(cohort_id=c.id, month=m, amount=amt, flow_type=ftype))
        
        # Fund 2: Venture Debt
        vdf = Fund(
            name="Venture Debt Fund II",
            capital_deployed=8750000.00,
            principal_repaid=2100000.00,
            net_exposure=6650000.00,
            target_irr=22.0,
            current_irr=19.8
        )
        db.add(vdf)
        db.flush()
        
        db.add(UnitMetrics(
            fund_id=vdf.id,
            cac_payback_months=11.5,
            ltv_cac_3y=3.2,
            ltv_cac_5y=4.8
        ))
        
        vdf_cohorts = [
            ("2024-01", "healthy"),
            ("2024-02", "at_risk"),
            ("2024-03", "healthy"),
            ("2024-04", "healthy"),
            ("2024-05", "healthy"),
            ("2024-06", "at_risk"),
        ]
        
        for month_str, status in vdf_cohorts:
            c = Cohort(fund_id=vdf.id, cohort_month=month_str, health_status=status)
            db.add(c)
            db.flush()
            
            for m, amt, ftype in cf_patterns[status]:
                scaled = int(amt * 0.7)
                db.add(Cashflow(cohort_id=c.id, month=m, amount=scaled, flow_type=ftype))
        
        db.commit()
        print("Done. Seeded 2 funds, 12 cohorts, 84 cashflows.")
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
