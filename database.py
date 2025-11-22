# database.py
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///site_checks.db"
Base = declarative_base()


# Определение модели данных для сохранения результатов проверки
class CheckResult(Base):
    __tablename__ = 'check_results'

    id = Column(Integer, primary_key=True)
    url = Column(String, nullable=False)
    status_code = Column(Integer)
    response_time = Column(Float)  # Время в секундах
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_success = Column(Integer)  # 1 - да, 0 - нет

    def __repr__(self):
        return f"<CheckResult(url='{self.url}', status='{self.status_code}')>"


# Инициализация
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def save_result(url, status_code, response_time, is_success):
    """Сохраняет один результат проверки в БД."""
    session = SessionLocal()
    new_result = CheckResult(
        url=url,
        status_code=status_code,
        response_time=response_time,
        is_success=is_success
    )
    session.add(new_result)
    session.commit()
    session.close()


def get_last_checks(limit=10):
    """Возвращает последние результаты проверок."""
    session = SessionLocal()
    results = session.query(CheckResult).order_by(CheckResult.timestamp.desc()).limit(limit).all()
    session.close()
    return results