import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer
import faiss
from transformers import pipeline

# Step 1: Load and extract text from the PDF document
def extract_pdf_text(pdf_path):
    doc = fitz.open(pdf_path)
    pdf_structure = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("blocks")  # Extract text by blocks (structured form)
        for block in blocks:
            # block[4] contains the actual text in each block
            pdf_structure.append({
                'page_num': page_num,
                'text': block[4].strip(),  # Clean up the text
                'block': block[:4]  # Coordinates of the text block (can be used for additional structure)
            })
    return pdf_structure

# Step 2: Chunking based on document structure
def create_chunks_from_structure(pdf_structure, min_chunk_length=200):
    chunks = []
    current_chunk = ""
    for block in pdf_structure:
        current_chunk += block['text'] + "\n"
        if len(current_chunk) > min_chunk_length:
            chunks.append(current_chunk.strip())
            current_chunk = ""
    if current_chunk:  # Append any remaining chunk
        chunks.append(current_chunk.strip())
    return chunks

# Step 3: Create embeddings for each chunk
def create_embeddings(chunks, model_name="sentence-transformers/all-MiniLM-L6-v2"):
    model = SentenceTransformer(model_name)
    embeddings = model.encode(chunks, convert_to_tensor=True)
    return embeddings

# Step 4: Index embeddings using FAISS for similarity search
def index_embeddings(embeddings):
    embedding_size = embeddings.shape[1]
    index = faiss.IndexFlatL2(embedding_size)
    faiss.normalize_L2(embeddings.numpy())
    index.add(embeddings.numpy())
    return index

# Step 5: Perform retrieval on a query
def retrieve_relevant_chunks(query, index, chunks, model, top_k=3):
    query_embedding = model.encode([query], convert_to_tensor=True).numpy()
    faiss.normalize_L2(query_embedding)
    D, I = index.search(query_embedding, top_k)
    return [chunks[i] for i in I[0]]

# Step 6: Use a language model to generate the response
def generate_rag_response(query, retrieved_chunks, generation_model_name="gpt-3.5-turbo"):
    generation_model = pipeline("text-generation", model=generation_model_name)
    prompt = query + "\n" + "\n".join(retrieved_chunks)
    response = generation_model(prompt, max_length=200)
    return response[0]['generated_text']

# Complete RAG Pipeline
def rag_pipeline(pdf_path, query):
    # Extract and chunk PDF text
    pdf_structure = extract_pdf_text(pdf_path)
    chunks = create_chunks_from_structure(pdf_structure)

    # Generate embeddings and index them
    embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    embeddings = create_embeddings(chunks, embedding_model)
    index = index_embeddings(embeddings)

    # Retrieve relevant chunks
    relevant_chunks = retrieve_relevant_chunks(query, index, chunks, embedding_model)

    # Generate a response based on relevant chunks
    response = generate_rag_response(query, relevant_chunks)

    return response

# Usage
pdf_path = "path/to/your/document.pdf"
query = "Explain the introduction section of the document"
response = rag_pipeline(pdf_path, query)
print(response)

