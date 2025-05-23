import json
from unittest.mock import patch, MagicMock
from handlers.Users import login  # ajustá si está en otro lugar


@patch("tools.Database")
@patch("tools.AwsTools.boto3.client")
@patch("handlers.Users.Users")
def test_login(mock_users_class, mock_boto_client, mock_db_class):

    mock_users_instance = MagicMock()
    mock_users_class.return_value = mock_users_instance

    mock_users_instance.db.run_select.return_value = [1]

    mock_users_instance.client_id = 'client-id-test'
    mock_users_instance.secret_hash = 'secret-hash-test'
    mock_users_instance.get_secret_hash.return_value = 'mocked-secret-hash'

    mock_users_instance.client_cognito.initiate_auth.return_value = {
        'data': {
            "AccessToken": "eyJraWQiOiJr...",
            "ExpiresIn": 3600,
            "TokenType": "Bearer",
            "RefreshToken": "eyJjdHkiOiJKV...",
            "IdToken": "eyJraWQiOiJr..."
        }
    }
    
    mock_users_instance.login.return_value = {
        "statusCode": 200,
        'data': {
            "AccessToken": "eyJraWQiOiJr...",
            "ExpiresIn": 3600,
            "TokenType": "Bearer",
            "RefreshToken": "eyJjdHkiOiJKV...",
            "IdToken": "eyJraWQiOiJr..."
        }
    }

    # Event simulado (ajustá si usás otra estructura)
    event = {
        "httpMethod": "POST",
        "body": json.dumps({
            "username": "test_user",
            "password": "test_pass"
        })
    }

    # Ejecutar
    response = login(event, None)
    print("RESPONSE:", response)

    # Validaciones
    assert response["statusCode"] == 200
    # assert response["body"] == {
    #     "AccessToken": "eyJraWQiOiJr...",
    #     "ExpiresIn": 3600,
    #     "TokenType": "Bearer",
    #     "RefreshToken": "eyJjdHkiOiJKV...",
    #     "IdToken": "eyJraWQiOiJr..."
    # }

    assert json.loads(response["body"]) == {
        "statusCode": 200,
        'data': {
            "AccessToken": "eyJraWQiOiJr...",
            "ExpiresIn": 3600,
            "TokenType": "Bearer",
            "RefreshToken": "eyJjdHkiOiJKV...",
            "IdToken": "eyJraWQiOiJr..."
        }
    }
