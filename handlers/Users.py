from classes.Users import Users
from tools.FunctionsTools import exception_decorator, validate_permissions

ADMIN = 1


@exception_decorator
def users(event, context):

    method = event['httpMethod']
    users_class = Users()

    functions = {
        "POST": users_class.create_user
    }

    return functions[method](event)


@exception_decorator
def auth_user(event, context):

    method = event['httpMethod']
    users_class = Users()

    functions = {
        "POST": users_class.authenticate_user
    }

    return functions[method](event)


@exception_decorator
def reauthenticate(event, context):

    method = event['httpMethod']
    users_class = Users()

    functions = {
        "POST": users_class.reauthenticate_user
    }

    return functions[method](event)


@exception_decorator
def login(event, context):

    method = event['httpMethod']
    users_class = Users()

    functions = {
        "POST": users_class.login
    }

    return functions[method](event)


@validate_permissions({'POST': [ADMIN]})
@exception_decorator
def create_admin(event, context):

    method = event['httpMethod']
    users_class = Users()

    functions = {
        "POST": users_class.create_admin
    }

    return functions[method](event)
