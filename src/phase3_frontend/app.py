from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging
from pathlib import Path
from typing import Optional

from src.phase1_preprocessing.config import load_config

logger = logging.getLogger(__name__)

app = FastAPI(title="LexRAG Simple UI")

here = Path(__file__).parent
templates = Jinja2Templates(directory=str(here / "templates"))
app.mount("/static", StaticFiles(directory=str(here / "static")), name="static")


@app.on_event("startup")
def startup_load_index() -> None:
    """Attempt to load FAISS index and encoder at startup if present in config."""
    try:
        config = load_config()
        index_path = Path(config.embedding.index_path)
        metadata_path = Path(config.embedding.metadata_path)
        if index_path.exists() and metadata_path.exists():
            logger.info("Loading FAISS index from %s", index_path)
            # import embedding helpers lazily to avoid loading heavy deps at import-time
            from src.phase1_preprocessing.embedder import load_faiss_index

            app.state.index, app.state.metadata_map, app.state.encoder = load_faiss_index(
                index_path, metadata_path, config.embedding.model_name
            )
            logger.info("Index loaded with %d vectors", app.state.index.ntotal)
        else:
            logger.warning("FAISS index or metadata not found; search will be unavailable until built.")
            app.state.index = None
            app.state.metadata_map = None
            app.state.encoder = None
    except Exception as exc:  # pragma: no cover - runtime environment dependent
        logger.exception("Failed to load index at startup: %s", exc)
        app.state.index = None
        app.state.metadata_map = None
        app.state.encoder = None


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/search", response_class=HTMLResponse)
async def search(request: Request) -> HTMLResponse:
    """Handle form submissions without using FastAPI's `Form` helpers.

    We avoid `Form(...)` in the function signature so FastAPI does not require
    `python-multipart` at import time (which caused the RuntimeError earlier).
    The form is parsed at runtime instead.
    """
    ctx = {"request": request, "query": None, "results": [], "error": None}
    try:
        form = await request.form()
        query = form.get("query")
        top_k = int(form.get("top_k", 5) or 5)
        ctx["query"] = query

        if not getattr(app.state, "index", None):
            raise RuntimeError("FAISS index not loaded. Run the pipeline to build embeddings and index first.")

        # import retrieval function lazily
        from src.phase1_preprocessing.embedder import retrieve_documents

        results = retrieve_documents(query, app.state.index, app.state.metadata_map, app.state.encoder, top_k=top_k)
        ctx["results"] = results
    except Exception as exc:
        logger.exception("Search failed: %s", exc)
        ctx["error"] = str(exc)

    return templates.TemplateResponse("results.html", ctx)


if __name__ == "__main__":  # pragma: no cover - local dev entry
    import uvicorn

    uvicorn.run("src.phase3_frontend.app:app", host="0.0.0.0", port=8000, reload=True)
