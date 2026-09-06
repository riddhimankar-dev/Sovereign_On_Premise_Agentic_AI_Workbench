import os

from app.tools.base import tool_registry
from app.services.chat_attachment_service import (
    save_chat_attachment,
    get_conversation_attachments,
    build_attachment_context,
    parse_to_text,
)


class TestToolRegistryDocTools:
    def test_generate_document_registered(self):
        assert tool_registry.get("generate_document") is not None

    def test_update_artifact_registered(self):
        tool = tool_registry.get("update_artifact")
        assert tool is not None
        assert tool.permission == "write"

    def test_convert_artifact_registered(self):
        assert tool_registry.get("convert_artifact") is not None

    def test_all_names_present_in_registry(self):
        names = tool_registry.list_tools()
        for expected in ["generate_document", "update_artifact", "convert_artifact",
                         "search_documents", "calculate", "analyze_data"]:
            assert expected in names


class TestChatAttachmentParsing:
    def test_txt_parsing_returns_text(self, tmp_path):
        p = tmp_path / "note.txt"
        p.write_text("operating pressure is 40 bar")
        text = parse_to_text(str(p), "txt")
        assert "40 bar" in text

    def test_json_parsing_returns_valid_json(self, tmp_path):
        import json
        p = tmp_path / "data.json"
        p.write_text(json.dumps({"limit": 42}))
        text = parse_to_text(str(p), "json")
        assert '"limit"' in text

    def test_csv_parsing_returns_rows(self, tmp_path):
        p = tmp_path / "table.csv"
        p.write_text("item,status\nP-102,OPEN\n")
        text = parse_to_text(str(p), "csv")
        assert "P-102" in text

    def test_save_and_retrieve_attachment_are_chat_scoped(self, tmp_path):
        content = b"pump pressure 40 bar"
        rec = save_chat_attachment("conv-A", "note.txt", content)
        assert rec["attachment_id"]
        assert rec["ext"] == "txt"
        assert get_conversation_attachments("conv-A")
        # Different conversation must not see it (chat-scoped).
        assert get_conversation_attachments("conv-B") == []
        ctx = build_attachment_context("conv-A")
        assert "40 bar" in ctx

    def test_build_attachment_context_empty_when_none(self):
        assert build_attachment_context("conv-emptynone") == ""