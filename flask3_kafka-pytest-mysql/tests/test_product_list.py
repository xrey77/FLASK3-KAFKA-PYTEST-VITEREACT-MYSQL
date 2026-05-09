import pytest # type: ignore
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

def test_product_list_success(mocker, client, mock_producer):

    mock_producer.poll = MagicMock() 
    mock_producer.return_value = mock_producer
    mock_paginated_service = mocker.patch('app.products.productlist.get_paginated_products')
    mock_producer = mocker.patch('app.products.productlist.producer')

    mock_paginated_service.return_value = {
        "page": 1,
        "totpage": 1,
        "totalrecords": 1,
        "products": [{
            "id": 1,
            "descriptions": "PROCASH 100 SERIES",
            "qty": 1,
            "unit": "PCS",
            "costprice": 1000,
            "sellprice": 2000
        }]
    }

    response = client.get('/api/products/list/1')

    assert response.status_code == 200
    mock_producer.produce.assert_called_once()
    mock_producer.produce.assert_called()
    mock_producer.flush.assert_called()

    args, kwargs = mock_producer.produce.call_args
    assert args[0] == 'central-topic'
    assert b'product_list_viewed' in kwargs['value']
    
    mock_producer.flush.assert_called_once()


def test_product_list_not_found(mocker, client, mock_producer):
    mock_producer.poll = MagicMock() 
    mock_producer.return_value = mock_producer
    mock_paginated_service = mocker.patch('app.products.productlist.get_paginated_products')
    mock_producer = mocker.patch('app.products.productlist.producer')

    mock_paginated_service.return_value = None
    response = client.get('/api/products/list/99')

    assert response.status_code == 404
    assert response.json['message'] == 'No record(s) found.'

    mock_producer.produce.assert_not_called()
