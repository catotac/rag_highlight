# RAG Highlight Application

This application demonstrates how to load a Word document, use a RAG model to generate answers from the document, and highlight the relevant text in the document.

## Setup Instructions

1. **Clone the Repository**:

    ```bash
    git clone https://github.com/your-username/rag_highlight.git
    cd rag_highlight
    ```

2. **Install Dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

3. **Run the Application**:

    To start the FastAPI server:

    ```bash
    bash run.sh
    ```

    Or manually run:

    ```bash
    uvicorn app.main:app --reload
    ```

4. **Test the API**:

    Access the API at `http://127.0.0.1:8000/generate_answer?query=your_query`.

## Project Structure

- **app/**: Contains the main application logic.
- **data/**: Contains the Word document to be highlighted.
- **tests/**: Contains unit tests for the FastAPI app.

## Future Work

- Integrate a real RAG model for dynamic document retrieval and response generation.

