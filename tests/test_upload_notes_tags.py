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

def test_upload_with_notes_and_tags(client):
    data = {
        'file': (io.BytesIO(b'fake image bytes'), 'test_receipt.png'),
        'notes': 'Business dinner',
        'tags': 'food, client, urgent'
    }
    resp = client.post('/upload', data=data, content_type='multipart/form-data')
    assert resp.status_code == 201
    json_data = resp.get_json()
    assert json_data['notes'] == 'Business dinner'
    assert set(json_data['tags']) == {'food', 'client', 'urgent'}
    # List receipts and check tags/notes
    resp = client.get('/receipts')
    assert resp.status_code == 200
    receipts = resp.get_json()['receipts']
    found = [r for r in receipts if r['filename'] == 'test_receipt.png']
    assert found
    assert found[0]['notes'] == 'Business dinner'
    assert set(found[0]['tags']) == {'food', 'client', 'urgent'}
