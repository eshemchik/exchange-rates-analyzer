from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import String
from sqlalchemy import Float


class Base(DeclarativeBase):
    pass


class Rates(Base):
    __tablename__ = "rates"
    base_currency: Mapped[str] = mapped_column(String(20), primary_key=True)
    date: Mapped[str] = mapped_column(String(20), primary_key=True)
    currency: Mapped[str] = mapped_column(String(20), primary_key=True)
    rate: Mapped[float] = mapped_column(Float)


class AnalysisResults(Base):
    __tablename__ = "analysis_results"
    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    currency: Mapped[str] = mapped_column(String(20), primary_key=True)
    base_currency: Mapped[str] = mapped_column(String(20))
    rate_change_percents: Mapped[float] = mapped_column(Float)


def init_db(db):
    # Create table if not exists.
    Rates.__table__.create(bind=db.engine, checkfirst=True)
    AnalysisResults.__table__.create(bind=db.engine, checkfirst=True)
