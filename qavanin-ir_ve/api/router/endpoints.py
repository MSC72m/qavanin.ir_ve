from fastapi import APIRouter, HTTPException, status
from data_processing.vectorizer import generate_embeddings
from database.db_oprations import get_closest_document, get_document_count, get_document_by_id, update_document, \
    delete_document
from data_processing.text_cleaner import convert_to_markdown
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

router = APIRouter()


class TextInput(BaseModel):
    text: str


@router.post("/get_closest_match", status_code=status.HTTP_200_OK)
async def get_closest_match(input_data: TextInput, limit: int):
    """
    Find the closest matching documents for a given input text.

    Args:
        input_data (TextInput): The input text to match against.
        limit (int): The maximum number of matching documents to return.

    Returns:
        dict: A dictionary containing the closest matching documents and total document count.

    Raises:
        HTTPException: If no matching document is found or an error occurs.
    """
    try:
        user_embeddings = await run_in_threadpool(generate_embeddings, input_data.text)
        closest_documents = await run_in_threadpool(get_closest_document, user_embeddings, limit)

        if not closest_documents:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No matching document found.")

        total_documents = await run_in_threadpool(get_document_count)

        return {
            "closest_documents": closest_documents,
            "total_documents": total_documents
        }
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")


@router.put("/update_document/{document_id}", status_code=status.HTTP_200_OK)
async def update_documents(document_id: int, content: TextInput):
    """
    Update the content of a specific document.

    Args:
        document_id (int): The ID of the document to update.
        content (TextInput): The new content for the document.

    Returns:
        dict: A dictionary containing a success message and the updated document information.

    Raises:
        HTTPException: If the document is not found or an error occurs during the update.
    """
    try:
        embeddings = await run_in_threadpool(generate_embeddings, content.text)
        content_md = await run_in_threadpool(convert_to_markdown, content.text)

        updated_document = await run_in_threadpool(update_document, document_id, content_md, embeddings)

        if not updated_document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found or update failed")

        return {
            "message": "Document updated successfully",
            "document": {
                "content": updated_document["content"],
                "updated_at": updated_document["updated_at"]
            }
        }
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/delete_document/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document_endpoint(document_id: int):
    """
    Delete a specific document.

    Args:
        document_id (int): The ID of the document to delete.

    Returns:
        None

    Raises:
        HTTPException: If the document is not found or an error occurs during deletion.
    """
    try:
        success = await run_in_threadpool(delete_document, document_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        return
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/get_document/{document_id}", status_code=status.HTTP_200_OK)
async def get_document_by_id_endpoint(document_id: int):
    """
    Retrieve a specific document by its ID.

    Args:
        document_id (int): The ID of the document to retrieve.

    Returns:
        dict: A dictionary containing the retrieved document information.

    Raises:
        HTTPException: If the document is not found or an error occurs during retrieval.
    """
    try:
        document = await run_in_threadpool(get_document_by_id, document_id)

        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

        return {
            "message": "Document retrieved successfully",
            "id": document["id"],
            "content": document["content"]
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
