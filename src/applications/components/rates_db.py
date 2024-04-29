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
    start_date: Mapped[str] = mapped_column(String(20))
    end_date: Mapped[str] = mapped_column(String(20))
    start_rate: Mapped[float] = mapped_column(Float())
    end_rate: Mapped[float] = mapped_column(Float())
    rate_change_percents: Mapped[float] = mapped_column(Float())


class RatesDAO:
    def __init__(self, db):
        self.db = db
        Rates.__table__.create(bind=db.engine, checkfirst=True)
        AnalysisResults.__table__.create(bind=db.engine, checkfirst=True)

    def read_analysis_results(self, analysis_id):
        return self.db.session.query(AnalysisResults).filter_by(id=analysis_id)

    def read_rates(self, base_currency, date):
        return self.db.session.query(Rates).filter_by(
            base_currency=base_currency, date=date
        )

    def write_analysis_results(self, entries):
        for entry in entries:
            # clear existing results to override
            self.db.session.query(AnalysisResults).filter_by(
                id=entry.id, currency=entry.currency, base_currency=entry.base_currency,
                rate_change_percents=entry.rate_change_percents
            ).delete()
            self.db.session.add(entry)
        self.db.session.commit()

    def write_rates(self, entries):
        for entry in entries:
            # clear existing results to override
            self.db.session.query(Rates).filter_by(
                base_currency=entry.base_currency, date=entry.date, currency=entry.currency
            ).delete()
            self.db.session.add(entry)
        self.db.session.commit()

