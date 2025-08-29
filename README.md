# resume_parser
It's a generic Resume Parser solution that supports two file formats (PDF and Word).

Resume Parser — Local, Free LLM (Ollama) + Streamlit UI
Parse PDF/DOCX resumes to clean JSON using a local model. No cloud calls.

Features
Local LLM via Ollama (e.g., llama3.1:8b, phi3:mini)
PDF/DOCX text extraction (PyMuPDF fallback to pdfminer)
Deterministic JSON (temperature 0) with basic validation
Batch parsing + JSONL export
Streamlit UI for upload, review, and download
Repo layout
. ├─ app.py # Streamlit UI 
  ├─ resume_parser.py # Free-only parser (Ollama) 
  ├─ requirements.txt # Python deps 
  ├─ scripts/  
  │ ├─ setup.sh # macOS/Linux installer 
  │ └─ setup.ps1 # Windows installer 
  └─ README.md
