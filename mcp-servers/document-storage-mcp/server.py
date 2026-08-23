import os
import uuid
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
from mcp.server import MCPServer

load_dotenv()

mcp = MCPServer("document-storage-mcp")

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


@mcp.tool()
def save_report(query: str, claim: str, source: str, tokens: int = 0, cost: float = 0.0) -> dict:
    report_id = str(uuid.uuid4())[:8]

    session = SessionLocal()
    report = Report(
        id=report_id,
        query=query,
        claim=claim,
        source=source,
        tokens=tokens,
        cost=cost,
        created_at=datetime.utcnow()
    )
    session.add(report)
    session.commit()
    session.close()

    return {"report_id": report_id, "status": "saved"}


@mcp.tool()
def get_report(report_id: str) -> dict:
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


@mcp.tool()
def list_reports() -> dict:
    session = SessionLocal()
    reports = session.query(Report).order_by(Report.created_at.desc()).all()
    session.close()

    return {
        "reports": [
            {"id": r.id, "query": r.query, "created_at": r.created_at.isoformat()}
            for r in reports
        ]
    }


if __name__ == "__main__":
    mcp.run()