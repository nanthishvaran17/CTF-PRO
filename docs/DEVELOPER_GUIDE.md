# CTF HUNTER X - Developer Guide

## System Components
- **Backend**: Python 3.11+, FastAPI, SQLAlchemy 2 (async aiosqlite), Pydantic v2.
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS.
- **Storage Vault**: Content-addressed vault at `data/uploads/`, artifacts at `data/artifacts/`, reports at `data/reports/`.

## Running Backend Tests
Execute pytest with verbose output:
```bash
python -m pytest tests/ -v
```

## Running Static Typechecks and Frontend Build
```bash
cd frontend
npm run build
```

## Code Standards
- All flag discovery logic must record byte offsets, encodings, and methods.
- No simulated or mock data: tests must verify real input transformations.
- Any archive extraction must use `SafeArchiveExtractor` to prevent Zip-Slip vulnerabilities.
