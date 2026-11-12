# CTF HUNTER X - REST API Reference (/api/v1)

## Challenges
- `POST /api/v1/challenges`: Create challenge `{title, category, description, flag_format}`.
- `GET /api/v1/challenges`: List all challenges with counts of files, candidates, and verified flags.
- `GET /api/v1/challenges/{id}`: Detailed challenge record with associated files and flags.
- `DELETE /api/v1/challenges/{id}`: Delete challenge and cascade-remove associated records.

## Files & Hex
- `POST /api/v1/challenges/{id}/files`: Ingest multipart files into content-addressed storage.
- `GET /api/v1/files/{id}/hex?offset=0&length=256`: Stream hex rows with exact decimal and hex byte offsets.

## Analysis & Orchestration
- `POST /api/v1/analysis/{id}/start`: Launch background analysis across all modular engines.
- `GET /api/v1/analysis/{id}/status`: Query current job progress (0-100%) and operational status.
- `GET /api/v1/analysis/{id}/results`: Retrieve structured results from all executed modules.

## Flags & Verification
- `GET /api/v1/flags/candidates`: Query candidate flags with optional status and challenge filters.
- `GET /api/v1/flags/{id}/evidence`: Retrieve full cryptographic evidence snippets and decode steps.
- `POST /api/v1/flags/{id}/validate`: Record authoritative scoreboard validation event `{is_success, validator, notes}`.
- `GET /api/v1/flags/{id}/repro`: Export executable Python reproduction script.

## Intelligence & Reports
- `GET /api/v1/challenges/{id}/evidence-graph`: Retrieve DAG nodes and edges for visualization.
- `GET /api/v1/challenges/{id}/writeup`: Generate complete Markdown writeup.
- `POST /api/v1/reports/generate`: Compile report in HTML, JSON, CSV, or PDF format.
- `GET /api/v1/reports/{id}/download`: Download generated report file.
- `GET /api/v1/dashboard/stats`: Database-computed statistics.
- `GET /api/v1/events/stream`: Server-Sent Events (SSE) stream for real-time progress.
