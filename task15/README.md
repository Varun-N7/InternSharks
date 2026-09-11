# Task 15 — AI Document Summarization with File Upload

## 📌 Project Overview

Task 15 extends the AI Text Summarization API from Task 14.

This API allows users to upload `.txt` and `.pdf` documents. The application extracts text from the uploaded document and sends the extracted text to OpenRouter for AI-powered summarization.

The API supports three summary types:

- `brief`
- `detailed`
- `bullet_points`

## 🚀 Features

- Upload TXT and PDF documents
- Extract text from uploaded files
- Maximum file size: 5 MB
- AI-powered summarization using OpenRouter
- Brief, detailed, and bullet-point summaries
- Validate uploaded files
- Validate AI responses using Pydantic
- Handle invalid files and AI service errors
- Simple FastAPI structure

## 🔄 Application Flow

```text
Upload File
     ↓
FastAPI
     ↓
Validate File
     ↓
Extract Text
     ↓
OpenRouter AI
     ↓
Generate Summary
     ↓
Validate AI Output
     ↓
Return Response
```

## 📁 Project Structure

```text
task15/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── summarizer.py
│   │   └── document.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── summarizer_service.py
│   │   └── document_service.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── summarizer.py
│   ├── prompts/
│   │   ├── __init__.py
│   │   └── summarizer_prompt.py
│   └── utils/
│       ├── __init__.py
│       └── file_parser.py
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## 🛠️ Technologies Used

- Python
- FastAPI
- Pydantic
- Uvicorn
- OpenRouter API
- Requests
- pypdf
- python-dotenv
- python-multipart

## ⚙️ Setup

### 1. Go to the project folder

```bash
cd ~/Desktop/doubletap/task15
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

macOS/Linux:

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

## 🔐 Environment Variables

Create a `.env` file:

```env
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=openrouter/free
```

Do not commit `.env` or your API key to GitHub.

An example file is provided as `.env.example`.

## ▶️ Run the API

Start the FastAPI server:

```bash
python -m uvicorn app.main:app --reload
```

The API will run at:

```text
http://127.0.0.1:8000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

## 📄 API Endpoint

### POST `/ai/summarize-document`

Upload a document and generate an AI summary.

### Request

Use `multipart/form-data`.

| Field | Type | Required | Description |
|---|---|---|---|
| `file` | File | Yes | `.txt` or `.pdf` document |
| `summary_type` | Text | Yes | `brief`, `detailed`, or `bullet_points` |

### Example

```text
file = Employee-Handbook.pdf
summary_type = brief
```

## ✅ Successful Response

```json
{
    "success": true,
    "status_code": 200,
    "data": {
        "file_name": "Employee-Handbook.pdf",
        "summary_type": "brief",
        "summary": "Summary of the document...",
        "main_topic": "Employee Handbook",
        "keywords": [
            "employees",
            "policies",
            "workplace"
        ]
    }
}
```

## ❌ Error Handling

The API handles common errors including:

- Missing file
- Empty file
- Unsupported file type
- File larger than 5 MB
- PDF extraction failure
- PDF with no extractable text
- Invalid summary type
- Invalid AI response
- Invalid OpenRouter API key
- OpenRouter rate limit
- AI/model service failure

Raw library errors, stack traces, API keys, and secrets are not returned to the client.

## 🧪 Testing

The API can be tested using Postman.

Recommended test cases:

1. Valid TXT file
2. Valid PDF file
3. Multi-page PDF
4. Brief summary
5. Detailed summary
6. Bullet-point summary
7. Empty file
8. Missing file
9. Unsupported file type
10. Invalid summary type
11. PDF with no extractable text
12. File larger than 5 MB
13. Invalid OpenRouter API key
14. AI/model service failure

### Postman Request

Method:

```text
POST
```

URL:

```text
http://127.0.0.1:8000/ai/summarize-document
```

Body:

```text
form-data
```

Add:

```text
file            File    Employee-Handbook.pdf
summary_type    Text    brief
```

## 🔒 Security

The following files and folders should not be committed to GitHub:

```text
.env
.venv/
__pycache__/
*.pyc
uploads/
```

The `.gitignore` file is included to help protect these files.

## 📌 Important Note

This project extracts text from PDFs using `pypdf`.

OCR is not included. Therefore, scanned or image-only PDFs may return:

```text
File contains no extractable text
```

The application follows this process:

```text
PDF → Extract Text → OpenRouter → Summary
```

The PDF itself is not sent directly to the AI model.

## 🎯 Task Goal

The goal of Task 15 is to extend the existing text summarization API so that users can upload real documents and receive structured AI-generated summaries while keeping the code simple, readable, and easy to explain in an interview.
