import os
import jwt
import boto3


class AwsTools:

    def __init__(self):
        self.client_id = os.getenv('CLIENT_ID')
        self.secret_hash = os.getenv('SECRET_HASH')
        self.client_cognito = boto3.client(
            'cognito-idp', region_name='us-east-1'
        )

    def extract_token_info(self, event):

        token = event['headers'].get('Authorization', '')

        response = jwt.decode(
            token,
            algorithms=["RS256"],
            options={"verify_signature": False}
        )

        return response
