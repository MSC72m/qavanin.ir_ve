# Qavanin.ir Scraper and API

This project is a web scraper and API for the Qavanin.ir website. It crawls random pages, processes the content, creates vector embeddings, and provides an API to query similar content.

## Project Structure

```
qavanin_scraper/
│
├── crawler/
│   ├── __init__.py
│   ├── web_scraper.py
│   ├── parser.py
│   └── main.py
│
├── data_processing/
│   ├── __init__.py
│   ├── text_cleaner.py
│   └── vectorizer.py
│
├── database/
│   ├── __init__.py
│   ├── models.py
│   └── db_operations.py
│
├── api/
│   ├── __init__.py
│   ├── main.py
│   └── endpoints.py
│
├── utils/
│   ├── __init__.py
│   └── config.py
│
├── requirements.txt
└── README.md
```

## Features

1. Web Scraping: Crawls 5 random pages from Qavanin.ir
2. Text Processing: Cleans HTML content and converts it to Markdown
3. Vector Embeddings: Creates vector embeddings for processed text
4. Database Storage: Stores original text, processed text, and vector embeddings in PostgreSQL
5. FastAPI Endpoint: Provides an API to query similar content based on user input

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/qavanin_scraper.git
   cd qavanin_scraper
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up your PostgreSQL database and update the connection details in `utils/config.py`.

## Usage

1. Run the scraper:
   ```
   python scraper/main.py
   ```

2. Start the FastAPI server:
   ```
   uvicorn api.main:app --reload
   ```

3. Access the API documentation at `http://localhost:8000/docs`

## API Endpoints

- `POST /query`: Accept user input, find similar content, and return the results

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

