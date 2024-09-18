# app/main.py
from fastapi import FastAPI
from fastapi.responses import FileResponse
from .rag_model import rag_generate_answer
from .document_handler import highlight_and_save_document

app = FastAPI()

@app.get("/generate_answer")
def generate_answer(query: str):
    # Generate the answer using the RAG model
    generated_answer, source_text = rag_generate_answer(query)

    # Highlight the source text in the document
    highlighted_file = highlight_and_save_document(source_text)

    # Return the generated answer and the highlighted document as a file response
    return {
        "answer": generated_answer,
        "document": FileResponse(highlighted_file)
    }

