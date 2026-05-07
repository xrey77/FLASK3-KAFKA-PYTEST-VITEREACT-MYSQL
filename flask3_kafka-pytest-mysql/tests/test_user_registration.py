import pytest # type: ignore
import json
from unittest.mock import patch, MagicMock
from config import create_app 

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@patch('app.auth.register.register_user')
@patch('app.auth.register.producer')
def test_user_register_success(mock_producer, mock_register_user, client):

    mock_user = MagicMock()
    mock_user.id = 28
    mock_user.email = "nelson@yahoo.com"    
    mock_register_user.return_value = mock_user
    
    # Payload
    payload = {
        "firstname": "Nelson",
        "lastname": "Zamora",
        "email": "nelson@yahoo.com", 
        "mobile": "23423423",
        "username": "Nelson",
        "password": "rey"}
    
    # Request
    response = client.post(
        '/auth/signup',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == 201
    assert response.get_json()['message'] == "You have registered successfully, please sign-in now."    
    
    assert mock_producer.produce.called
    mock_register_user.assert_called_once_with(payload)



@patch('app.services.auth_service.register_user') 
def test_user_register_failure(mock_register_user, client):
    # Mock error
    mock_register_user.side_effect = ValueError("User already exists")
    
    payload = {
        "firstname": "Soji",
        "lastname": "Gragasin",
        "email": "soji@yahoo.com", 
        "mobile": "23423423",
        "username": "Soji",
        "password": "rey"}
    
    response = client.post(
        '/auth/signup',
        data=json.dumps(payload),
        content_type='application/json'
    )
    
    # Assertions
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['message'] == "Email Address is already taken."
