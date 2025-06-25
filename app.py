# requirements.txt
# fastapi
# uvicorn
# pdfminer.six
# pandas
# python-multipart
# requests

# app.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pdfminer.high_level import extract_text
from pathlib import Path
import pandas as pd
import os
import logging

app = FastAPI()

INVOICES_DIR = "invoices"

def list_local_pdfs():
    """List all PDF files in the invoices directory."""
    if not os.path.isdir(INVOICES_DIR):
        raise Exception(f"Invoices directory '{INVOICES_DIR}' does not exist.")
    return [f for f in os.listdir(INVOICES_DIR) if f.lower().endswith('.pdf')]

def parse_pdf(filepath):
    """Extract text from a PDF and return as string."""
    try:
        text = extract_text(filepath)
        return text
    except Exception as e:
        raise Exception(f"Failed to parse PDF {filepath}: {str(e)}")

@app.post("/parse_invoice_pdf/")
async def parse_invoice_pdf(request: Request):
    try:
        data = await request.json()
        file_name = data.get("file_name")
        # return {"file": file_name, "text": "tested api"}
        if not file_name:
            return JSONResponse(status_code=400, content={"error": "file_name is required in the request body."})
        pdf_files = list_local_pdfs()
        matched_file = next((f for f in pdf_files if f == file_name), None)
        if not matched_file:
            return JSONResponse(status_code=404, content={"error": f"File '{file_name}' not found in invoices directory."})
        pdf_path = os.path.join(INVOICES_DIR, matched_file)
        text = parse_pdf(pdf_path)
        return {"file": matched_file, "text": text}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# Dockerfile
# ---------------------------
# FROM python:3.11-slim
# WORKDIR /app
# COPY . .
# RUN pip install --no-cache-dir -r requirements.txt
# CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]