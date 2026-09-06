import pytest

from app.services.file_document_generator import (
    render_document,
    extract_document_data,
    SUPPORTED_TEMPLATES,
)


DATA = {
    "title": "P-102 Overpressure Approval Note",
    "sections": {
        "Subject": "Overpressure assessment for centrifugal pump P-102",
        "Background": "Operating pressure approached the design limit during a recent test.",
        "Recommendation": ["Reduce operating pressure by 1 bar", "Schedule calibration of relief valve"],
    },
}


class TestFormatRendering:
    @pytest.mark.parametrize("fmt", ["docx", "xlsx", "pptx", "pdf", "txt", "json", "md", "csv"])
    def test_all_expected_formats_render_nonempty(self, fmt):
        content = render_document("approval_note", fmt, DATA)
        assert content, f"{fmt} rendered empty"
        assert isinstance(content, bytes)
        assert len(content) > 20

    def test_txt_contains_title_and_section(self):
        text = render_document("approval_note", "txt", DATA).decode("utf-8")
        assert "P-102 Overpressure Approval Note" in text
        assert "Subject" in text

    def test_json_is_parseable_and_contains_sections(self):
        import json
        raw = render_document("approval_note", "json", DATA).decode("utf-8")
        payload = json.loads(raw)
        assert payload["title"] == DATA["title"]
        assert "sections" in payload

    def test_markdown_contains_heading(self):
        text = render_document("approval_note", "md", DATA).decode("utf-8")
        assert text.startswith("# ")
        assert "## Background" in text

    def test_csv_contains_headers(self):
        text = render_document("approval_note", "csv", DATA).decode("utf-8")
        assert "Field,Value" in text
        assert "sections" in text

    def test_risk_template_allows_new_formats(self):
        assert "csv" in SUPPORTED_TEMPLATES["risk_assessment"]
        assert "json" in SUPPORTED_TEMPLATES["risk_assessment"]
        assert "txt" in SUPPORTED_TEMPLATES["risk_assessment"]

    def test_unsupported_format_raises(self):
        with pytest.raises(ValueError):
            render_document("approval_note", "bogus", DATA)


class TestExtractAndConvert:
    def test_docx_round_trip_preserves_sections(self):
        import os
        b = render_document("approval_note", "docx", DATA)
        tmp = "/tmp/opencode/test_extract.docx"
        os.makedirs("/tmp/opencode", exist_ok=True)
        with open(tmp, "wb") as f:
            f.write(b)
        extracted = extract_document_data(tmp, "docx")
        sections = extracted.get("sections", {})
        # At least one of our section headings round-trips.
        keys = [k.lower() for k in sections.keys()]
        assert any("background" in k for k in keys) or "subject" in keys

    def test_convert_docx_to_pdf_preserves_content(self):
        import os
        b = render_document("approval_note", "docx", DATA)
        tmp = "/tmp/opencode/test_convert.docx"
        with open(tmp, "wb") as f:
            f.write(b)
        data = extract_document_data(tmp, "docx")
        pdf_bytes = render_document("approval_note", "pdf", data)
        assert len(pdf_bytes) > 1000

    def test_xlsx_round_trip_keys(self):
        import os
        risk_data = {
            "title": "Risk Assessment",
            "sheets": {"Summary": {"headers": ["Item", "Detail"], "rows": [["A", "B"]]}},
        }
        b = render_document("risk_assessment", "xlsx", risk_data)
        tmp = "/tmp/opencode/test_extract.xlsx"
        with open(tmp, "wb") as f:
            f.write(b)
        extracted = extract_document_data(tmp, "xlsx")
        assert "Summary" in extracted.get("sheets", {})
        assert extracted["sheets"]["Summary"]["rows"][0] == ["A", "B"]