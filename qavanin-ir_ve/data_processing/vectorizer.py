from sentence_transformers import SentenceTransformer
import numpy as np

# Load the SentenceTransformer model
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def generate_embeddings(sentences: str) -> list[float]:
    # Ensure the input is a list of sentences
    if isinstance(sentences, str):
        sentences = [sentences]

    # Generate embeddings
    embeddings = model.encode(sentences)

    # Ensure we're working with a numpy array
    if not isinstance(embeddings, np.ndarray):
        embeddings = np.array(embeddings)

    # If we have a 2D array with only one row, flatten it
    if len(embeddings.shape) == 2 and embeddings.shape[0] == 1:
        embeddings = embeddings.flatten()

    # Convert the embeddings to a 1-dimensional list of floats
    embeddings_list = embeddings.tolist()

    # Ensure the embeddings are a 1-dimensional list of floats
    if not isinstance(embeddings_list, list) or not all(isinstance(x, float) for x in embeddings_list):
        raise ValueError("Embeddings must be a 1-dimensional list of floats.")

    return embeddings_list