# Task 17 — Introduction to RAG: Chat with a Document

A simple Retrieval-Augmented Generation (RAG) API built with FastAPI, FAISS, Hugging Face sentence-transformers, and OpenRouter.

## Objective

Allow users to upload a PDF or TXT document, extract its text, split it into chunks, create embeddings, store those embeddings in FAISS, and ask questions about the uploaded document.

The system retrieves relevant document chunks before sending the question and retrieved context to an LLM. This helps keep answers grounded in the uploaded document.

## RAG Pipeline

```text
Extract → Chunk → Embed → Store → Retrieve → Build Context → Generate Answer
```

```text
PDF / TXT
   ↓
Text Extraction
   ↓
Text Chunking
   ↓
Hugging Face Embeddings
   ↓
FAISS Vector Store
   ↓
User Question
   ↓
Question Embedding
   ↓
FAISS Similarity Search
   ↓
Top Relevant Chunks
   ↓
Grounded RAG Prompt
   ↓
OpenRouter LLM
   ↓
Answer
```

## Technologies

- Python
- FastAPI
- Pydantic
- pypdf
- FAISS
- NumPy
- sentence-transformers
- Hugging Face `all-MiniLM-L6-v2`
- OpenRouter
- Uvicorn
- python-dotenv

## Project Structure

```text
task17/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── routes/
│   │   ├── __init__.py
│   │   └── rag.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── rag_service.py
│   │   ├── embedding_service.py
│   │   └── ai_service.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── rag.py
│   ├── prompts/
│   │   ├── __init__.py
│   │   └── rag_prompt.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── file_parser.py
│   │   └── text_chunker.py
│   └── storage/
│       ├── __init__.py
│       └── vector_store.py
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Features

- Upload `.txt` and `.pdf` documents
- Maximum file size: 5MB
- Extract text from TXT and PDF files
- Reject unsupported file types
- Reject empty or non-extractable documents
- Split documents into chunks
- Generate local embeddings using Hugging Face
- Store vectors using FAISS
- Search for the most relevant chunks
- Configurable `top_k` retrieval
- Send retrieved context and the question to OpenRouter
- Grounded answers using a RAG prompt
- Handle invalid document IDs
- Handle OpenRouter API errors
- Handle invalid API keys and rate limits
- Keep document vectors isolated by document ID
- No LangChain or LlamaIndex

## Embeddings

This project uses the local Hugging Face model:

```text
sentence-transformers/all-MiniLM-L6-v2
```

The model converts text into numerical vectors. The user's question is converted into a vector using the same model.

FAISS compares the question vector with document chunk vectors to find semantically similar content.

Embeddings are generated locally, so no embedding API key is required.

## Chunking

The project uses simple manual character-based chunking:

```text
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
```

The overlap helps preserve context when information falls near a chunk boundary.

## Vector Search

FAISS uses an `IndexFlatIP` index.

Embeddings are normalized before storage, allowing inner-product search to be used for cosine-similarity-style retrieval.

Each uploaded document has its own FAISS index, identified by its `document_id`.

## Environment Variables

Create a `.env` file:

```env
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=openrouter/free
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

Do not commit `.env` or any API keys to GitHub.

`.env.example` is provided as a safe template.

## Installation

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the Application

From the `task17` directory:

```bash
uvicorn app.main:app --reload
```

The API runs at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

### 1. Upload Document

```http
POST /rag/documents
```

Upload a PDF or TXT file using `multipart/form-data`.

Form-data:

```text
file: <document>
```

Example successful response:

```json
{
  "success": true,
  "status_code": 201,
  "data": {
    "document_id": "example-id",
    "file_name": "document.txt",
    "chunks_created": 1
  }
}
```

Save the returned `document_id` for later questions.

### 2. Ask a Question

```http
POST /rag/ask
```

Request body:

```json
{
  "document_id": "example-id",
  "question": "What is RAG?",
  "top_k": 3
}
```

Example successful response:

```json
{
  "success": true,
  "status_code": 200,
  "data": {
    "document_id": "example-id",
    "question": "What is RAG?",
    "answer": "RAG stands for Retrieval-Augmented Generation..."
  }
}
```

### 3. Get Document Information

```http
GET /rag/documents/{document_id}
```

Example:

```http
GET /rag/documents/example-id
```

Example response:

```json
{
  "success": true,
  "status_code": 200,
  "data": {
    "document_id": "example-id",
    "file_name": "document.txt",
    "chunks_created": 1
  }
}
```

## Error Handling

The API handles common failures without exposing raw exceptions, stack traces, or API secrets.

Examples include:

- Empty document
- Unsupported file type
- File larger than 5MB
- No extractable PDF text
- Empty question
- Invalid document ID
- Embedding failure
- FAISS/vector search failure
- Invalid OpenRouter API key
- OpenRouter rate limit
- OpenRouter model/request failure
- Empty or invalid AI response

## Grounded RAG Behavior

The RAG prompt instructs the LLM to:

- Use only the supplied document context
- Avoid outside knowledge
- Avoid guessing or inventing information
- Say when the answer cannot be found in the document

This helps reduce hallucinations and keeps answers grounded in retrieved document content.

## Testing

The implementation was tested using Postman.

Completed checks included:

- TXT document upload
- Question where the answer exists
- Question where the answer is not found
- Multiple questions against the same document
- PDF document upload
- Question against an uploaded PDF
- Invalid document ID
- Empty question
- Unsupported file type

Multiple-document isolation was intentionally skipped during the testing session.

## RAG vs Conversation Memory

RAG and conversation memory solve different problems.

### Conversation Memory

```text
User → AI
 ↓
Message history
 ↓
Next question
 ↓
AI uses previous conversation
```

### RAG

```text
Document
 ↓
Chunks
 ↓
Embeddings
 ↓
FAISS
 ↓
Relevant chunks
 ↓
AI answer
```

RAG is useful when the assistant needs to answer questions using information contained in uploaded documents.

## Important Concepts Learned

### RAG
Retrieval-Augmented Generation retrieves relevant information before generating an answer.

### Embeddings
Embeddings represent text as numerical vectors that capture semantic meaning.

### Vector
A vector is the numerical representation used for similarity comparison.

### FAISS
FAISS is used for efficient similarity search over vectors.

### Chunk Size
Chunk size controls how much document text is placed into each searchable piece.

### Chunk Overlap
Overlap repeats a small part between adjacent chunks to preserve context.

### Query Embedding
The user's question is converted into an embedding before searching FAISS.

### Top-K
`top_k` controls how many relevant chunks are retrieved for the question.

### Grounded Generation
The LLM receives retrieved document context and is instructed to answer using that context only.

### Context Window
The amount of information that can be provided to the LLM in one request is limited. Retrieving only relevant chunks helps avoid sending an entire large document.

### Hallucination
A hallucination occurs when an AI generates information that is unsupported or incorrect. Grounded RAG helps reduce this by supplying relevant source context and restricting the prompt.

## Security Notes

- Never commit `.env`
- Never commit API keys
- Do not upload sensitive documents to a public repository
- Keep virtual environments out of Git
- Do not commit generated vector/cache files

## Limitations

- Data is stored in memory and is lost when the application restarts.
- No OCR is included for scanned/image-only PDFs.
- Only PDF and TXT files are supported.
- Maximum upload size is 5MB.
- This is an introductory RAG implementation designed for learning and demonstration.

## Future Improvements

Possible future improvements include:

- Persistent vector storage
- Database-backed document metadata
- Authentication
- User-specific document collections
- Better chunking strategies
- Document deletion endpoint
- OCR support
- More embedding models
- Streaming AI responses
- Re-ranking retrieved chunks
- Production deployment

## Conclusion

This project demonstrates a complete beginner-friendly RAG pipeline using FastAPI, Hugging Face embeddings, FAISS, and OpenRouter.

```text
Upload document
      ↓
Extract text
      ↓
Create chunks
      ↓
Create embeddings
      ↓
Store in FAISS
      ↓
Ask question
      ↓
Retrieve relevant chunks
      ↓
Send context + question to LLM
      ↓
Generate grounded answer
```