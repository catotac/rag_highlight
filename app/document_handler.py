# app/document_handler.py
from docx import Document
from fastapi.responses import FileResponse

def highlight_text(doc, text_to_highlight):
    """Highlights the text within a Word document."""
    for paragraph in doc.paragraphs:
        if text_to_highlight in paragraph.text:
            for run in paragraph.runs:
                if text_to_highlight in run.text:
                    run.font.highlight_color = 1  # Highlight color
                    break

def highlight_and_save_document(source_text):
    """Loads a document, highlights the source text, and saves the highlighted document."""
    doc = Document('data/your_document.docx')
    
    # Highlight the specific text retrieved from the RAG model
    highlight_text(doc, source_text)
    
    # Save the highlighted document
    highlighted_file = 'data/highlighted_document.docx'
    doc.save(highlighted_file)
    
    return highlighted_file

