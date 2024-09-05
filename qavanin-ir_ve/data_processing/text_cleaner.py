import re


def convert_to_markdown(text):
    markdown_output = ""

    # Convert Titles and Headings
    text = re.sub(r"^(.+?)(?=\s*[-–—:])", r"# \1", text)

    # Convert Dates to Bold
    text = re.sub(r"(\d{4}/\d{1,2}/\d{1,2})", r"**\1**", text)

    # Convert References in Parentheses to Italics
    text = re.sub(r"\(([^)]+)\)", r"(*\1*)", text)

    # Handle numbered lists
    text = re.sub(r"(\d+)(\s*[-–—])", r"\n\1.", text)

    # Handle bullet points (Using Persian alphabets 'الف', 'ب', 'پ', etc.)
    text = re.sub(r"([\u0627-\u064A])\s*[-–—]", r"\n- **\1** - ", text)

    # Convert Sections with specific keywords like "بند" (Article), "ماده" (Clause) to subsections
    text = re.sub(r"(بند \(.+?\))", r"### \1", text)
    text = re.sub(r"(ماده \(.+?\))", r"### \1", text)

    # Convert "تبصره" (Note or Footnote) to bold and formatted notes
    text = re.sub(r"(تبصره\s*\d*)", r"**\1**", text)

    # Detect lines with "جدول" (Table) or "پيوست" (Appendix) and format accordingly
    text = re.sub(r"(جدول .+?:)", r"**\1**", text)
    text = re.sub(r"(پيوست .+?:)", r"**\1**", text)

    # Split the text into paragraphs and process each separately
    paragraphs = text.split('\n\n')

    for para in paragraphs:
        # If a paragraph starts with a number or bullet, format it as a list
        if re.match(r'^\d+\.', para) or re.match(r'^\s*[-*]', para):
            markdown_output += f"\n{para.strip()}"
        else:
            # Otherwise, treat it as a regular paragraph
            markdown_output += f"\n\n{para.strip()}"

    return markdown_output

