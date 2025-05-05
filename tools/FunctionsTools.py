import os
import jwt
import sys
import json
import traceback
from botocore.exceptions import ClientError
from sqlalchemy.exc import OperationalError
from sqlalchemy import select

from models.UsersRoles import UsersRolesModel
from models.Users import UsersModel
from tools.Database import Database


def get_event_data(event: dict) -> dict:

    method = event.get('httpMethod', 'GET')

    methods = {
        'POST': convert_to_dict(event.get('body')) or {},
        'GET': convert_to_dict(event.get('queryStringParameters')) or {},
        'PUT': convert_to_dict(event.get('body')) or {},
        'DELETE': convert_to_dict(event.get('queryStringParameters')) or {}
    }

    return methods[method]


def convert_to_dict(value):

    if isinstance(value, dict):
        return value

    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return {}


def validate_event_data(event_data: list[list]) -> dict:

    errors = []

    for field in event_data:

        name = field[0]
        _type = field[1]
        value = field[2]

        if isinstance(value, str) and not value.strip():
            errors.append(f"{name} can't be empty.")

        if _type == int:
            try:
                value = int(value)
            except ValueError:
                errors.append(f"Type of {name} is invalid. Expected int.")

        if not isinstance(value, _type):
            errors.append(
                f"Type of {name} is invalid. Expected {_type.__name__}."
            )

    return {
        'is_valid': not errors, 'errors': errors
    }


class CustomError(Exception):

    def __init__(self, message: str, status_code: int):

        self.message: str = message
        self.status_code = status_code

        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message


def exception_decorator(function):

    def validations(*args, **kwargs):

        result = []
        statusCode = 200
        message = ''

        try:
            result = function(*args, **kwargs)

        except CustomError as e:

            print(e)
            read_exception_message()

            statusCode = e.status_code
            message = str(e)

        except OperationalError as e:

            print(e)
            read_exception_message()

            statusCode = 400
            print(e.args[0])
            message = str(e)

        except ClientError as e:

            print(e)
            read_exception_message()

            statusCode = 400
            message = e.args[0]

            if 'Error' in e.response and 'Message' in e.response['Error']:
                message = e.response['Error']['Message']

        except Exception as e:

            print(e)
            read_exception_message()

            statusCode = 500
            message = 'Internal server error'

        return response(statusCode, result, message)

    return validations


def response(statusCode, data=[], message=''):

    body = {'statusCode': statusCode}

    if data:
        body['statusCode'] = data['statusCode']
        body['data'] = data['data']

    if message:
        body['message'] = message

    return {
        'statusCode': statusCode,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
            'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept'
        },
        'body': json.dumps(body)
    }


def read_exception_message():

    type, object, stack = sys.exc_info()

    last_trace = traceback.extract_tb(stack)[-1]
    filename, line, function, code = last_trace

    path = filename.split("\\")[-2::]

    print(f'''
        line: {line},
        function: {function},
        code: {code},
        path: {path}
    ''')


def validate_permissions(roles: list):

    def validations(function):
        def wrapper(event, context):

            token = event['headers'].get('Authorization', '')[7:]

            decoded_token = jwt.decode(
                token,
                algorithms=["RS256"],
                options={"verify_signature": False}
            )

            username = decoded_token.get('cognito:username', '')

            database = Database(
                db=os.getenv('DATABASE_NAME'),
                host=os.getenv('DATABASE_HOST'),
                user=os.getenv('DATABASE_USER'),
                password=os.getenv('DATABASE_PASSWORD'),
                port=os.getenv('DATABASE_PORT')
            )

            statement = select(
                UsersModel.user_id,
                UsersRolesModel
            ).join(
                UsersModel,
                UsersRolesModel.user_id == UsersModel.user_id
            ).where(
                UsersRolesModel.active == 1,
                UsersModel.active == 1,
                UsersModel.username == username
            )

            result = database.run_statement(statement, 2)

            user_role = result[0]['role_id']

            if not result:
                return response(
                    statusCode=403,
                    message='User does not have permission.'
                )

            if user_role not in roles.get(event['httpMethod'], []):
                return response(
                    statusCode=403,
                    message='User does not have permission.'
                )

            return function(event, context)

        return wrapper

    return validations
