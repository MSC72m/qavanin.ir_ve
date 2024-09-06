import pytest
import numpy as np
from data_processing.vectorizer import generate_embeddings

@pytest.fixture(scope="module")
def model():
    """Fixture that returns a SentenceTransformer model."""
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

@pytest.mark.parametrize("sentence, expected_shape", [
    ("This is a test.", (384,)),
    (["This is a test.", "This is another test."], (2, 384)),
])
def test_generate_embeddings_shape(model, sentence, expected_shape):
    """Test that the generate_embeddings function generates embeddings of the correct shape."""
    embeddings = generate_embeddings(sentence)
    assert isinstance(embeddings, list)
    assert all(isinstance(x, float) for x in embeddings)
    assert np.array(embeddings).shape == expected_shape

def test_generate_embeddings_invalid_input(model):
    """Test that the generate_embeddings function raises a ValueError if the input is invalid."""
    with pytest.raises(ValueError):
        generate_embeddings(123)
