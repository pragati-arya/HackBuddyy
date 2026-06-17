from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL")

# FIX: Render's managed Postgres gives you a "postgres://" URL, but
# SQLAlchemy 1.4+ only accepts "postgresql://". If your DATABASE_URL came
# straight from Render's dashboard without editing, this is very likely
# why the app fails to even start.
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# FIX: if the env var is missing entirely, create_engine(None) crashes on
# import and takes down the whole app (every route, including "/").
# Fail loudly with a clear message instead of a cryptic traceback, and
# fall back to a local SQLite file so the app can still boot for local dev.
if not DATABASE_URL:
    print("[database] WARNING: DATABASE_URL is not set. Falling back to local SQLite (hackbuddy.db).")
    DATABASE_URL = "sqlite:///./hackbuddy.db"

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# FIX: pool_pre_ping checks the connection is alive before using it,
# and pool_recycle proactively replaces connections older than 5 minutes.
# Render's free Postgres tier drops idle connections; without this, the
# first request after any idle period throws a stale-connection error,
# which looks exactly like intermittent "backend not running".
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()
