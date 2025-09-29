from fastapi.testclient import TestClient
import app as appmod

client = TestClient(appmod.app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("ok") is True

def test_export_json():
    r = client.get("/api/export/products.json")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
