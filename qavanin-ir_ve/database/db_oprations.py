from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import func
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


def get_closest_document(query_embedding: List[float], limit: int) -> List[str]:
    with get_db_session() as session:
        try:
            # Perform similarity search using <-> for L2 distance
            closest_documents = session.query(law_documents.content).order_by(
                law_documents.embedding.l2_distance(query_embedding)
            ).limit(limit).all()

            # Extract content from the result and return as a list of strings
            return [doc.content for doc in closest_documents]
        except Exception as e:
            logger.error(f"Error in get_closest_document: {str(e)}")
            raise

def insert_document(content, embeds):
    # Convert embeds to a list of Python floats
    embeds_list = [float(x) for x in embeds]
    with get_db_session() as session:
        try:
            # Assume LawDocument is your SQLAlchemy model
            document = law_documents(
                content=content,
                embedding=embeds_list,
                updated_at=None  # or the appropriate datetime
            )
            session.add(document)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error inserting document: {e}")


def get_document_by_id(document_id: int) -> Optional[law_documents]:
    with get_db_session() as session:
        return session.query(law_documents).filter(law_documents.id == document_id).first()


def update_document(document_id: int, content: str, embedding: List[float]) -> bool:
    with get_db_session() as session:
        document = session.query(law_documents).filter(law_documents.id == document_id).first()
        if document:
            document.content = content
            document.embedding = embedding
            return True
        return False


def delete_document(document_id: int) -> bool:
    with get_db_session() as session:
        document = session.query(law_documents).filter(law_documents.id == document_id).first()
        if document:
            session.delete(document)
            return True
        return False


def batch_insert_documents(documents: List[dict]) -> List[law_documents]:
    with get_db_session() as session:
        db_documents = [law_documents(content=doc['content'], embedding=doc['embedding']) for doc in documents]
        session.bulk_save_objects(db_documents)
        session.flush()
        return db_documents


def get_paginated_documents(page: int = 1, per_page: int = 10) -> List[law_documents]:
    with get_db_session() as session:
        return session.query(law_documents).order_by(law_documents.id).offset((page - 1) * per_page).limit(
            per_page).all()


def get_document_count() -> int:
    with get_db_session() as session:
        return session.query(law_documents).count()
