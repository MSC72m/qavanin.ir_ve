from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from typing import List, Optional
import numpy as np
import logging
from .models import LawDocument as law_documents, engine
from contextlib import contextmanager

logger = logging.getLogger(__name__)


@contextmanager
def get_db_session():
    """
    Context manager for handling database sessions.

    This function creates a new database session, yields it, and ensures proper
    commit, rollback, and closure of the session.

    Yields:
        Session: An active SQLAlchemy database session.

    Raises:
        SQLAlchemyError: If any database-related error occurs during the session.
    """
    session = Session(bind=engine)
    try:
        yield session
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        session.close()


def get_closest_document(query_embedding: List[float], limit: int) -> List[dict]:
    """
    Retrieves the closest documents to a given query embedding.

    Args:
        query_embedding (List[float]): The embedding vector of the query.
        limit (int): The maximum number of documents to retrieve.

    Returns:
        List[dict]: A list of dictionaries containing the id and content of the closest documents.

    Note:
        This function uses L2 distance to measure similarity between embeddings.
    """
    with get_db_session() as session:
        try:
            closest_documents = session.query(law_documents.id, law_documents.content).order_by(
                law_documents.embedding.l2_distance(query_embedding)
            ).limit(limit).all()

            logger.debug(f"Closest documents fetched: {closest_documents}")

            if not closest_documents:
                logger.warning(f"No documents found within the limit of {limit}.")

            return [{"id": doc.id, "content": doc.content} for doc in closest_documents]
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_closest_document: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in get_closest_document: {str(e)}")
            return []


def insert_document(content, embeds):
    """
    Inserts a new document into the database.

    Args:
        content (str): The content of the document.
        embeds (List[float]): The embedding vector of the document.

    Note:
        This function converts the embedding to a list of floats before insertion.
    """
    embeds_list = [float(x) for x in embeds]
    with get_db_session() as session:
        try:
            document = law_documents(
                content=content,
                embedding=embeds_list,
                updated_at=None
            )
            session.add(document)
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error inserting document: {e}")
        except Exception as e:
            session.rollback()
            logger.error(f"Unexpected error inserting document: {e}")


def get_document_by_id(document_id: int):
    """
    Retrieves a document from the database by its ID.

    Args:
        document_id (int): The ID of the document to retrieve.

    Returns:
        dict: A dictionary containing the document's id and content, or None if not found.
    """
    with get_db_session() as session:
        try:
            # Load all attributes eagerly
            document = session.query(law_documents).options(joinedload('*')).filter_by(id=document_id).first()
            if not document:
                return None
            document_data = {
                "id": document.id,
                "content": document.content
            }
            return document_data
        except Exception as e:
            logger.error(f"Error retrieving document: {str(e)}")
            return None



def update_document(document_id: int, content: str, embedding: list[float]):
    """
    Updates an existing document in the database.

    Args:
        document_id (int): The ID of the document to update.
        content (str): The new content of the document.
        embedding (List[float]): The new embedding vector of the document.

    Returns:
        dict: A dictionary containing the updated document's content and updated_at timestamp,
              or None if the update fails.
    """
    try:
        if not isinstance(embedding, list) or not all(isinstance(x, float) for x in embedding):
            logger.error("Invalid embedding format")
            return None

        with get_db_session() as session:
            document = session.query(law_documents).filter(law_documents.id == document_id).first()
            if not document:
                logger.warning(f"Document with ID {document_id} not found")
                return None

            document.content = content
            document.embedding = embedding
            session.commit()

            session.refresh(document)

            updated_document = {
                "content": document.content,
                "updated_at": document.updated_at
            }
            return updated_document

    except Exception as e:
        logger.error(f"Error updating document: {str(e)}")
        return None
    except SQLAlchemyError as e:
        logger.error(f"Database error in update_document: {e}")
        return None

    except Exception as e:
        logger.error(f"Unexpected error in update_document: {e}")
        return None


def delete_document(document_id: int) -> bool:
    """
    Deletes a document from the database.

    Args:
        document_id (int): The ID of the document to delete.

    Returns:
        bool: True if the document was successfully deleted, False otherwise.
    """
    with get_db_session() as session:
        try:
            document = session.query(law_documents).filter(law_documents.id == document_id).first()
            if document:
                session.delete(document)
                session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error in delete_document: {e}")
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Unexpected error in delete_document: {e}")
            return False


def get_document_count() -> int:
    """
    Retrieves the total number of documents in the database.

    Returns:
        int: The total number of documents, or 0 if an error occurs.
    """
    with get_db_session() as session:
        try:
            return session.query(law_documents).count()
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_document_count: {str(e)}")
            return 0
        except Exception as e:
            logger.error(f"Unexpected error in get_document_count: {str(e)}")
            return 0