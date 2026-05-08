import pytest # type: ignore
import io
import json
from unittest.mock import MagicMock
from werkzeug.datastructures import FileStorage # type: ignore
from config import create_app 

@pytest.fixture
def app():
    app = create_app() # Your factory
    app.config.update({
        "TESTING": True,
        "JWT_SECRET_KEY": "super-secret-test-key"
    })
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def mock_producer(mocker):
    return mocker.patch('app.users.uploadpic.producer')

@pytest.fixture
def mock_update_service(mocker):
    return mocker.patch('app.users.uploadpic.update_profile_picture')

# 3. Create a valid JWT token fixture
@pytest.fixture
def auth_header(app):
    from flask_jwt_extended import create_access_token # type: ignore
    with app.app_context():
        token = create_access_token(identity="123")
        return {"Authorization": f"Bearer {token}"}

def test_profile_picture_upload_success(client, mock_producer, mock_update_service, auth_header):
    user_id = 1
    # Mock successful service response
    mock_update_service.return_value = ({"message": "Profile updated"}, 200)
    
    # Mock a file
    mock_file = FileStorage(
        stream=io.BytesIO(b"dummy image data"),
        filename="test.jpg",
        content_type="image/jpeg",
    )
    data = {"userpic": mock_file}
    
    # --- WHEN ---
    response = client.patch(
        f"/api/uploadpicture/{user_id}",
        data=data,
        headers=auth_header,
        content_type="multipart/form-data"
    )
    
    assert response.status_code == 200
    assert response.json["message"] == "Profile updated"
    
    # Verify Kafka producer called
    mock_producer.produce.assert_called_once()
    args, kwargs = mock_producer.produce.call_args
    assert args[0] == 'central-topic'
    assert b'user_upload_picture' in kwargs['value']
        
    # Verify flush
    mock_producer.flush.assert_called_once()

def test_profile_picture_no_file(client, auth_header):
    response = client.patch(
        "/api/uploadpicture/1",
        headers=auth_header,
        content_type="multipart/form-data"
    )
    
    assert response.status_code == 400
    assert response.json["message"] == "No Image found."
