import io
import os
import json
import tempfile
import numpy as np
import cv2
import pytest
from PIL import Image
import pytesseract
import openai

import app.ocr as ocr_module
from app.schemas import ReceiptSchema
from app import create_app, db
from app.routes import allowed_file

# Fixtures for Flask app and test client
def pytest_configure():
    # Suppress Flask deprecation warnings
    import warnings
    warnings.filterwarnings('ignore', category=DeprecationWarning)

@pytest.fixture
def app():
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    app = create_app()
    app.config.update({
        'TESTING': True,
        'UPLOAD_FOLDER': tempfile.mkdtemp()
    })
    with app.app_context():
        db.create_all()
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

# OCR module tests
def test_preprocess_image(tmp_path):
    # Create a simple gray image file
    arr = np.full((10, 10), 128, dtype=np.uint8)
    file_path = tmp_path / 'test.png'
    cv2.imwrite(str(file_path), arr)
    processed = ocr_module.preprocess_image(str(file_path))
    assert isinstance(processed, np.ndarray)
    assert processed.dtype == np.uint8


def test_ocr_extract_fallback(monkeypatch):
    # Force preprocess_image to fail to trigger fallback
    monkeypatch.setattr(ocr_module, 'preprocess_image', lambda x: (_ for _ in ()).throw(Exception()))
    dummy_img = Image.new('RGB', (5, 5))
    monkeypatch.setattr(Image, 'open', lambda x: dummy_img)
    monkeypatch.setattr(pytesseract, 'image_to_string', lambda img, lang, config: 'fallback')
    result = ocr_module.ocr_extract('nofile')
    assert result == 'fallback'


def test_ocr_extract_normal(monkeypatch):
    # Normal branch of ocr_extract
    dummy_img = np.zeros((5,5), dtype=np.uint8)
    monkeypatch.setattr(ocr_module, 'preprocess_image', lambda x: dummy_img)
    monkeypatch.setattr(pytesseract, 'image_to_string', lambda img, lang, config: 'normal')
    result = ocr_module.ocr_extract('path')
    assert result == 'normal'

class DummyChoice:
    def __init__(self, content):
        self.message = type('M', (), {'content': content})


def test_parse_receipt_fields_success(monkeypatch):
    sample = json.dumps({'merchant': 'A', 'date': '2025-01-01', 'total': '9.99'})
    monkeypatch.setattr(openai.ChatCompletion, 'create', lambda **kwargs: type('R', (), {'choices': [DummyChoice(sample)]}))
    data = ocr_module.parse_receipt_fields('text')
    assert data == {'merchant': 'A', 'date': '2025-01-01', 'total': '9.99'}


def test_parse_receipt_fields_failure(monkeypatch):
    monkeypatch.setattr(openai.ChatCompletion, 'create', lambda **kwargs: type('R', (), {'choices': [DummyChoice('no json')]}))
    data = ocr_module.parse_receipt_fields('text')
    assert data == {'merchant': None, 'date': None, 'total': None}

# Schema tests
def test_receipt_schema_tag_conversion():
    class Dummy:
        tags = 'a,b'
    schema = ReceiptSchema()
    dumped = schema.dump(Dummy())
    assert dumped['tags'] == ['a', 'b']
    loaded = schema.load({'tags': ['x', 'y']}, partial=True)
    assert getattr(loaded, 'tags') == 'x,y'

# Routes and app tests
def test_allowed_file():
    assert allowed_file('foo.png')
    assert not allowed_file('foo.txt')


def test_upload_receipt_no_file(client):
    resp = client.post('/upload', data={})
    assert resp.status_code == 400
    assert resp.get_json()['error'] == 'No file part'


def test_upload_receipt_empty_filename(client):
    data = {'file': (io.BytesIO(b''), '')}
    resp = client.post('/upload', data=data, content_type='multipart/form-data')
    assert resp.status_code == 400
    assert resp.get_json()['error'] == 'No selected file'


def test_upload_receipt_disallowed_extension(client):
    file_data = (io.BytesIO(b''), 'test.txt')
    resp = client.post('/upload', data={'file': file_data}, content_type='multipart/form-data')
    assert resp.status_code == 400
    assert resp.get_json()['error'] == 'File type not allowed'


def test_list_receipts_empty(client):
    resp = client.get('/receipts')
    json_data = resp.get_json()
    assert resp.status_code == 200
    assert json_data['receipts'] == []
    assert json_data['total'] == 0
    assert json_data['page'] == 1
    assert 'pages' in json_data


def test_upload_and_retrieve_receipt(client, monkeypatch):
    # Stub OCR extraction and parsing
    monkeypatch.setattr(ocr_module, 'ocr_extract', lambda f: '')
    monkeypatch.setattr(ocr_module, 'parse_receipt_fields', lambda t: {'merchant': 'TestShop', 'date': '2025-04-24', 'total': '12.34'})
    # Create a dummy PNG image in memory
    img = Image.new('RGB', (10, 10), color='white')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    data = {
        'file': (buf, 'receipt.png'),
        'notes': 'hello',
        'tags': 'food,drink'
    }
    # Upload
    resp = client.post('/upload', data=data, content_type='multipart/form-data')
    assert resp.status_code == 201
    res_json = resp.get_json()
    rid = res_json['id']
    assert res_json['filename'] == 'receipt.png'
    assert res_json['notes'] == 'hello'
    assert res_json['tags'] == ['food', 'drink']
    # List receipts
    list_resp = client.get('/receipts')
    assert list_resp.status_code == 200
    list_json = list_resp.get_json()
    assert list_json['total'] == 1
    assert list_json['receipts'][0]['id'] == rid
    # Get receipt detail
    detail_resp = client.get(f'/receipts/{rid}')
    assert detail_resp.status_code == 200
    detail_json = detail_resp.get_json()
    assert detail_json['id'] == rid
    assert detail_json['merchant'] == 'TestShop'
    assert detail_json['date'] == '2025-04-24'
    assert detail_json['total'] == 12.34
