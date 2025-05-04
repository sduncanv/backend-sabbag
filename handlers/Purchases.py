from classes.Purchases import Purchases
from tools.FunctionsTools import exception_decorator


@exception_decorator
def purchases(event, context):

    method = event['httpMethod']
    purchases_class = Purchases()

    functions = {
        "POST": purchases_class.create_purchase,
        "GET": purchases_class.get_purchase
    }

    return functions[method](event)
