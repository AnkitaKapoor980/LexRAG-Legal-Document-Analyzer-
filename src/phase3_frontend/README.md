# Phase 3 — Streamlit Frontend

This folder contains the Streamlit web application for the LexRAG Legal Document Analyzer.

## Overview

The Streamlit app provides an intuitive interface to:
- Upload PDF contracts
- Extract and analyze legal documents
- View extracted clauses, risk analysis, and compliance checks
- Ask questions about the contract using the Q&A agent

## Running the Frontend

### Option 1: Use the Unified Launcher (Recommended)

From the project root:
```powershell
python scripts/run_app.py
```

This starts both the backend API and the Streamlit frontend together.

### Option 2: Run Streamlit Manually

If you need to run only the frontend:
```powershell
python -m streamlit run src/phase3_frontend/streamlit_app.py
```

> **Note:** The backend API must be running on port 8000 for the frontend to work.

## Features

- **Document Upload**: Upload PDF contracts for analysis
- **Analysis Dashboard**: View results in organized tabs:
  - Summary
  - Extracted Clauses
  - Risk Analysis
  - Compliance Checks
  - Q&A Chat
- **Backend Health Check**: Test connectivity to the API
- **Clear Analysis**: Reset the current analysis

## Configuration

The app connects to the backend API at `http://localhost:8000` by default.

## Troubleshooting

**"streamlit not found" error:**
- Use `python -m streamlit` instead of just `streamlit`
- Or add Python Scripts folder to your PATH (see main README)

**Backend connection errors:**
- Ensure the backend API is running on port 8000
- Check the "Check Backend" button in the UI for diagnostics

**Analysis timeout:**
- Large documents may take time to process
- Default timeout is 300 seconds (5 minutes)

## Dependencies

All dependencies are listed in the project's main `requirements.txt`:
- `streamlit>=1.28.0`
- `pdfplumber>=0.11.0`
- `requests>=2.32.0`
