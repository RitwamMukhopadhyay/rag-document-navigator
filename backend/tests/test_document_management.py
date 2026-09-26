import io
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal, Base, engine
from app.rag.vector_store import global_vector_store
from app.rag.ingestion_service import IngestionService

client = TestClient(app)

def test_document_upload_and_duplicate_detection():
    # Generate dummy PDF content bytes
    dummy_pdf_content = b"%PDF-1.4 %ABCDEF1234567890 Document Test Content Page 1 sample text for indexing"
    
    # 1. First Upload
    files = [("files", ("Test_Document_Alpha.pdf", io.BytesIO(dummy_pdf_content), "application/pdf"))]
    response = client.post("/api/documents/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["documents_processed"] == 1
    assert data["duplicates_skipped"] == 0
    assert len(data["results"]) == 1
    res1 = data["results"][0]
    assert res1["status"] == "success"
    assert res1["filename"] == "Test_Document_Alpha.pdf"
    doc_id = res1["document_id"]

    # 2. Duplicate Upload (Same file content & name)
    files_dup = [("files", ("Test_Document_Alpha.pdf", io.BytesIO(dummy_pdf_content), "application/pdf"))]
    response_dup = client.post("/api/documents/upload", files=files_dup)
    assert response_dup.status_code == 200
    data_dup = response_dup.json()
    assert data_dup["duplicates_skipped"] == 1
    assert data_dup["results"][0]["status"] == "duplicate"
    assert "already exists" in data_dup["results"][0]["message"]

    # 3. Document Library Listing
    list_res = client.get("/api/documents")
    assert list_res.status_code == 200
    doc_list = list_res.json()
    filenames = [d["filename"] for d in doc_list]
    assert "Test_Document_Alpha.pdf" in filenames

    # 4. Document Deletion
    del_res = client.delete(f"/api/documents/{doc_id}")
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True

    # 5. Verify file removed from library
    list_res_after = client.get("/api/documents")
    filenames_after = [d["filename"] for d in list_res_after.json()]
    assert "Test_Document_Alpha.pdf" not in filenames_after

def test_incremental_indexing_and_cross_doc_retrieval():
    pdf1 = b"%PDF-1.4 Annual shipping policy timeline and standard return guidelines."
    pdf2 = b"%PDF-1.4 Clinical drug trial results and efficacy benchmark measurements."

    client.post("/api/documents/upload", files=[("files", ("Annual_Policy_2026.pdf", io.BytesIO(pdf1), "application/pdf"))])
    client.post("/api/documents/upload", files=[("files", ("Clinical_Trial_2026.pdf", io.BytesIO(pdf2), "application/pdf"))])

    # Retrieve query
    ret_res = client.post("/api/retrieve", json={"question": "clinical trial shipping policy", "top_k": 5})
    assert ret_res.status_code == 200
    ret_data = ret_res.json()
    assert ret_data["total_retrieved"] > 0
    retrieved_files = [c["filename"] for c in ret_data["retrieved_chunks"]]
    
    # Both documents should be searchable
    assert any("Annual_Policy_2026.pdf" in f or "Clinical_Trial_2026.pdf" in f for f in retrieved_files)

    # Cleanup
    docs = client.get("/api/documents").json()
    for d in docs:
        if d["filename"] in ["Annual_Policy_2026.pdf", "Clinical_Trial_2026.pdf"]:
            client.delete(f"/api/documents/{d['id']}")
