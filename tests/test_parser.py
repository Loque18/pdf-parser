from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_parse_pdf_files() -> None:
    response = client.post(
        "/parser",
        files=[
            ("files", ("first.pdf", b"%PDF-1.4 first", "application/pdf")),
            ("files", ("second.pdf", b"%PDF-1.4 second", "application/pdf")),
        ],
    )

    assert response.status_code == 200
    assert response.json() == {"message": "ok"}
