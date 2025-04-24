import io
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

def test_upload_list_detail(client):
    # Upload a receipt with notes and tags
    data = {
        'file': (io.BytesIO(b'fake image bytes'), 'receipt1.png'),
        'notes': 'taxi ride',
        'tags': 'transport,urgent'
    }
    resp = client.post('/upload', data=data, content_type='multipart/form-data')
    assert resp.status_code == 201
    receipt = resp.get_json()
    assert receipt['notes'] == 'taxi ride'
    assert set(receipt['tags']) == {'transport', 'urgent'}
    rid = receipt['id']

    # List receipts with pagination
    resp = client.get('/receipts?page=1&per_page=1')
    assert resp.status_code == 200
    page = resp.get_json()
    assert page['total'] >= 1
    assert page['page'] == 1
    assert page['per_page'] == 1
    assert any(r['id'] == rid for r in page['receipts'])

    # Get detail
    resp = client.get(f'/receipts/{rid}')
    assert resp.status_code == 200
    detail = resp.get_json()
    assert detail['id'] == rid
    assert detail['notes'] == 'taxi ride'
    assert set(detail['tags']) == {'transport', 'urgent'}
