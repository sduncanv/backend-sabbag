from classes.Products import Products
from tools.FunctionsTools import exception_decorator, validate_permissions

ADMIN = 1
CUSTOMER = 2


@validate_permissions({
    'POST': [ADMIN],
    'GET': [ADMIN, CUSTOMER],
    'PUT': [ADMIN],
    'DELETE': [ADMIN],
})
@exception_decorator
def products(event, context):

    method = event['httpMethod']
    products_class = Products()

    functions = {
        "POST": products_class.create_product,
        "GET": products_class.get_product,
        "PUT": products_class.update_product,
        "DELETE": products_class.delete_product
    }

    return functions[method](event)
