from app.db.database import SessionLocal
from app.db.models import Message
from app.services.conversation_titles import generate_title
from app.services.chat_attachment_service import (
    clear_conversation_attachments,
    save_chat_attachment,
    build_attachment_context,
    get_conversation_attachments,
)


class TestConversationTitles:
    def test_leave_policy_example(self):
        assert generate_title("Explain how our company's leave policy works") == "Company Leave Policy"

    def test_sales_report_example(self):
        assert generate_title("Create a report on Q3 sales performance") == "Q3 Sales Performance Report"

    def test_inspection_report_reorders_doc_type(self):
        title = generate_title("Create an inspection report for P-102 compliance assessment")
        assert title == "P-102 Compliance Assessment Inspection Report"

    def test_question_extracts_focus(self):
        title = generate_title("What is the maximum operating pressure of pump P-102?")
        assert "P-102" in title and "Maximum" in title

    def test_politeness_stripped(self):
        assert generate_title("can you please tell me about the maintenance procedure?") == "Maintenance Procedure"

    def test_fallback_nonempty_for_gibberish(self):
        assert generate_title("!!!" ) == "!!!"


class TestMessagePersistenceColumns:
    def test_messages_table_has_persistence_columns(self, tmp_path):
        db = SessionLocal()
        try:
            cols = {c.name for c in Message.__table__.columns}
            assert {"sources", "artifacts", "meta", "attachments"} <= cols
        finally:
            db.close()

    def test_add_message_persists_sources_and_artifacts(self):
        import uuid
        db = SessionLocal()
        try:
            from app.db.repositories import ConversationRepository
            from app.db.models import Conversation
            repo = ConversationRepository(db)
            conv = Conversation(conversation_id=str(uuid.uuid4()), company_id="apexpetro", user_id=1)
            db.add(conv)
            db.commit()
            db.refresh(conv)
            conv_id = conv.conversation_id

            msg = repo.add_message(
                conv_id,
                1,
                "assistant",
                "answer text",
                run_id="run-1",
                sources=[{"document_id": "DOC-1", "content": "x", "relevance": 0.9}],
                artifacts=[{"artifact_id": "ART-1", "download_url": "/api/artifacts/ART-1/download"}],
                metadata={"model": "qwen2.5:3b", "verified": True},
            )
            db.refresh(msg)
            assert msg.sources[0]["document_id"] == "DOC-1"
            assert msg.artifacts[0]["artifact_id"] == "ART-1"
            assert msg.meta["verified"] is True

            loaded = db.query(Message).filter(Message.message_id == msg.message_id).first()
            assert loaded.sources == msg.sources
            assert loaded.artifacts == msg.artifacts
            assert loaded.meta["model"] == "qwen2.5:3b"

            repo.delete(conv_id)
        finally:
            db.close()


class TestAttachmentRestoreFromMessages:
    def test_attachment_context_rebuilds_from_persisted_messages(self):
        import uuid
        conv_id = "persist-conv-test"
        clear_conversation_attachments(conv_id)
        save_chat_attachment(conv_id, "vib.csv", b"id,val\nn1,7.5\n")
        record = get_conversation_attachments(conv_id)[0]
        assert build_attachment_context(conv_id)

        db = SessionLocal()
        try:
            from app.db.repositories import ConversationRepository
            from app.db.models import Conversation
            repo = ConversationRepository(db)
            conv = Conversation(conversation_id=str(uuid.uuid4()), company_id="apexpetro", user_id=1)
            db.add(conv)
            db.commit()
            db.refresh(conv)
            conv.conversation_id = conv_id
            db.commit()

            repo.add_message(conv_id, 1, "user", "why is it high?", attachments=[{
                "attachment_id": record["attachment_id"],
                "filename": record["filename"],
                "ext": record["ext"],
                "file_path": record["file_path"],
                "size": record["size"],
                "summary": record["summary"],
            }])

            clear_conversation_attachments(conv_id)  # simulate restart (in-memory index lost)
            ctx = build_attachment_context(conv_id, db=db)
            assert "7.5" in ctx or "vib" in ctx

            repo.delete(conv_id)
        finally:
            db.close()
            clear_conversation_attachments(conv_id)