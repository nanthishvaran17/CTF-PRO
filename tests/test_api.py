import pytest
import io
from pathlib import Path
from httpx import AsyncClient, ASGITransport
from backend.ctfx.main import app
from backend.ctfx.db.session import init_db

@pytest.mark.asyncio
async def test_full_api_workflow(tmp_path: Path):
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Health check
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"

        # 2. Check dashboard stats (should be clean/empty)
        stats_resp = await client.get("/api/v1/dashboard/stats")
        assert stats_resp.status_code == 200
        stats = stats_resp.json()
        assert "challenges_total" in stats
        assert "tools_installed" in stats

        # 3. Create challenge
        c_payload = {
            "title": "Operation Ghost Cipher",
            "category": "Forensics",
            "description": "Investigate network capture and extract the hidden flag. Flag format: FLAG{...}"
        }
        create_resp = await client.post("/api/v1/challenges", json=c_payload)
        assert create_resp.status_code == 201
        c_data = create_resp.json()
        c_id = c_data["id"]

        # 4. Upload file with planted flag
        file_content = b"HEAD_DATA\x00FLAG{api_end_to_end_verified_flag}\x00TAIL_DATA"
        files = {
            "files": ("capture.bin", file_content, "application/octet-stream")
        }
        upload_resp = await client.post(f"/api/v1/challenges/{c_id}/files", files=files)
        assert upload_resp.status_code == 200
        upload_data = upload_resp.json()
        assert upload_data["uploaded_count"] == 1
        uploaded_sha = upload_data["files"][0]["sha256"]

        # 5. Start analysis
        analysis_resp = await client.post(f"/api/v1/analysis/{c_id}/start")
        assert analysis_resp.status_code == 200
        job_id = analysis_resp.json()["job_id"]

        # Wait a moment for background task
        import asyncio
        for _ in range(20):
            await asyncio.sleep(0.1)
            status_resp = await client.get(f"/api/v1/analysis/{c_id}/status")
            if status_resp.json()["status"] in ("COMPLETED", "FAILED"):
                break

        # 6. Verify candidates discovered
        flags_resp = await client.get(f"/api/v1/flags/candidates?challenge_id={c_id}")
        assert flags_resp.status_code == 200
        candidates = flags_resp.json()
        assert len(candidates) >= 1
        cand = [c for c in candidates if "FLAG{api_end_to_end_verified_flag}" in c["flag"]][0]
        cand_id = cand["id"]

        # 7. Check hex view with byte range offset
        # Get file ID
        c_detail = (await client.get(f"/api/v1/challenges/{c_id}")).json()
        file_id = c_detail["files"][0]["id"]
        hex_resp = await client.get(f"/api/v1/files/{file_id}/hex?offset=0&length=64")
        assert hex_resp.status_code == 200
        assert len(hex_resp.json()["rows"]) >= 1

        # 8. Check evidence deep link
        ev_resp = await client.get(f"/api/v1/flags/{cand_id}/evidence")
        assert ev_resp.status_code == 200
        assert len(ev_resp.json()["evidence_snippets"]) >= 1

        # 9. Authoritative Validation
        val_payload = {
            "validator": "ctfd_scoreboard_api",
            "is_success": True,
            "raw_response": '{"status": "correct", "points": 100}'
        }
        val_resp = await client.post(f"/api/v1/flags/{cand_id}/validate", json=val_payload)
        assert val_resp.status_code == 200
        assert val_resp.json()["status"] == "VERIFIED-BY-CHALLENGE"

        # 10. Check Evidence Graph
        graph_resp = await client.get(f"/api/v1/challenges/{c_id}/evidence-graph")
        assert graph_resp.status_code == 200
        graph = graph_resp.json()
        assert len(graph["nodes"]) >= 2
        assert len(graph["edges"]) >= 1

        # 11. Check Markdown Writeup
        writeup_resp = await client.get(f"/api/v1/challenges/{c_id}/writeup")
        assert writeup_resp.status_code == 200
        assert "Operation Ghost Cipher" in writeup_resp.json()["writeup_markdown"]

        # 12. Check Smart Triage
        triage_resp = await client.get(f"/api/v1/challenges/{c_id}/triage")
        assert triage_resp.status_code == 200
        assert "ai_hypothesis" in triage_resp.json()

        # 13. Generate Reports in HTML and JSON
        rep_resp = await client.post("/api/v1/reports/generate", json={"challenge_id": c_id, "format": "HTML"})
        assert rep_resp.status_code == 200
        report_id = rep_resp.json()["report_id"]

        # Download report
        dl_resp = await client.get(f"/api/v1/reports/{report_id}/download")
        assert dl_resp.status_code == 200
        assert b"<!DOCTYPE html>" in dl_resp.content

        # 14. Tools Inventory Endpoint
        tools_resp = await client.get("/api/v1/tools")
        assert tools_resp.status_code == 200
        assert len(tools_resp.json()) >= 10
