import fitz
from typing import List, Dict, Any
from pathlib import Path
from app.core.logging import get_logger

logger = get_logger(__name__)


class OCREngine:
    def __init__(self):
        self._ocr = None

    def _get_ocr(self):
        if self._ocr is None:
            try:
                from paddleocr import PaddleOCR
                self._ocr = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
            except Exception as e:
                logger.error("paddleocr_init_failed", error=str(e))
                raise
        return self._ocr

    def ocr_pdf_page(self, file_path: Path, page_num: int) -> Dict[str, Any]:
        doc = fitz.open(file_path)
        page = doc[page_num]
        pix = page.get_pixmap(dpi=200)
        img_bytes = pix.tobytes("png")
        doc.close()

        ocr = self._get_ocr()
        try:
            result = ocr.ocr(img_bytes, cls=True)
            if result and result[0]:
                texts = []
                confidences = []
                for line in result[0]:
                    if len(line) >= 2:
                        texts.append(line[1][0])
                        confidences.append(line[1][1])
                return {
                    "page_number": page_num + 1,
                    "text": "\n".join(texts),
                    "has_text": len(texts) > 0,
                    "ocr_confidence": sum(confidences) / len(confidences) if confidences else 0.0,
                    "ocr_status": "success",
                }
            return {
                "page_number": page_num + 1,
                "text": "",
                "has_text": False,
                "ocr_confidence": 0.0,
                "ocr_status": "empty",
            }
        except Exception as e:
            logger.error("ocr_page_failed", page=page_num + 1, error=str(e))
            return {
                "page_number": page_num + 1,
                "text": "",
                "has_text": False,
                "ocr_confidence": 0.0,
                "ocr_status": "error",
                "error": str(e),
            }

    def process_pdf(self, file_path: Path) -> List[Dict[str, Any]]:
        doc = fitz.open(file_path)
        num_pages = len(doc)
        doc.close()

        results = []
        for page_num in range(num_pages):
            page_text = self.ocr_pdf_page(file_path, page_num)
            results.append(page_text)
        return results


def needs_ocr(pages: List[Dict[str, Any]], min_text_per_page: int = 50) -> List[int]:
    ocr_pages = []
    for i, page in enumerate(pages):
        if not page.get("has_text", False) or len(page.get("text", "").strip()) < min_text_per_page:
            ocr_pages.append(i)
    return ocr_pages


ocr_engine = OCREngine()