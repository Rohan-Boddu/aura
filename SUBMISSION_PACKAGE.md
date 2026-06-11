# AURA 4.0 — Agents League Hackathon Submission Package

**Track Recommendation:** Reasoning Agents (Microsoft Foundry)

## Required Submission Artifacts (per official rules)

1. **Project Description** (in the submission form)
2. **Demo Video** (YouTube or Vimeo, max 5 minutes)
3. **Public GitHub Repository** (with source code)
4. **Architecture Diagram** (illustrating Microsoft Foundry usage)

All of these are now prepared or heavily supported in this repo.

---

## What Has Been Prepared

### 1. Architecture Diagram (Required)
- **Primary file:** `docs/architecture_diagram.md`
  - Contains high-quality Mermaid diagram
  - Detailed explanation of how AURA 4.0 integrates with Azure AI Foundry via ToolSet
  - Instructions for rendering to PNG/SVG
- **Generated visual:** An AI-generated diagram image was created (see session images folder or re-generate from the Mermaid).

**Action for you:**
- Open `docs/architecture_diagram.md` in a Markdown viewer or paste the Mermaid into https://mermaid.live
- Export as high-resolution PNG
- Name it `aura-4-0-architecture-diagram.png` and place it in the root of your public GitHub repo or in a `docs/` folder.

### 2. GitHub Repository
Your current workspace is the project. Make sure to push:
- The `integration/` folder (critical for proving real Foundry usage)
- `docs/` folder (agent_contract.md + architecture_diagram.md + openapi.json)
- Updated `README.md`
- `server.py` with the new agent contract endpoints
- `project code base/core/architecture_intelligence.py`

### 3. Pitch & Demo Materials
- `pitch_deck_and_demo.md` — Complete 45-second pitch script + detailed demo steps + video structure
- `README.md` — Now submission-ready and judge-friendly

### 4. Supporting Docs
- `docs/agent_contract.md` — Excellent for judges (shows the clean agent-facing contract + Foundry mapping)
- `docs/openapi.json` — Can be mentioned as ready for portal import

---

## Recommended 5-Minute Demo Video Structure

Use the script in `pitch_deck_and_demo.md`.

Suggested timeline:
- **0:00 – 0:45** — Condensed 45-second pitch (use the 3-slide script)
- **0:45 – 2:30** — Live human demo (ingest demo repo → goal → 9-stage timeline → blast radius graph with shadow coupling highlighted → verification checklist)
- **2:30 – 4:00** — Show the Foundry integration proof (most important part for judges):
  1. Start AURA server + load the demo repo (so you have a real analysis_id).
  2. Run: `python integration/foundry_agent.py --test-tools`
     - This shows clear [AURA TOOL CALLED FROM FOUNDRY AGENT] logs + real JSON responses for all 4 tools.
     - This is excellent visible proof that the contract works.
  3. (Stronger if possible) Set your `AZURE_AIPROJECTS_CONNECTION_STRING` and run the script normally.
     - Show the "Agent created successfully! Agent ID: ..." output.
  4. Quickly show the architecture diagram (docs/architecture_diagram.md rendered as PNG).
- **4:00 – 5:00** — Show the architecture diagram + quick summary of why this fits the Reasoning Agents track (multi-step reasoning + reliability/safety + real Microsoft SDK usage)

**Tips:**
- Speak slowly and point at the screen.
- Emphasize "read-only", "cited evidence", and "the agent is forced to consult AURA before proposing changes".
- End with: "This gives Foundry agents the architectural guardrails they need."

---

## Final Pre-Submission Checklist

- [ ] Render and include a clear `architecture_diagram.png` (from `docs/architecture_diagram.md`)
- [ ] Record and upload the demo video (unlisted on YouTube or Vimeo)
- [ ] Clean up your public GitHub repo (remove personal paths like `D:\hackathon` if any, add a good README)
- [ ] Register for the hackathon (if not already) and activate your profile
- [ ] Choose **Reasoning Agents** track (you can also submit to a second track if rules allow)
- [ ] In the submission form, use the text from the updated `README.md` + `pitch_deck_and_demo.md` as base for the project description
- [ ] Attach/link the architecture diagram

---

## Quick Links for Judges / Submission Form

- Architecture Diagram: `docs/architecture_diagram.md` (or the exported PNG)
- Foundry Integration Code: `integration/foundry_agent.py`
- Agent Contract: `docs/agent_contract.md`
- OpenAPI for Custom Tools: `docs/openapi.json`
- Full Pitch + Demo Script: `pitch_deck_and_demo.md`

---

You now have a complete, coherent submission package that tells a strong story:

**AURA 4.0 is not just another agent — it is the missing Architecture Intelligence Layer that makes Azure AI Foundry agents (and other AI coding agents) dramatically safer and more capable when working with real codebases.**

Good luck! If you need any last tweaks (different diagram version, shorter video script, etc.), just ask.