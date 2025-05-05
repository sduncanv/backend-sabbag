import os
import hmac
import boto3
import base64
import hashlib
from sqlalchemy import insert, update, select, or_

from models.Users import UsersModel
from models.UsersRoles import UsersRolesModel
from tools.Database import Database
from tools.FunctionsTools import (
    get_event_data, validate_event_data, CustomError
)


class Users:

    def __init__(self) -> None:

        self.client_id = os.getenv('CLIENT_ID')
        self.secret_hash = os.getenv('SECRET_HASH')
        self.db = Database(
            db=os.getenv('DATABASE_NAME'),
            host=os.getenv('DATABASE_HOST'),
            user=os.getenv('DATABASE_USER'),
            password=os.getenv('DATABASE_PASSWORD'),
            port=os.getenv('DATABASE_PORT')
        )
        self.client_cognito = boto3.client(
            'cognito-idp', region_name='us-east-1'
        )

    def create_user(self, event) -> dict:

        input_data = get_event_data(event)

        username = input_data.get('username', '')
        email = input_data.get('email', '')
        password = input_data.get('password', '')

        values = [
            ['username', str, username],
            ['password', str, password],
            ['email', str, email]
        ]

        is_valid = validate_event_data(values)

        if not is_valid['is_valid']:
            raise CustomError(
                is_valid['errors'][0], 400
            )

        statement = select(UsersModel).where(
            UsersModel.active == 1, or_(
                UsersModel.username == username,
                UsersModel.email == email
            )
        )

        user_exists = self.db.run_statement(statement, 2)
        if user_exists:
            raise CustomError('Username or email already exists.', 400)

        result = self.client_cognito.sign_up(
            ClientId=self.client_id,
            SecretHash=self.get_secret_hash(
                username, self.client_id, self.secret_hash
            ),
            Username=username,
            Password=password,
            UserAttributes=[
                {'Name': 'email', 'Value': email},
                {'Name': 'custom:role', 'Value': str(2)}
            ]
        )

        status_code = result['ResponseMetadata']['HTTPStatusCode']
        data = result

        if status_code == 200:

            password = hashlib.sha256(bytes(str(password), "utf-8")).hexdigest()

            statement = insert(UsersModel).values(
                username=username,
                email=email,
                password=password
            )

            result_statement = self.db.run_statement(statement, 1)

            CUSTOMER_ROLE_ID = 2
            self.db.run_statement(
                insert(UsersRolesModel).values(
                    user_id=result_statement['user_id'],
                    role_id=CUSTOMER_ROLE_ID
                ), 1
            )

            result_statement.update({"message": "User was created."})
            data = result_statement
            status_code = 201

        return {'statusCode': status_code, 'data': data}

    def get_secret_hash(self, username, client_id, client_secret) -> str:

        message = username + client_id
        dig = hmac.new(
            client_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()

        return base64.b64encode(dig).decode()

    def authenticate_user(self, event) -> dict:

        data = get_event_data(event)

        username = data.get('username', '')
        code = data.get('code', '')

        values = [
            ['username', str, username],
            ['code', str, code]
        ]

        is_valid = validate_event_data(values)
        if not is_valid['is_valid']:
            raise CustomError(is_valid['errors'][0], 400)

        result = self.client_cognito.confirm_sign_up(
            ClientId=self.client_id,
            SecretHash=self.get_secret_hash(
                username, self.client_id, self.secret_hash
            ),
            Username=username,
            ConfirmationCode=code
        )

        status_code = result['ResponseMetadata']['HTTPStatusCode']
        data = result
        message = 'User not authenticated.'

        if status_code == 200:

            statement = update(UsersModel).where(
                UsersModel.username == username
            ).values(
                is_authenticated=1
            )

            data = self.db.run_statement(statement, 3)
            message = 'User authenticated.'

        return {
            'statusCode': status_code,
            'data': data,
            'message': message
        }

    def reauthenticate_user(self, event) -> dict:

        data = get_event_data(event)
        username = data.get('username', '')

        values = [['username', str, username],]

        is_valid = validate_event_data(values)
        if not is_valid['is_valid']:
            raise CustomError(is_valid['errors'][0], 400)

        result = self.client_cognito.resend_confirmation_code(
            ClientId=self.client_id,
            SecretHash=self.get_secret_hash(
                username, self.client_id, self.secret_hash
            ),
            Username=username
        )

        status_code = result['ResponseMetadata']['HTTPStatusCode']
        data = result
        message = 'Code not sent.'

        if status_code == 200:
            message = 'Code sent.'

        return {
            'statusCode': status_code,
            'data': data,
            'message': message
        }

    def login(self, event):

        data = get_event_data(event)

        username = data.get('username', '')
        password = data.get('password', '')

        values = [
            ['username', str, username],
            ['password', str, password]
        ]

        is_valid = validate_event_data(values)
        if not is_valid['is_valid']:
            raise CustomError(is_valid['errors'][0], 400)

        statement = select(UsersModel).where(
            UsersModel.active == 1,
            UsersModel.username == username
        )

        user_exists = self.db.run_statement(statement, 2)
        if not user_exists:
            raise CustomError("Username does'n exists.", 400)

        response = self.client_cognito.initiate_auth(
            AuthFlow='USER_PASSWORD_AUTH',
            ClientId=self.client_id,
            AuthParameters={
                'SECRET_HASH': self.get_secret_hash(
                    username, self.client_id, self.secret_hash
                ),
                'USERNAME': username,
                'PASSWORD': password
            }
        )

        status_code = response['ResponseMetadata']['HTTPStatusCode']
        data = response.get('AuthenticationResult', {})

        if status_code == 400:
            raise CustomError(
                message=data, status_code=status_code
            )

        return {'statusCode': status_code, 'data': data}

    def create_admin(self, event):

        data = get_event_data(event)
        user_id = data.get('user_id', '')

        values = [
            ['user_id', int, user_id]
        ]

        is_valid = validate_event_data(values)
        if not is_valid['is_valid']:
            raise CustomError(is_valid['errors'][0], 400)

        username = self.db.run_statement(
            select(UsersModel).where(
                UsersModel.active == 1,
                UsersModel.user_id == user_id,
            ), 2
        )

        if not username:
            raise CustomError("User does'n exists.", 400)

        ADMIN_ROLE_ID = 1
        statement = update(UsersRolesModel).where(
            UsersRolesModel.user_id == user_id,
            UsersRolesModel.active == 1
        ).values(
            role_id=ADMIN_ROLE_ID
        )

        result = self.client_cognito.admin_update_user_attributes(
            UserPoolId=os.getenv('USER_POOL_ID'),
            Username=username[0]['username'],
            UserAttributes=[
                {'Name': 'custom:role', 'Value': str(1)}
            ]
        )

        status_code = result['ResponseMetadata']['HTTPStatusCode']
        data = result

        if status_code == 200:
            self.db.run_statement(statement, 3)
            data = {"message": "Admin was created."}

        return {'statusCode': status_code, 'data': data}
