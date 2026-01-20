from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Fund(Base):
    __tablename__ = "fund"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    capital_deployed = Column(Float, nullable=False)
    principal_repaid = Column(Float, nullable=False)
    net_exposure = Column(Float, nullable=False)
    target_irr = Column(Float, nullable=False)
    current_irr = Column(Float, nullable=False)

    cohorts = relationship("Cohort", back_populates="fund", cascade="all, delete-orphan")
    unit_metrics = relationship("UnitMetrics", back_populates="fund", uselist=False, cascade="all, delete-orphan")


class Cohort(Base):
    __tablename__ = "cohort"

    id = Column(Integer, primary_key=True, index=True)
    fund_id = Column(Integer, ForeignKey("fund.id"), nullable=False)
    cohort_month = Column(String(7), nullable=False)
    health_status = Column(String(20), nullable=False)

    fund = relationship("Fund", back_populates="cohorts")
    cashflows = relationship("Cashflow", back_populates="cohort", cascade="all, delete-orphan")


class Cashflow(Base):
    __tablename__ = "cashflow"

    id = Column(Integer, primary_key=True, index=True)
    cohort_id = Column(Integer, ForeignKey("cohort.id"), nullable=False)
    month = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    flow_type = Column(String(20), nullable=False)

    cohort = relationship("Cohort", back_populates="cashflows")


class UnitMetrics(Base):
    __tablename__ = "unit_metrics"

    id = Column(Integer, primary_key=True, index=True)
    fund_id = Column(Integer, ForeignKey("fund.id"), nullable=False, unique=True)
    cac_payback_months = Column(Float, nullable=False)
    ltv_cac_3y = Column(Float, nullable=False)
    ltv_cac_5y = Column(Float, nullable=False)

    fund = relationship("Fund", back_populates="unit_metrics")
