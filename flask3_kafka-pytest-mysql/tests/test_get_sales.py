import json
import pytest
from unittest.mock import MagicMock
from config import create_app 

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    return app    

@pytest.fixture
def client(app):
    return app.test_client()

def test_get_sales_success(mocker, client):
    mock_sales_service = mocker.patch('app.products.sales.get_all_sales_service')
    mock_sales_service.return_value = [{"id": 1, "product": "Item A", "price": 100}]

    mock_producer = mocker.patch('app.products.sales.producer')
    
    response = client.get('/api/getsales')
    
    assert response.status_code == 200
    assert response.json['sales'][0]['product'] == "Item A"
    
    mock_producer.produce.assert_called_once()
    
    args, kwargs = mock_producer.produce.call_args
    assert 'central-topic' in args
    assert 'event' in json.loads(kwargs['value'].decode('utf-8'))

def test_get_sales_no_records(client, mocker):
    mock_sales_service = mocker.patch('app.products.sales.get_all_sales_service')
    mock_sales_service.return_value = None

    # mock_producer = mocker.patch('app.products.sales.producer')

    response = client.get('/api/getsales')
    print(response.status_code)
    assert response.status_code == 404
    assert "No record(s) found." in response.get_data(as_text=True)
    # mock_producer.produce.assert_called_once()

    