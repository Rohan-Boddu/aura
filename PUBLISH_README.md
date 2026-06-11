# AURA 4.0 — Clean Repository Contents

This publish/ folder contains **exactly** the files that should exist in the public GitHub repository.

## Included (Clean & Professional)
- ura/                 — Core engines (AST, Chronos, Evidence, Risk, Intent, etc.)
- docs/                 — Architecture diagram, Agent Contract, OpenAPI spec
- integration/          — Azure AI Foundry + Semantic Kernel integration (your key strength)
- 	ests/                — 17 real-data tests (no mocks, real git + AST)
- logo/                 — Branding assets
- server.py             — Main Flask server
- un.bat               — Premium one-click launcher (checks deps first)
- equirements.txt
- README.md             — Judge-friendly documentation
- pitch_deck_and_demo.md
- HTML frontend (ingest + dashboard + loading + intro)
- .gitignore
- LICENSE (MIT)

## What was deliberately excluded
- All recordings, video scripts, personal notes
- __pycache__, generated matrices
- web_automation/ tools and MP4s
- Old "project code base" folder name
- Duplicate / junk files

## How to push this to GitHub

Option A (recommended):
  1. Delete everything in your current git working tree except .git
  2. Copy the *contents* of this publish/ folder into the root
  3. git add . && git commit -m "chore: clean publish-ready AURA 4.0 tree" && git push

Option B:
  cd publish
  git init
  git remote add origin <your-repo-url>
  git add .
  git commit -m "Initial clean submission"
  git branch -M main
  git push -u origin main

This structure directly addresses the "incomplete / messy repo" feedback from the review.
