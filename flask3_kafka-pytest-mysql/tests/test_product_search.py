import pytest
import json
from unittest.mock import MagicMock, patch
from config import create_app

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mock_get_products(mocker):
    return mocker.patch('app.products.search.get_product_search_results')

@pytest.fixture
def mock_producer(mocker):
    return mocker.patch('app.products.search.producer')

def test_product_search_success(client, mock_get_products, mock_producer):

    mock_products = {"products": ["item1", "item2"], "total": 2}
    mock_get_products.return_value = mock_products
    
    response = client.get('/api/products/search/1/testkeyword')
    
    assert response.status_code == 200
    assert response.json == mock_products
    
    mock_producer.produce.assert_called_once()
    
    args, kwargs = mock_producer.produce.call_args
    topic = args[0]
    payload = json.loads(kwargs['value'].decode('utf-8'))
    
    assert topic == 'central-topic'
    assert payload['event'] == 'product_search_viewed'
    assert payload['page'] == 1
    assert payload['count'] == 2
    mock_producer.flush.assert_called_once()

def test_product_search_no_results(client, mock_get_products, mock_producer):
    mock_get_products.return_value = {"products": []}
    
    response = client.get('/api/products/search/1/empty')
    
    assert response.status_code == 404
    assert response.json['message'] == 'No record(s) found.'
    
    mock_producer.produce.assert_not_called()
