import json
import pytest # type: ignore
from unittest.mock import MagicMock, patch
from flask_jwt_extended import create_access_token # type: ignore
from config import create_app
from config.extensions import db

@pytest.fixture
def app():
    app = create_app({'TESTING': True})
    
    with app.app_context():
        yield app

@pytest.fixture
def client():
    app = create_app()
    app.config['JWT_SECRET_KEY'] = 'test-secret'
    app.config['TESTING'] = True
    
    # Initialize DB for tests
    with app.app_context():
        from config.extensions import db
        yield app.test_client()
        

@pytest.fixture
def auth_header(client):
    token = create_access_token(identity="admin")
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def db(app): 
    from config.extensions import db as _db
    yield _db

@patch('app.users.delete.producer') 
def test_delete_user_success(mock_producer, client, auth_header, db):
    from app.models.user import Users 
    from config.extensions import db

    # user = Users(username="testuser")
    user = Users(
        username='testuser',
        firstname='John',
        lastname='Doe',
        email='john@example.com',
        mobile='1234567890',
        password='hashedpassword',
        role_id=1,
        department_id=1
        # Ensure all NOT NULL fields are present
    )

    db.session.add(user)
    db.session.commit()
    user_id = user.id

    response = client.delete(
        f'/api/deleteuser/{user_id}',
        headers=auth_header
    )

    assert response.status_code == 200
    assert response.json['message'] == f'User ID {user_id} has been deleted.'

    mock_producer.produce.assert_called_once()
    args, kwargs = mock_producer.produce.call_args
    assert args[0] == 'central-topic'
    assert b'user_delete' in kwargs['value']
    
    mock_producer.flush.assert_called_once()


@patch('app.users.delete.producer')
def test_delete_user_not_found(mock_producer, client, auth_header):        
    response = client.delete(f'/api/deleteuser/99', headers=auth_header)
    json_data = response.get_json()
    assert json_data is not None, "Response body was not JSON or was empty"
    assert json_data['message'] == "User ID not found."
    
    mock_producer.produce.assert_not_called()