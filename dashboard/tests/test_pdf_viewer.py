from __future__ import annotations

import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from dashboard import server


FRONTEND = Path(__file__).resolve().parents[1] / "frontend"
PAPER_JS = FRONTEND / "static" / "js" / "paper.js"
PAPER_HTML = FRONTEND / "pages" / "paper.html"
PDF_HTML = FRONTEND / "pages" / "pdf.html"
PDFJS = FRONTEND / "static" / "vendor" / "pdfjs" / "pdf.min.mjs"
WORKER = FRONTEND / "static" / "vendor" / "pdfjs" / "pdf.worker.min.mjs"


class PdfViewerTests(unittest.TestCase):
    def test_paper_page_mounts_canvas_viewer(self) -> None:
        page = PAPER_HTML.read_text(encoding="utf-8")
        script = PAPER_JS.read_text(encoding="utf-8")
        standalone = PDF_HTML.read_text(encoding="utf-8")

        self.assertIn("pdf-viewer.js", page)
        self.assertIn("SciCodePdfViewer.mount", script)
        self.assertNotIn("<iframe", script)
        self.assertIn("pdf.html?id=", script)
        self.assertIn("SciCodePdfViewer.mount", standalone)
        self.assertTrue(PDFJS.is_file())
        self.assertTrue(WORKER.is_file())

    def test_pdf_endpoint_returns_file_bytes(self) -> None:
        paper_id = next(path.parent.name for path in server.PAPERS_ROOT.glob("*/paper.pdf"))
        client = TestClient(server.app)
        response = client.get(f"/api/papers/{paper_id}/pdf")
        library = client.get("/static/vendor/pdfjs/pdf.min.mjs")
        worker = client.get("/static/vendor/pdfjs/pdf.worker.min.mjs")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "application/pdf")
        self.assertTrue(response.content.startswith(b"%PDF"))
        self.assertEqual(library.status_code, 200)
        self.assertIn("javascript", library.headers["content-type"])
        self.assertEqual(worker.status_code, 200)
        self.assertIn("javascript", worker.headers["content-type"])
