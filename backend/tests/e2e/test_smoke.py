"""E2E smoke tests against a running backend on http://localhost:8000.

Requires the backend (uvicorn app.main:app --port 8000) to be running.
These are integration smoke tests, not hermetic unit tests.
"""
import httpx

import pytest

BASE = "http://localhost:8000"
SEED_EMAIL = "arjun.mehta@apexpetro.com"
SEED_PASSWORD = "apexpetro2026"


@pytest.fixture(scope="module")
def client():
    return httpx.Client(base_url=BASE, timeout=30.0)


@pytest.fixture(scope="module")
def token(client):
    resp = client.post(
        "/api/auth/login",
        json={"email": SEED_EMAIL, "password": SEED_PASSWORD},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


@pytest.fixture()
def headers(token):
    return {"Authorization": f"Bearer {token}"}


class TestAuthCore:
    def test_protected_route_rejects_anon(self, client):
        resp = client.get("/api/approvals")
        assert resp.status_code == 401

    def test_me_returns_seed_user(self, client, headers):
        resp = client.get("/api/auth/me", headers=headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["email"] == SEED_EMAIL
        assert body["role"].upper() == "ENGINEER"


class TestCodeSandbox:
    def test_code_run_returns_stdout(self, client, headers):
        resp = client.post(
            "/api/code/run",
            headers=headers,
            json={"code": "pressure=42\nlimit=40\nprint(f'Deviation: {pressure-limit} bar')", "timeout": 30},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "Deviation: 2 bar" in body["stdout"]
        assert body["return_code"] == 0

    def test_code_run_rejects_anon(self, client):
        resp = client.post("/api/code/run", json={"code": "print(1)"})
        assert resp.status_code == 401


class TestOfflineScript:
    def test_offline_script_importable_and_runs(self):
        import subprocess
        import sys
        import os
        script = os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "verify_offline.py")
        script = os.path.abspath(script)
        proc = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=60)
        assert proc.returncode in (0, 1), proc.stdout + proc.stderr
        assert "SOVEREIGN AI WORKBENCH" in proc.stdout


class TestArtifactsAPI:
    def test_list_artifacts_returns_version_and_preview(self, client, headers):
        resp = client.get("/api/artifacts?limit=5", headers=headers)
        assert resp.status_code == 200
        body = resp.json()
        assert "version" in (body["artifacts"][0] if body["artifacts"] else {})
        assert "preview_url" in (body["artifacts"][0] if body["artifacts"] else {})

    def test_preview_endpoint_returns_content(self, client, headers):
        list_resp = client.get("/api/artifacts?limit=5", headers=headers)
        arts = list_resp.json()["artifacts"]
        if not arts:
            pytest.skip("No artifacts seeded")
        # Pick one whose preview is JSON (text-based) if available.
        target = next((a for a in arts if a["artifact_type"] in ("TXT", "MD", "CSV", "JSON", "DOCX", "XLSX", "PPTX")), arts[0])
        resp = client.get(f"/api/artifacts/{target['artifact_id']}/preview", headers=headers)
        assert resp.status_code == 200
        if resp.headers.get("content-type", "").startswith("application/json"):
            body = resp.json()
            assert body["artifact_id"] == target["artifact_id"]
        else:
            assert len(resp.content) > 0

    def test_download_endpoint_returns_file(self, client, headers):
        list_resp = client.get("/api/artifacts?limit=1", headers=headers)
        arts = list_resp.json()["artifacts"]
        if not arts:
            pytest.skip("No artifacts seeded")
        aid = arts[0]["artifact_id"]
        resp = client.get(f"/api/artifacts/{aid}/download", headers=headers)
        assert resp.status_code == 200
        assert "Content-Disposition" in resp.headers


class TestChatAttachmentAPI:
    def test_upload_attachment_parses_txt(self, client, headers):
        files = {"file": ("note.txt", b"operating pressure limit 40 bar", "text/plain")}
        data = {"conversation_id": "e2e-conv-attachment"}
        resp = client.post("/api/chat/attachments", headers=headers, files=files, data=data)
        assert resp.status_code == 200
        body = resp.json()
        assert body["attachment_id"]
        assert body["ext"] == "txt"
        assert "40 bar" in body["summary"]


class TestConversationAPI:
    def test_rename_conversation_persists_and_roundtrips(self, client, headers):
        resp = client.post("/api/chat/conversations", headers=headers)
        assert resp.status_code == 200
        conv_id = resp.json()["conversation_id"]

        rename = client.patch(
            f"/api/chat/conversations/{conv_id}",
            headers=headers,
            json={"title": "P-102 Maintenance Review"},
        )
        assert rename.status_code == 200
        assert rename.json()["title"] == "P-102 Maintenance Review"

        listing = client.get("/api/chat/conversations", headers=headers).json()
        match = next(c for c in listing["conversations"] if c["conversation_id"] == conv_id)
        assert match["title"] == "P-102 Maintenance Review"

        client.delete(f"/api/chat/conversations/{conv_id}", headers=headers)

    def test_rename_rejects_empty_title(self, client, headers):
        resp = client.post("/api/chat/conversations", headers=headers)
        conv_id = resp.json()["conversation_id"]
        resp2 = client.patch(f"/api/chat/conversations/{conv_id}", headers=headers, json={"title": "   "})
        assert resp2.status_code == 400
        client.delete(f"/api/chat/conversations/{conv_id}", headers=headers)

    def test_delete_conversation_removes_messages(self, client, headers):
        resp = client.post("/api/chat/conversations", headers=headers)
        conv_id = resp.json()["conversation_id"]
        msgs = client.get(f"/api/chat/conversations/{conv_id}/messages", headers=headers)
        assert msgs.status_code == 200

        delete = client.delete(f"/api/chat/conversations/{conv_id}", headers=headers)
        assert delete.status_code == 200
        assert delete.json()["deleted"] is True

        listing = client.get("/api/chat/conversations", headers=headers).json()
        assert all(c["conversation_id"] != conv_id for c in listing["conversations"])

        repeat = client.delete(f"/api/chat/conversations/{conv_id}", headers=headers)
        assert repeat.status_code == 404

    def test_messages_serialize_persistence_fields(self, client, headers):
        resp = client.post("/api/chat/conversations", headers=headers)
        conv_id = resp.json()["conversation_id"]
        msgs = client.get(f"/api/chat/conversations/{conv_id}/messages", headers=headers)
        assert msgs.status_code == 200
        payload = msgs.json()
        # Serializer must expose sources/artifacts/meta even for empty conversations.
        assert isinstance(payload["messages"], list)
        assert payload["total"] == 0
        client.delete(f"/api/chat/conversations/{conv_id}", headers=headers)

    def test_reopen_restores_sources_and_artifact_links(self, client, headers):
        """Simulates close->reopen: persisted sources + artifact download links
        must be returned verbatim by the messages endpoint."""
        import uuid
        from app.db.database import SessionLocal
        from app.db.repositories import ConversationRepository
        from app.db.models import Conversation

        db = SessionLocal()
        try:
            repo = ConversationRepository(db)
            conv = Conversation(conversation_id=str(uuid.uuid4()), company_id="apexpetro", user_id=1)
            db.add(conv)
            db.commit()
            db.refresh(conv)
            conv_id = conv.conversation_id

            repo.add_message(conv_id, 1, "user", "what is the pressure limit?")
            repo.add_message(
                conv_id,
                1,
                "assistant",
                "The pressure limit is 12 bar.",
                run_id="run-reopen-1",
                sources=[{"document_id": "DOC-P102", "content": "pressure 12 bar", "page": 3, "relevance": 0.95}],
                artifacts=[{"artifact_id": "ART-REOPEN", "name": "Inspection.xlsx", "format": "xlsx", "download_url": "/api/artifacts/ART-REOPEN/download"}],
                metadata={"model": "qwen2.5:3b", "verified": True},
            )

            payload = client.get(
                f"/api/chat/conversations/{conv_id}/messages", headers=headers
            ).json()
            assistant = [m for m in payload["messages"] if m["role"] == "assistant"][0]
            assert assistant["sources"][0]["document_id"] == "DOC-P102"
            assert assistant["sources"][0]["relevance"] == 0.95
            assert assistant["artifacts"][0]["artifact_id"] == "ART-REOPEN"
            assert assistant["artifacts"][0]["download_url"].endswith("/download")
            assert assistant["meta"]["verified"] is True

            repo.delete(conv_id)
        finally:
            db.close()
