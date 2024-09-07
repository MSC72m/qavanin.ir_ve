# qavanin.ir Scraper and API

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
  - [Docker Setup](#docker-setup)
  - [Manual Setup](#manual-setup)
- [Usage](#usage)
  - [Running the Scraper](#running-the-scraper)
  - [Starting the API Server](#starting-the-api-server)
- [API Endpoints](#api-endpoints)
  - [GET /get_closest_match](#get-get_closest_match)
  - [PUT /update_document/{document_id}](#put-update_documentdocument_id)
  - [DELETE /delete_document/{document_id}](#delete-delete_documentdocument_id)
  - [GET /get_document/{document_id}](#get-get_documentdocument_id)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Dependencies](#dependencies)
- [Future Improvements](#future-improvements)
- [Error Handling](#error-handling)
- [Possible issues](#possible-issues)


## Overview
The qavanin.ir Scraper and API is a comprehensive solution for extracting, processing, and analyzing legal documents from the qavanin.ir website. It combines web scraping capabilities with natural language processing and a robust API to provide easy access to legal information.

## Features
- **Web Scraping**: Crawls multiple pages from qavanin.ir, extracting legal documents.
- **Text Processing**: Cleans HTML content and converts it to a structured Markdown format.
- **Vector Embeddings**: Generates vector embeddings for processed text using `SentenceTransformer`.
- **Database Storage**: Stores original text, processed text, and vector embeddings in PostgreSQL with `pgvector` extension.
- **FastAPI Endpoints**: Provides a RESTful API for querying similar content, updating documents, and more.
- **Docker Support**: Easily deploy and run the application using Docker.

## Installation

### Docker Setup
1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/qavanin_scraper.git
    cd qavanin_scraper
    ```

2. Build the Docker image:
    ```bash
    docker build -t my-pgvector-db .
    ```

3. Run the Docker container:
    ```bash
    docker run -d --name your_container_name -e POSTGRES_DB=qavanin_db -e POSTGRES_USER=test -e POSTGRES_PASSWORD=test -p 5432:5432 my-pgvector-db
    ```

### Manual Setup

1. Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

2. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

3. Set up your PostgreSQL database and install the `pgvector` extension.

4. Create a `.env` file in the project root and add your database configuration:
    ```bash
    POSTGRES_USER=your_username
    POSTGRES_PASSWORD=your_password
    POSTGRES_DB=qavanin_db
    ```

## Usage

### Running the Scraper
1. Configure web scraping variables in `crawler/main.py`:
    ```python
    item_in_page = 25  # Number of items per page
    start_page = 1     # First page to start scraping
    last_page = 1      # Last page to scrape
    ```

2. Run the scraper:
    ```bash
    python crawler/main.py
    ```

### Starting the API Server
1. Start the FastAPI server:
    ```bash
    uvicorn api.main:app --reload
    ```

2. Access the API documentation at [http://localhost:8000/docs](http://localhost:8000/docs).

## API Endpoints

### GET /get_closest_match
Find the closest matching documents for a given input text.

**Request**:
```bash
  GET /api/get_closest_match?limit=5
```
**Body**:
```json
{
  "text": "Your search query here"
}
```
**Response**:
```json
{
  "closest_documents": [
    {
      "id": 1,
      "content": "Matched document content"
    }
  ],
  "total_documents": 100
}
```

### PUT /update_document/{document_id}

Update the content of a specific document.
**Request**:
```bash
PUT /api/update_document/1
```
**Body**:
```json
{
  "text": "Updated document content"
}
```
**Response**:
```json
{
  "message": "Document updated successfully",
  "document": {
    "content": "Updated document content",
    "updated_at": "2023-05-20T12:00:00Z"
  }
}
```
### DELETE /delete_document/{document_id}
Delete a specific document.
**Request**:
```bash
  DELETE /api/delete_document/1
```
Response:
```bash
204 No Content
```

## GET /get_document/{document_id}
Retrieve a specific document by its ID.

Request:
```bash
GET /api/get_document/1
```
Response:
```json
{
  "message": "Document retrieved successfully",
  "id": 1,
  "content": "Document content"
}
``` 

## Configuration
Database configuration is stored in the `.env` file.
Web scraping parameters can be adjusted in `crawler/main.py`.
The SentenceTransformer model can be changed in `data_processing/vectorizer.py`.

## Project Structure
```
qavanin_scraper/
│
├── crawler/
│   ├── web_scraper.py
│   ├── parser.py
│   └── main.py
│
├── data_processing/
│   ├── text_cleaner.py
│   └── vectorizer.py
│
├── database/
│   ├── models.py
│   └── db_operations.py
│
├── api/
│   ├── main.py
│   └── endpoints.py
│
├── .env
├── requirements.txt
├── Dockerfile
└── README.md
```
## Dependencies
### Main dependencies include:

FastAPI
SQLAlchemy
psycopg2-binary
BeautifulSoup4
requests
sentence-transformers
pgvector

For a complete list, refer to the requirements.txt file.

## Future Improvements

The Qavanin.ir Scraper and API is designed to be extensible and scalable, with potential improvements to increase its performance, error handling, and usability. Some of the key future enhancements include:

1. **Multithreading or Asyncio for Faster Scraping**  
   Implementing multithreading or asynchronous scraping techniques can significantly speed up the scraping process by allowing multiple pages to be scraped simultaneously.
    Multithreading is possible just need to implement some logic to handle duplication and handle when program gets out of sync for now didn't have the enough time. can use set's and handle errors to not have duplications in db.
    Sadly currently limited by the website being iran access so no proxy and cdn usage is possible. probably should refactor with playwright to be able to have asynchronous requesting.
    Other options include having multiple instances of the scraper in docker.
2. **Improved Error Handling**  
   Adding more robust error handling and recovery mechanisms will ensure smoother scraping even under challenging network conditions or in case of changes to the target website's structure.

3. **Rate Limiting**  
   Introducing rate limiting will prevent overloading the qavanin.ir website, ensuring compliance with web scraping best practices and avoiding potential blocking by the server.

4. **Performance Optimization for Document Processing**  
   Optimizing the performance of large-scale document processing will improve response times when dealing with a high volume of legal documents. Caching mechanisms could also be introduced to optimize frequent queries.

5. **Parallel Processing for Text Cleaning and Vectorization**  
   To handle large batches of documents, implementing parallel processing for text cleaning and vector embedding generation can help improve the overall efficiency of the data pipeline.
---

## Error Handling
### The application includes comprehensive error handling:

**Database connection errors are caught and logged.**
**Web scraping failures are handled with retries and logging.**
**API endpoints include proper error responses and status codes.**
**Custom exceptions like DatabaseInitializationError are used for specific error scenarios.**

## Possible Issues

- **qavanin.ir Access**: qavanin.ir is an Iran-access website, meaning that it will reject any requests that are not made with an Iranian IP. This might cause problems if your IP is not from Iran.

- **Cloudflare Protection**: qavanin.ir is behind Cloudflare and is protected by it. Reducing the delay might cause some problems with interrupting the bot with puzzles and other security measures.

- **Database Initialization**: Database initialization might fail if it is not correctly set up. Make sure to check this step before proceeding with other steps.

- **Dependencies**: Not having the correct dependencies installed can cause problems. For example, Chromium drivers are required for crawling, and the sentence-transformers library has many dependencies, such as torch and CUDA libraries. Make sure that any errors you encounter are not related to these dependencies.

- **Library Interference**: Some libraries, if not installed currently, might cause problems and interfere with each other. Keep this in mind.
