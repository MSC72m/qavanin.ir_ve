import pytest
from unittest.mock import Mock, patch
from database.models import LawDocument, init_db, create_table_if_not_exists, get_db, check_pgvector_extension

@pytest.fixture
def mock_engine():
    """Fixture that returns a mock SQLAlchemy engine."""
    return Mock()

@pytest.fixture
def mock_connection(mock_engine):
    """Fixture that returns a mock SQLAlchemy connection."""
    return mock_engine.connect.return_value

@pytest.fixture
def mock_inspector(mock_engine):
    """Fixture that returns a mock SQLAlchemy inspector."""
    return Mock()

def test_law_document_from_dict():
    """Test that the LawDocument class can be created from a dictionary correctly."""
    data = {"content": "Test document", "embedding": [0.1, 0.2, 0.3]}
    document = LawDocument.from_dict(data)
    assert document.content == "Test document"
    assert document.embedding == [0.1, 0.2, 0.3]

def test_law_document_to_dict():
    """Test that the LawDocument class can be converted to a dictionary correctly."""
    document = LawDocument(content="Test document", embedding=[0.1, 0.2, 0.3])
    data = document.to_dict()
    assert data["content"] == "Test document"
    assert data["embedding"] == [0.1, 0.2, 0.3]

def test_init_db(mock_engine, mock_connection):
    """Test that the init_db function can create the pgvector extension and all tables correctly."""
    with patch("models.create_engine", return_value=mock_engine):
        init_db("test_db_url")
        mock_connection.execute.assert_called_once_with(DDL('CREATE EXTENSION IF NOT EXISTS vector'))
        mock_engine.metadata.create_all.assert_called_once()

def test_create_table_if_not_exists(mock_engine, mock_inspector):
    """Test that the create_table_if_not_exists function can create the 'law_documents' table if it doesn't already exist."""
    mock_inspector.get_table_names.return_value = []
    with patch("models.inspect", return_value=mock_inspector):
        create_table_if_not_exists()
        mock_engine.metadata.create_all.assert_called_once()

def test_get_db(mock_engine):
    """Test that the get_db function can provide a database session for use in a context manager."""
    with patch("models.SessionLocal", return_value=Mock()) as mock_session_local:
        with get_db() as db:
            assert db == mock_session_local.return_value

def test_check_pgvector_extension(mock_engine, mock_connection):
    """Test that the check_pgvector_extension function can check if the pgvector extension is installed in the database."""
    mock_connection.execute.return_value.fetchone.return_value = True
    with patch("models.engine", mock_engine):
        check_pgvector_extension()
        mock_connection.execute.assert_called_once_with(text("SELECT extname FROM pg_extension WHERE extname = 'vector';"))
