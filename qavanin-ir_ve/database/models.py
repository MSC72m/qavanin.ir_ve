import os
from dotenv import load_dotenv
import logging
from sqlalchemy import create_engine, Column, Integer, Text, DateTime, Index, text, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from sqlalchemy.schema import DDL
from pgvector.sqlalchemy import Vector
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

Base = declarative_base()




class LawDocument(Base):
    __tablename__ = 'law_documents'

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(384), nullable=False)  # Adjust dimension as needed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Index for faster similarity search
    __table_args__ = (
        Index('idx_law_documents_embedding', 'embedding', postgresql_using='ivfflat'),
    )

    def __repr__(self):
        return f"<LawDocument(id={self.id}, content='{self.content[:50]}...')>"

    @classmethod
    def from_dict(cls, data: dict) -> 'LawDocument':
        return cls(
            content=data['content'],
            embedding=data['embedding'],  # Now it's a native PostgreSQL vector
        )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'content': self.content,
            'embedding': self.embedding,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://test:test@localhost:5432/qavanin_db")

# Create engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db(db_url):
    engine = create_engine(db_url)
    with engine.connect() as connection:
        connection.execute(DDL('CREATE EXTENSION IF NOT EXISTS vector'))

    # Create all tables
    Base.metadata.create_all(engine)


def create_table_if_not_exists():
    inspector = inspect(engine)
    if 'law_documents' not in inspector.get_table_names():
        Base.metadata.create_all(bind=engine)
        logger.info("Table 'law_documents' created successfully.")
    else:
        logger.info("Table 'law_documents' already exists.")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_pgvector_extension():
    with engine.connect() as conn:
        try:
            result = conn.execute(text("SELECT extname FROM pg_extension WHERE extname = 'vector';"))
            if result.fetchone():
                logger.info("pgvector extension is installed.")
            else:
                logger.warning("pgvector extension is not installed. Please install it to use the vector type.")
        except Exception as e:
            logger.error(f"Error checking pgvector extension: {e}")


if __name__ == "__main__":
    db_url = "postgresql://test:test@localhost:5432/qavanin_db"
    try:
        init_db(db_url)
        create_table_if_not_exists()
        check_pgvector_extension()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
