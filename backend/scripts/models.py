from sqlalchemy import create_engine, Column, Integer, String, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+pymysql://ovdr_developer:123456@172.19.108.9/OVDR"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Clothing(Base):
    __tablename__ = "Clothing"

    cid = Column(Integer, primary_key=True, index=True)
    category = Column(Enum("tops", "bottoms", "dresses"), nullable=False)
    cloth_path = Column(String(255), nullable=False)  # image path