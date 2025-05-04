import os
from sqlalchemy import select, insert, update

from models.ProductsModel import ProductModel
from tools.Database import Database
from tools.FunctionsTools import (
    get_event_data, validate_event_data, CustomError
)


class Products:

    def __init__(self) -> None:
        self.db = Database(
            db=os.getenv('DATABASE_NAME'),
            host=os.getenv('DATABASE_HOST'),
            user=os.getenv('DATABASE_USER'),
            password=os.getenv('DATABASE_PASSWORD'),
            port=os.getenv('DATABASE_PORT')
        )

    def create_product(self, event: dict):

        input_data = get_event_data(event)

        name = input_data.get('name', '')
        price = input_data.get('price', '')
        category = input_data.get('category', '')
        quantity = input_data.get('quantity', '')

        data = [
            ['name', str, name],
            ['price', float, price],
            ['category', str, category],
            ['quantity', int, quantity],
        ]

        is_valid = validate_event_data(data)

        if not is_valid['is_valid']:
            raise CustomError(is_valid['errors'][0], 400)

        statement = insert(ProductModel).values(
            name=name,
            price=price,
            category=category,
            quantity=quantity
        )

        result_statement = self.db.run_statement(statement, 1)

        return {'statusCode': 201, 'data': result_statement}

    def get_product(self, event: dict):

        input_data = get_event_data(event)
        conditions = [ProductModel.active == 1]

        product_id = input_data.get('product_id', '')
        category = input_data.get('category', '')

        if product_id:
            conditions.append(ProductModel.product_id == product_id)

        if category:

            is_valid = validate_event_data([['category', str, category]])
            if not is_valid['is_valid']:
                raise CustomError(is_valid['errors'][0], 400)

            conditions.append(ProductModel.category == category)

        statement = select(ProductModel).where(*conditions)

        limit = input_data.get('limit')
        offset = input_data.get('offset')

        if limit:

            is_valid = validate_event_data([['limit', int, limit]])
            if not is_valid['is_valid']:
                raise CustomError(is_valid['errors'][0], 400)

            statement = statement.limit(limit)

        if offset:

            is_valid = validate_event_data([['offset', int, offset]])
            if not is_valid['is_valid']:
                raise CustomError(is_valid['errors'][0], 400)

            statement = statement.offset(offset)

        result_statement = self.db.run_statement(statement, 2)

        status_code = 200

        if not result_statement:
            status_code = 404
            result_statement = []

        return {'statusCode': status_code, 'data': result_statement}

    def update_product(self, event):

        input_data = get_event_data(event)
        product_id = input_data.get('product_id', '')

        is_valid = validate_event_data([['product_id', int, product_id]])

        if not is_valid['is_valid']:
            raise CustomError(is_valid['errors'][0], 400)

        if product_id:

            product_found = self.get_product(
                {'queryStringParameters': {'product_id': product_id}}
            )

            if product_found['statusCode'] != 200:
                raise CustomError("Product doesn't exist.", 404)

        column_names = [column.name for column in ProductModel.__table__.columns]
        to_update = {}

        for key, val in input_data.items():
            if key in column_names and key not in ['product_id', 'active', 'in_stock']:
                to_update[key] = val

        statement = update(ProductModel).where(
            ProductModel.product_id == product_id,
            ProductModel.active == 1
        ).values(**to_update)

        result_statement = self.db.run_statement(statement, 3)

        if result_statement:
            status_code = 200
            data = 'The product was updated.'

        else:
            status_code = 400
            data = "The product wasn't updated."

        return {'statusCode': status_code, 'data': data}

    def delete_product(self, event):

        input_data = get_event_data(event)

        product_id = input_data.get('product_id', '')
        conditions = [ProductModel.active == 1]

        is_valid = validate_event_data([['product_id', str, product_id]])

        if not is_valid['is_valid']:
            raise CustomError(is_valid['errors'][0], 400)

        if product_id:

            conditions.append(ProductModel.product_id == product_id)

            product_found = self.get_product(
                {'queryStringParameters': {'product_id': product_id}}
            )

            if product_found['statusCode'] != 200:
                raise CustomError("Product doesn't exist.", 404)

        statement = update(ProductModel).where(
            *conditions
        ).values(active=0)

        result_statement = self.db.run_statement(statement, 3)

        if result_statement:
            status_code = 200
            data = 'The product was updated.'

        else:
            status_code = 400
            data = "The product wasn't updated."

        return {'statusCode': status_code, 'data': data}
