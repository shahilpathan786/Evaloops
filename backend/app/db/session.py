from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import Session , sessionmaker
from app.core.config import getAppConfig
from typing import Generator



Base = declarative_base()

config = getAppConfig()
engine = create_engine(config.database_url)

sessionLocal = sessionmaker(autoflush=False , autocommit = False , bind=engine, expire_on_commit=False)

def get_db() -> Generator[Session , None , None]:
    db = sessionLocal()

    try:
        yield db
    finally:
        db.close()
