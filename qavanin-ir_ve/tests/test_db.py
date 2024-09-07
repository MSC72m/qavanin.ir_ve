import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from pgvector.sqlalchemy import Vector
from database.models import Base, LawDocument, init_db, get_db, DatabaseInitializationError

# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_db():
    """Create a test database and tables for each test function."""
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)

    # Create a new session for each test
    with TestingSessionLocal() as session:
        yield session

    # Drop all tables after each test
    Base.metadata.drop_all(engine)


def test_law_document_creation(test_db):
    """Test creating a LawDocument instance."""
    document = LawDocument(
        content="Test legal document content",
        embedding=[0.1] * 384  # Assuming 384-dimensional embedding
    )
    test_db.add(document)
    test_db.commit()

    retrieved_doc = test_db.query(LawDocument).first()
    assert retrieved_doc.content == "Test legal document content"
    assert len(retrieved_doc.embedding) == 384
    assert retrieved_doc.created_at is not None


def test_law_document_update(test_db):
    """Test updating a LawDocument instance."""
    document = LawDocument(
        content="Original content",
        embedding=[0.1] * 384
    )
    test_db.add(document)
    test_db.commit()

    document.content = "Updated content"
    test_db.commit()

    updated_doc = test_db.query(LawDocument).first()
    assert updated_doc.content == "Updated content"
    assert updated_doc.updated_at is not None


def test_init_db(monkeypatch):
    """Test the init_db function."""

    def mock_execute(self, statement, *args, **kwargs):
        if "CREATE EXTENSION" in str(statement):
            return None
        if "SELECT extname" in str(statement):
            class MockResult:
                def fetchone(self):
                    return ('vector',)

            return MockResult()

    monkeypatch.setattr("sqlalchemy.engine.base.Connection.execute", mock_execute)

    # This should not raise an exception
    init_db()


def test_init_db_error(monkeypatch):
    """Test the init_db function when pgvector is not installed."""

    def mock_execute(self, statement, *args, **kwargs):
        if "CREATE EXTENSION" in str(statement):
            return None
        if "SELECT extname" in str(statement):
            class MockResult:
                def fetchone(self):
                    return None

            return MockResult()

    monkeypatch.setattr("sqlalchemy.engine.base.Connection.execute", mock_execute)

    with pytest.raises(DatabaseInitializationError):
        init_db()


def test_get_db():
    """Test the get_db function."""
    db_generator = get_db()
    db = next(db_generator)
    assert db is not None
    try:
        next(db_generator)
    except StopIteration:
        pass  # This is expected behavior


if __name__ == "__main__":
    pytest.main()