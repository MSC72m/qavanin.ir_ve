from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from data_processing.vectorizer import generate_embeddings
from database.db_oprations import get_closest_document, get_document_count
from pydantic import BaseModel

router = APIRouter()

class TextInput(BaseModel):
    text: str

@router.post("/get_closest_match", status_code=status.HTTP_200_OK)
async def get_closest_match(input_data: TextInput, limit: int):
    try:
        # Generate embeddings for the input text
        user_embeddings = generate_embeddings(input_data.text)

        closest_documents = get_closest_document(user_embeddings, limit=limit)
        if not closest_documents:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No matching document found."
            )

        total_documents = get_document_count()

        return JSONResponse(
            content={
                "closest_document": closest_documents,  # This is already a list of strings
                "total_documents": total_documents,
            },
            status_code=status.HTTP_200_OK
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )