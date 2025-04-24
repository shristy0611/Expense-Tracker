import io
import time
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


def test_upload_performance(client):
    start = time.time()
    for i in range(50):
        data = {
            'file': (io.BytesIO(b'fake image bytes'), f'test_{i}.png'),
            'notes': 'performance test',
            'tags': 'benchmark'
        }
        resp = client.post('/upload', data=data, content_type='multipart/form-data')
        assert resp.status_code == 201
    elapsed = time.time() - start
    assert elapsed < 60, f"Upload throughput too slow: {50/elapsed:.2f} req/sec"


def test_list_performance(client):
    # Seed DB with 50 receipts
    with client.application.app_context():
        for i in range(50):
            r = Receipt(filename=f'f{i}.png')
            db.session.add(r)
        db.session.commit()
    start = time.time()
    for _ in range(50):
        resp = client.get('/receipts?page=1&per_page=50')
        assert resp.status_code == 200
        json_data = resp.get_json()
        assert json_data['total'] >= 50, f"Expected at least 50 receipts, got {json_data['total']}"
    elapsed = time.time() - start
    assert elapsed < 60, f"List throughput too slow: {50/elapsed:.2f} req/sec"
