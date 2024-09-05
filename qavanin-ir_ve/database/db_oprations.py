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


def update_document(document_id: int, content: str, embedding: List[float]):
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

            updated_document = {
                "content": document.content,
                "updated_at": document.updated_at
            }
            return updated_document

    except SQLAlchemyError as e:
        logger.error(f"Database error in update_document: {e}")
        return None

    except Exception as e:
        logger.error(f"Unexpected error in update_document: {e}")
        return None


def delete_document(document_id: int) -> bool:
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
    with get_db_session() as session:
        try:
            return session.query(law_documents).count()
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_document_count: {str(e)}")
            return 0
        except Exception as e:
            logger.error(f"Unexpected error in get_document_count: {str(e)}")
            return 0
