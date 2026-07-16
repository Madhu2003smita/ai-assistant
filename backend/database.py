"""
SQLAlchemy database setup.
Uses SQLite by default (easy local dev).
Set DATABASE_URL env var for Postgres/MySQL in production.
  e.g.  DATABASE_URL=postgresql+psycopg2://user:pass@localhost/hcp_crm
        DATABASE_URL=mysql+pymysql://user:pass@localhost/hcp_crm
"""

import os

from sqlalchemy import Column, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hcp_crm.db")


connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(String(36), primary_key=True, index=True)
    hcp_name = Column(String(255), nullable=False, default="")
    interaction_type = Column(String(100), default="Meeting")
    date = Column(String(20), default="")
    time = Column(String(20), default="")
    attendees = Column(Text, default="")
    topics_discussed = Column(Text, default="")
    materials_shared = Column(Text, default="")
    samples_distributed = Column(Text, default="")
    hcp_sentiment = Column(String(50), default="Neutral")
    outcomes = Column(Text, default="")
    follow_up_actions = Column(Text, default="")
    ai_summary = Column(Text, default="")
    ai_entities = Column(Text, default="{}")   
    created_at = Column(String(30), default="")
    updated_at = Column(String(30), default="")


def init_db() -> None:
    """Create all tables if they do not exist."""
    Base.metadata.create_all(bind=engine)
