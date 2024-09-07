import os
from dotenv import load_dotenv
import logging
from sqlalchemy import create_engine, Column, Integer, Text, DateTime, Index, text, inspect
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from sqlalchemy.schema import DDL
from pgvector.sqlalchemy import Vector

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Retrieve database configuration from environment variables
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")

# Construct database URL
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost:5432/{POSTGRES_DB}"

# Create SQLAlchemy base class
Base = declarative_base()


class LawDocument(Base):
    """
    Represents a legal document in the database.

    Attributes:
        id (int): The primary key of the document.
        content (str): The text content of the document.
        embedding (Vector): The vector embedding of the document for similarity search.
        created_at (DateTime): The timestamp when the document was created.
        updated_at (DateTime): The timestamp when the document was last updated.
    """
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


# Create engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)


class DatabaseInitializationError(Exception):
    """Custom exception for database initialization errors."""
    pass


def init_db():
    """
    Initializes the database by creating the pgvector extension and all tables.

    This function performs the following steps:
    1. Creates the pgvector extension if it doesn't exist.
    2. Checks if the 'law_documents' table exists, creates it if it doesn't.
    3. Verifies that the pgvector extension is properly installed.

    Raises:
        DatabaseInitializationError: If any step of the initialization process fails.
    """
    try:
        with engine.connect() as connection:
            # Create pgvector extension
            logger.info("Attempting to create pgvector extension...")
            connection.execute(DDL('CREATE EXTENSION IF NOT EXISTS vector'))
            logger.info("pgvector extension created or already exists.")

            # Check if the table exists
            inspector = inspect(engine)
            if 'law_documents' not in inspector.get_table_names():
                logger.info("Table 'law_documents' does not exist. Creating it...")
                Base.metadata.create_all(engine)
                logger.info("Table 'law_documents' created successfully.")
            else:
                logger.info("Table 'law_documents' already exists.")

            # Check pgvector extension
            result = connection.execute(text("SELECT extname FROM pg_extension WHERE extname = 'vector';"))
            if result.scalar():  # Using scalar to check for a single value
                logger.info("pgvector extension is properly installed.")
            else:
                raise DatabaseInitializationError(
                    "pgvector extension is not installed. Please install it to use the vector type.")

    except Exception as e:
        logger.error(f"Error during database initialization: {str(e)}")
        raise DatabaseInitializationError(f"Failed to initialize database: {str(e)}") from e



def get_db():
    """
    Provides a database session for use in a context manager.

    Yields:
        Session: A SQLAlchemy database session.

    Usage:
        with get_db() as db:
            # Use the database session
            db.query(...)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    try:
        init_db()
        logger.info("Database initialized successfully.")
    except DatabaseInitializationError as e:
        logger.error(f"Database initialization failed: {str(e)}")
    except Exception as e:
        logger.critical(f"Unexpected error during database initialization: {str(e)}")