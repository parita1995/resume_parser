#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os, io, json, re
from pathlib import Path
from typing import Dict, List
import fitz  # PyMuPDF
from pdfminer.high_level import extract_text as pdfminer_extract
import docx
from pydantic import BaseModel, Field, field_validator


# In[ ]:


# ===== Output schema =====
class ResumeOut(BaseModel):
    name: str = Field(..., description="Full candidate name")
    email: str = Field(..., description="Primary email address")
    skills: List[str] = Field(default_factory=list, description="List of distinct skills")

    @field_validator("name")
    @classmethod
    def _n(cls, v: str) -> str:
        return " ".join(v.split()).strip().title()

    @field_validator("email")
    @classmethod
    def _e(cls, v: str) -> str:
        return v.strip().lower()


# In[ ]:


# ===== Text extraction =====
def read_text(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".pdf":
        try:
            with fitz.open(path) as doc:
                blocks = []
                for pg in doc:
                    for x0,y0,x1,y1,txt,*_ in pg.get_text("blocks"):
                        if txt and txt.strip():
                            blocks.append((int(y0), int(x0), txt.strip()))
                blocks.sort(key=lambda t: (t[0], t[1]))
                text = "\n".join(b[2] for b in blocks)
        except Exception:
            text = ""
        if not text.strip() and path.stat().st_size < 5_000_000:
            try:
                text = pdfminer_extract(str(path)) or ""
            except Exception:
                text = ""
        return text
    elif ext == ".docx":
        d = docx.Document(str(path))
        return "\n".join(p.text for p in d.paragraphs)
    else:
        raise ValueError(f"Unsupported: {ext}")


# In[ ]:


# ===== Prompting helpers =====
MAX_CHARS = 8000
def truncate(s: str, max_chars: int = MAX_CHARS) -> str:
    s = s.strip()
    return s if len(s) <= max_chars else s[:max_chars]
    
SYSTEM_INSTRUCTIONS = (
    "You extract structured data. "
    "Return ONLY valid JSON that matches the schema. "
    "Rules: dedupe skills, use canonical names if obvious, no prose."
)

USER_TEMPLATE = (
    "Extract name, primary email, and skills from this resume text.\n\n"
    "=== RESUME TEXT START ===\n{chunk}\n=== RESUME TEXT END ==="
)

EMAIL_RX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,24}\b")


# In[ ]:


def postprocess(d: Dict) -> ResumeOut:
    m = EMAIL_RX.search((d.get("email") or "")) or EMAIL_RX.search(d.get("name",""))
    email = m.group(0).lower() if m else ""
    seen=set(); skills=[]
    for s in d.get("skills") or []:
        k=s.strip().lower()
        if k and k not in seen: seen.add(k); skills.append(s.strip())
    return ResumeOut(name=d.get("name","").strip(), email=email, skills=skills)


# In[ ]:


def repair_or_fill(json_text: str) -> Dict:
    try:
        d = json.loads(json_text)
    except Exception:
        m = re.search(r"\{.*\}", json_text, flags=re.S)
        d = json.loads(m.group(0)) if m else {}
    return {"name": d.get("name",""), "email": d.get("email",""), "skills": d.get("skills", [])}


# In[ ]:


def ensure_ollama(host: str | None = None) -> None:
    import urllib.request, json, os
    host = host or os.getenv("OLLAMA_HOST","http://127.0.0.1:11434")
    try:
        with urllib.request.urlopen(f"{host}/api/tags", timeout=3) as r:
            json.load(r)  # ok
    except Exception as e:
        raise RuntimeError(f"Ollama not reachable at {host}. Start it or set OLLAMA_HOST. Details: {e}")


# In[ ]:


def parse_with_ollama(resume_text: str, model: str = "llama3.1:8b") -> ResumeOut:
    """
    Requires: pip install ollama; and the Ollama daemon running.
    Example models: 'llama3.1:8b', 'phi3:mini', 'mistral:7b'.
    """
    import ollama
    ensure_ollama()
    schema = {"name":"", "email":"", "skills":[]}
    user = (
        "Extract name, primary email, and skills. "
        "Return JSON with keys exactly: name, email, skills.\n"
        f"Schema example:\n{json.dumps(schema, indent=2)}\n\n"
        f"{USER_TEMPLATE.format(chunk=truncate(resume_text))}"
    )
    resp = ollama.chat(
        model=model,
        format="json",
        messages=[
            {"role":"system", "content": SYSTEM_INSTRUCTIONS},
            {"role":"user", "content": user},
        ],
        options={"temperature": 0, "num_ctx": 2048, "num_predict": 256}
    )
    data = repair_or_fill(resp["message"]["content"])
    return postprocess(data)


# In[ ]:


# ===== Orchestrator (free only) =====
def parse_resume_llm(path: Path, model: str = "llama3.1:8b") -> ResumeOut:
    text = read_text(path)
    return parse_with_ollama(text, model=model)

# ===== Batch =====
def batch_folder(folder: Path, model: str = "llama3.1:8b") -> List[ResumeOut]:
    outs=[]
    for p in sorted(folder.iterdir()):
        if p.suffix.lower() not in {".pdf",".docx"}: continue
        try:
            outs.append(parse_resume_llm(p, model=model))
        except Exception as e:
            outs.append(ResumeOut(name="", email="", skills=[f"ERROR: {e}"]))  # visible in UI
    return outs


# In[ ]:


if __name__ == "__main__":
    import argparse, json
    ap = argparse.ArgumentParser()
    ap.add_argument("--resumes", required=True, help="Folder with PDF/DOCX")
    ap.add_argument("--model", default="llama3.1:8b", help="Ollama model tag")
    ap.add_argument("--dump_json", default="preds.jsonl")
    args = ap.parse_args()

    folder = Path(args.resumes)
    with open(args.dump_json, "w", encoding="utf-8") as f:
        for p in sorted(folder.iterdir()):
            if p.suffix.lower() not in {".pdf",".docx"}:
                continue
            rec = parse_resume_llm(p, model=args.model.strip())
            row = rec.model_dump()
            row["file"] = p.name
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            print(row)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




