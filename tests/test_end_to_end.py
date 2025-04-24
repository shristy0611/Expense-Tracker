import io
import os
import tempfile
import pytest
from app import create_app, db
from app.models import Receipt

@pytest.fixture
def client():
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client


def test_upload_and_list_receipt(client):
    # Simulate uploading a fake image file (as bytes)
    from PIL import Image
    def make_valid_png_bytes():
        buf = io.BytesIO()
        img = Image.new("RGB", (10, 10), color="white")
        img.save(buf, format="PNG")
        buf.seek(0)
        return buf
    data = {
        'file': (make_valid_png_bytes(), 'test_receipt.png')
    }
    resp = client.post('/upload', data=data, content_type='multipart/form-data')
    assert resp.status_code == 201
    json_data = resp.get_json()
    assert 'filename' in json_data
    # List receipts
    resp = client.get('/receipts')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, dict)
    assert 'receipts' in data
    assert isinstance(data['receipts'], list)
    assert any(r['filename'] == 'test_receipt.png' for r in data['receipts'])
