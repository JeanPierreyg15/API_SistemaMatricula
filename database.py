from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase,sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()
class Base(DeclarativeBase):
    "Clase base de SQLALCHEMY"

def _argumentos_sqlite() -> dict:
    return {"check_same_thread": False} if os.getenv("DATABASE_URL","sqlite:///./matricula.db").startswith("sqlite") else {}

engine = create_engine(os.getenv("DATABASE_URL","sqlite:///./matricula.db"),connect_args=_argumentos_sqlite(),pool_pre_ping=True)
sessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)

def get_db():
    db = sessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()