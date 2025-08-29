# resume_parser
It's a generic Resume Parser solution that supports two file formats (PDF and Word).

Resume Parser -Local, Free LLM (Ollama) + Streamlit UI
Parse PDF/DOCX resumes to clean JSON using a local model. No cloud calls.

Features
Local LLM via Ollama (e.g., llama3.1:8b, phi3:mini)
PDF/DOCX text extraction (PyMuPDF fallback to pdfminer)
Deterministic JSON (temperature 0) with basic validation
Batch parsing + JSONL export
Streamlit UI for upload, review, and download
```text
Repo layout
  ├─ app.py # Streamlit UI 
  ├─ resume_parser.py # Free-only parser (Ollama) 
  ├─ requirements.txt # Python deps 
  ├─ scripts/  
  │ ├─ setup.sh # macOS/Linux installer 
  │ └─ setup.ps1 # Windows installer 
  └─ README.md
```
Requirements
1) System
  OS: Windows 10/11, macOS 12+, or Ubuntu 20.04+
  CPU: Any 64-bit; GPU optional
  RAM: 8 GB minimum, 16 GB recommended
  Disk: 6–10 GB free (models + Python env)
  Network: Only for first-time model download

2) Software
  Python 3.10 or newer
  Ollama (desktop app or CLI). Keep it running while you use the app.

3) Local LLM model
  ollama pull llama3.1:8b (~4–5 GB size)

4) Python packages

| Package        | Purpose                                                    |
| -------------- | ---------------------------------------------------------- |
| `streamlit`    | Web UI for upload, preview, and download                   |
| `ollama`       | Talks to the local model daemon                            |
| `pydantic`     | Validates and structures the JSON output                   |
| `pymupdf`      | Fast PDF text extraction                                   |
| `pdfminer.six` | Slow but robust PDF fallback when PyMuPDF gives empty text |
| `python-docx`  | Reads `.docx` resumes                                      |
| `watchdog`     | improves auto-reload on some systems.                      |

5) Install
    python -m venv .venv
    # Windows
    .\.venv\Scripts\Activate.ps1
    # macOS/Linux
    source .venv/bin/activate
  
    pip install -r requirements.txt

6) Run
  1. Start Ollama (desktop app open is enough).
  2. Pull a model (one time).
  3. Launch the app:
    streamlit run app.py
  4. Open http://localhost:8501
  5. Upload PDF/DOCX and click “Parse resumes”.

7) Notes
  Data stays local. No cloud calls.
  First run may take longer while the model loads.
  If Ollama uses a non-default port, set OLLAMA_HOST before running:
  PowerShell: $env:OLLAMA_HOST="http://127.0.0.1:11435"
  Bash: export OLLAMA_HOST="http://127.0.0.1:11435"
