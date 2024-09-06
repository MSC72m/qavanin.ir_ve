import pytest
from unittest.mock import Mock, patch
from database.db_oprations import get_db_session, get_closest_document, insert_document, get_document_by_id, update_document, delete_document, get_document_count

@pytest.fixture
def mock_session():
    """Fixture that returns a mock SQLAlchemy session."""
    return Mock()

def test_get_db_session(mock_session):
    """Test that the get_db_session function can create a database session correctly."""
    with patch("db_operations.Session", return_value=mock_session):
        with get_db_session() as session:
            assert session == mock_session

def test_get_closest_document(mock_session):
    """Test that the get_closest_document function can retrieve the closest documents to a given query embedding correctly."""
    mock_session.query().order_by().limit().all.return_value = [(1, "Test document 1"), (2, "Test document 2")]
    with patch("db_operations.Session", return_value=mock_session):
        documents = get_closest_document([0.1, 0.2, 0.3], 2)
        assert documents == [{"id": 1, "content": "Test document 1"}, {"id": 2, "content": "Test document 2"}]

def test_insert_document(mock_session):
    """Test that the insert_document function can insert a new document into the database correctly."""
    with patch("db_operations.Session", return_value=mock_session):
        insert_document("Test document", [0.1, 0.2, 0.3])
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

def test_get_document_by_id(mock_session):
    """Test that the get_document_by_id function can retrieve a document from the database by its ID correctly."""
    mock_session.query().options().filter_by().first.return_value = Mock(id=1, content="Test document")
    with patch("db_operations.Session", return_value=mock_session):
        document = get_document_by_id(1)
        assert document == {"id": 1, "content": "Test document"}

def test_update_document(mock_session):
    """Test that the update_document function can update an existing document in the database correctly."""
    mock_session.query().filter().first.return_value = Mock(id=1, content="Test document", embedding=[0.1, 0.2, 0.3])
    with patch("db_operations.Session", return_value=mock_session):
        updated_document = update_document(1, "Updated test document", [0.4, 0.5, 0.6])
        assert updated_document["content"] == "Updated test document"
        mock_session.commit.assert_called_once()

def test_delete_document(mock_session):
    """Test that the delete_document function can delete a document from the database correctly."""
    mock_session.query().filter().first.return_value = Mock(id=1)
    with patch("db_operations.Session", return_value=mock_session):
        result = delete_document(1)
        assert result == True
        mock_session.delete.assert_called_once()
        mock_session.commit.assert_called_once()

def test_get_document_count(mock_session):
    """Test that the get_document_count function can retrieve the total number of documents in the database correctly."""
    mock_session.query().count.return_value = 10
    with patch("db_operations.Session", return_value=mock_session):
        count = get_document_count()
        assert count == 10
