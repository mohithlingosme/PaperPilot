# PaperPilot — Research-to-Publish Operating System (R‑P OS)

**PaperPilot** is an AI-powered **Research-to-Publish Operating System**: a single workflow that takes you from **sources → search → outline → draft with citations → export**.

> **Core promise:** evidence-backed writing **with a workflow** (not “prompt → random text”).

## Features

- **Source Collection**: Paste URLs, upload PDFs, scan/OCR documents, auto-extract metadata and key points.
- **Research Dashboard**: Library of sources per project, tagging + filtering, outline + research-question tracking.
- **AI Draft Engine**: Summarize sources, build structured outlines, generate drafts with in-text citations linked to sources, multi-source synthesis.
- **Refinement & Publishing**: Built-in editor, export to DOCX/PDF, publish to blog/CMS.

## Tech Stack

- **Frontend**: Node.js
- **Backend**: Python
- **DB**: TBD
- **Infra**: Docker, Kubernetes

## Quickstart (Local Dev)

### Prerequisites
- Node.js 18+
- Python 3.9+
- Docker

### Environment Setup
1. Clone the repo.
2. Install dependencies: `npm install` (root), `pip install -r requirements.txt` (backend).
3. Set up environment variables (see .env.example).

### Run Locally
- Start services: `docker-compose -f infra/ci/docker-compose.ci.yml up`
- Run web: `npm run dev` (from apps/web)
- Run API: `python -m backend.app` (from backend/)
- Run worker: `npm run worker` (from apps/worker)

## Testing

Run unit tests: `npm run test:unit`
Run integration tests: `npm run test`
Run e2e tests: `npm run test:e2e`

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, branch naming, PR rules, testing, and code style.

## Development Plan

See [Development_plan.md](Development_plan.md) for detailed development roadmap.

## License

See [LICENSE](LICENSE).
