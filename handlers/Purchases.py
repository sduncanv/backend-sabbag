from classes.Purchases import Purchases
from tools.FunctionsTools import exception_decorator, validate_permissions

ADMIN = 1
CUSTOMER = 2


@validate_permissions({
    'POST': [CUSTOMER],
    'GET': [ADMIN, CUSTOMER]
})
@exception_decorator
def purchases(event, context):

    method = event['httpMethod']
    purchases_class = Purchases()

    functions = {
        "POST": purchases_class.create_purchase,
        "GET": purchases_class.get_purchase
    }

    return functions[method](event)
