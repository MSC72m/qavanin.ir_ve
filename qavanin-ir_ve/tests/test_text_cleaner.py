import pytest
from data_processing.text_cleaner import convert_to_markdown

@pytest.mark.parametrize("input_text, expected_output", [
    ("Title\n---\nContent", "# Title\n\nContent"),
    ("Heading 1\n========\nContent", "# Heading 1\n\nContent"),
    ("Heading 2\n--------\nContent", "# Heading 2\n\nContent"),
])
def test_convert_to_markdown_headings(input_text, expected_output):
    """Test that the convert_to_markdown function can convert titles and headings correctly."""
    output = convert_to_markdown(input_text)
    assert output == expected_output

@pytest.mark.parametrize("input_text, expected_output", [
    ("Date: 2022/01/01", "Date: **2022/01/01**"),
    ("Date: 1400/12/31", "Date: **1400/12/31**"),
])
def test_convert_to_markdown_dates(input_text, expected_output):
    """Test that the convert_to_markdown function can format dates correctly."""
    output = convert_to_markdown(input_text)
    assert output == expected_output

@pytest.mark.parametrize("input_text, expected_output", [
    ("1. Item 1\n2. Item 2", "\n1. Item 1\n2. Item 2"),
    ("- Item 1\n- Item 2", "\n- **Item 1** -\n- **Item 2** -"),
])
def test_convert_to_markdown_lists(input_text, expected_output):
    """Test that the convert_to_markdown function can handle numbered lists and bullet points correctly."""
    output = convert_to_markdown(input_text)
    assert output == expected_output

@pytest.mark.parametrize("input_text, expected_output", [
    ("بند (1) Content", "### بند (1)\n\nContent"),
    ("ماده (2) Content", "### ماده (2)\n\nContent"),
    ("تبصره 1 Content", "**تبصره 1**\n\nContent"),
    ("جدول 1: Title", "**جدول 1: Title**\n\nContent"),
    ("پيوست 1: Title", "**پيوست 1: Title**\n\nContent"),
])
def test_convert_to_markdown_legal_structures(input_text, expected_output):
    """Test that the convert_to_markdown function can format specific legal document structures correctly."""
    output = convert_to_markdown(input_text)
    assert output == expected_output

@pytest.mark.parametrize("input_text, expected_output", [
    ("Persian text", "Persian text"),
    ("(Persian text)", "(*Persian text*)"),
])
def test_convert_to_markdown_persian_text(input_text, expected_output):
    """Test that the convert_to_markdown function can process Persian text elements correctly."""
    output = convert_to_markdown(input_text)
    assert output == expected_output
