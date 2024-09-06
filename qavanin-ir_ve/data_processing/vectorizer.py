from sentence_transformers import SentenceTransformer
import numpy as np

# Load the SentenceTransformer model
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')


def generate_embeddings(sentences: str) -> list[float]:
    """
    Generate vector embeddings for the given text using a pre-trained Sentence Transformer model.

    Args:
        sentences (str): A string or list of strings to generate embeddings for.

    Returns:
        list[float]: A 1-dimensional list of floats representing the text embeddings.

    Raises:
        ValueError: If the generated embeddings are not in the expected format.
    """
    if isinstance(sentences, str):
        sentences = [sentences]

    # Generate embeddings
    embeddings = model.encode(sentences)
    if not isinstance(embeddings, np.ndarray):
        embeddings = np.array(embeddings)

    if len(embeddings.shape) == 2 and embeddings.shape[0] == 1:
        embeddings = embeddings.flatten()

    embeddings_list = embeddings.tolist()

    if not isinstance(embeddings_list, list) or not all(isinstance(x, float) for x in embeddings_list):
        raise ValueError("Embeddings must be a 1-dimensional list of floats.")

    return embeddings_list
