"""
api.py — FastAPI backend for the Living Systems Design Lab.

Endpoints:
  GET  /                    — health check
  GET  /presets             — list available presets
  POST /generate            — prompt → segments JSON
  POST /presets/{name}      — run a named preset → segments JSON
  POST /generate/export     — prompt → OBJ wireframe file download

Run with:
  uvicorn api:app --reload

Test at:
  http://127.0.0.1:8000/docs
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from prompt_translate import translate
from engine import MorphogenesisEngine
from export import export_wireframe_obj


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title       = "Living Systems Design Lab API",
    description = (
        "Morphogenesis simulation backend. "
        "Translates natural-language prompts into 3D branching structures."
    ),
    version     = "0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins  = ["*"],   # tighten in production
    allow_methods  = ["*"],
    allow_headers  = ["*"],
)


# ── Pydantic models ───────────────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    prompt: str  = Field(..., example="spiral tower, tall")
    seed:   Optional[int] = Field(None, example=42)


class SegmentOut(BaseModel):
    x1: float; y1: float; z1: float
    x2: float; y2: float; z2: float
    radius:    float
    parent_id: int


class GenerateResponse(BaseModel):
    mode:          str
    segment_count: int
    params:        dict
    segments:      List[SegmentOut]


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/", summary="Health check")
def root() -> dict:
    return {"status": "Living Systems Design Lab API", "version": "0.1.0"}


@app.get("/presets", summary="List preset names")
def list_presets() -> dict:
    return {"presets": ["tree", "coral", "spiral", "shelter"]}


@app.post("/generate", response_model=GenerateResponse, summary="Prompt → segments")
def generate(req: GenerateRequest) -> GenerateResponse:
    params = translate(req.prompt)
    if req.seed is not None:
        params.seed = req.seed

    engine = MorphogenesisEngine(params)
    engine.run()

    if not engine.segments:
        raise HTTPException(
            status_code=422,
            detail="Engine produced no segments for the given prompt.",
        )

    segs = [
        SegmentOut(
            x1=float(s.start[0]), y1=float(s.start[1]), z1=float(s.start[2]),
            x2=float(s.end[0]),   y2=float(s.end[1]),   z2=float(s.end[2]),
            radius    = float(s.radius),
            parent_id = s.parent_id if s.parent_id is not None else -1,
        )
        for s in engine.segments
    ]

    params_dict = {
        k: (v.tolist() if hasattr(v, "tolist") else v)
        for k, v in vars(params).items()
        if v is not None and not callable(v)
    }

    return GenerateResponse(
        mode          = params.mode,
        segment_count = len(segs),
        params        = params_dict,
        segments      = segs,
    )


@app.post(
    "/presets/{name}",
    response_model = GenerateResponse,
    summary        = "Run a named preset",
)
def run_preset(name: str, seed: int = 42) -> GenerateResponse:
    from presets import tree, coral, spiral, shelter

    presets = {"tree": tree, "coral": coral, "spiral": spiral, "shelter": shelter}
    if name not in presets:
        raise HTTPException(
            status_code=404,
            detail=f"Preset '{name}' not found. Choose: tree | coral | spiral",
        )

    params      = presets[name]()
    params.seed = seed

    engine = MorphogenesisEngine(params)
    engine.run()

    segs = [
        SegmentOut(
            x1=float(s.start[0]), y1=float(s.start[1]), z1=float(s.start[2]),
            x2=float(s.end[0]),   y2=float(s.end[1]),   z2=float(s.end[2]),
            radius    = float(s.radius),
            parent_id = s.parent_id if s.parent_id is not None else -1,
        )
        for s in engine.segments
    ]

    params_dict = {
        k: (v.tolist() if hasattr(v, "tolist") else v)
        for k, v in vars(params).items()
        if v is not None and not callable(v)
    }

    return GenerateResponse(
        mode          = params.mode,
        segment_count = len(segs),
        params        = params_dict,
        segments      = segs,
    )


@app.post("/generate/export", summary="Prompt → downloadable OBJ wireframe")
def generate_export(req: GenerateRequest):
    params = translate(req.prompt)
    if req.seed is not None:
        params.seed = req.seed

    engine = MorphogenesisEngine(params)
    engine.run()

    if not engine.segments:
        raise HTTPException(status_code=422, detail="No segments generated.")

    tmp  = tempfile.NamedTemporaryFile(suffix=".obj", delete=False)
    path = export_wireframe_obj(engine, tmp.name)

    return FileResponse(
        path             = path,
        media_type       = "application/octet-stream",
        filename         = f"{params.mode}_structure.obj",
    )
