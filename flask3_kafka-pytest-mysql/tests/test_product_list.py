import pytest # type: ignore
import json
from unittest.mock import MagicMock, patch
from flask import Flask # type: ignore
# Import the blueprint from your source file
# from app.products.productlist import api_prodlist

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    # REGISTER THE BLUEPRINT HERE
    # app.register_blueprint(api_prodlist)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mock_get_products():
    with patch('app.products.productlist.get_paginated_products') as mock:
        yield mock

# Correctly patch the producer within productlist.py
# @pytest.fixture
# def mock_producer():
#     with patch('app.products.productlist.producer') as mock:
#         yield mock

def test_product_list_success(mocker, client, mock_producer, mock_get_products):

    mock_producer.poll = MagicMock() 
    mock_producer.return_value = mock_producer

    mock_producer = mocker.patch('app.products.productlist.producer')

    # 1. Setup mock data
    mock_items = [{"id": 1, "name": "prod1"}, {"id": 2, "name": "prod2"}]
    # Simulate pagination data structure if necessary
    mock_get_products.return_value = MagicMock(items=lambda: mock_items)
    
    # 2. Call the endpoint using url_prefix + route
    response = client.get('/api/products/list/1')
    
    # 3. Assertions
    assert response.status_code == 200
    assert len(response.json) == 2
    
    # 4. Verify Kafka producer was called
    mock_producer.produce.assert_called_once()
    assert "product_list_viewed" in mock_producer.produce.call_args[0][1]


# def test_product_list_not_found(client, mock_producer, mock_get_products):
#     mock_get_products.return_value = None

#     response = client.get('/api/products/list/99')
    
#     assert response.status_code == 404
#     assert response.json['message'] == 'No record(s) found.'

#     mock_producer.produce.assert_not_called()
