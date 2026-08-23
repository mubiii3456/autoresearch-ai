import os
import uuid
from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Report(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True)
    query = Column(String)
    claim = Column(String)
    source = Column(String)
    tokens = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(engine)


class SaveReportRequest(BaseModel):
    query: str
    claim: str
    source: str
    tokens: int = 0
    cost: float = 0.0


@app.post("/reports")
def save_report(request: SaveReportRequest):
    report_id = str(uuid.uuid4())[:8]

    session = SessionLocal()
    report = Report(
        id=report_id,
        query=request.query,
        claim=request.claim,
        source=request.source,
        tokens=request.tokens,
        cost=request.cost,
        created_at=datetime.utcnow()
    )
    session.add(report)
    session.commit()
    session.close()

    return {"report_id": report_id, "status": "saved"}


@app.get("/reports/{report_id}")
def get_report(report_id: str):
    session = SessionLocal()
    report = session.query(Report).filter(Report.id == report_id).first()
    session.close()

    if not report:
        return {"error": f"Report '{report_id}' not found"}

    return {
        "id": report.id,
        "query": report.query,
        "claim": report.claim,
        "source": report.source,
        "tokens": report.tokens,
        "cost": report.cost,
        "created_at": report.created_at.isoformat()
    }


@app.get("/reports")
def list_reports():
    session = SessionLocal()
    reports = session.query(Report).order_by(Report.created_at.desc()).all()
    session.close()

    return {
        "reports": [
            {"id": r.id, "query": r.query, "created_at": r.created_at.isoformat()}
            for r in reports
        ]
    }


@app.get("/health")
def health():
    return {"status": "ok"}