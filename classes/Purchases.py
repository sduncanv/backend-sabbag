import os
import boto3
from sqlalchemy import select, insert, update

from classes.Products import Products
from models.Users import UsersModel
from models.Purchases import PurchasesModel
from models.Products import ProductModel
from tools.Database import Database
from tools.FunctionsTools import (
    get_event_data, validate_event_data, CustomError
)


class Purchases:

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
        self.product_class = Products()
        self.client_cognito = boto3.client(
            'cognito-idp', region_name='us-east-1'
        )

    def create_purchase(self, event) -> dict:

        input_data = get_event_data(event)

        user_id = input_data.get('user_id', '')
        product_id = input_data.get('product_id', '')

        values = [
            ['user_id', int, user_id],
            ['product_id', int, product_id]
        ]

        is_valid = validate_event_data(values)
        if not is_valid['is_valid']:
            raise CustomError(is_valid['errors'][0], 400)

        statement = select(UsersModel).where(
            UsersModel.active == 1,
            UsersModel.user_id == user_id
        )

        user_found = self.db.run_select(statement)
        if not user_found:
            raise CustomError('User not found.', 404)

        statement = select(ProductModel).where(
            ProductModel.active == 1,
            ProductModel.product_id == product_id
        )

        product_found = self.db.run_select(statement)
        if not product_found:
            raise CustomError('Product not found.', 404)

        in_stock = product_found[0]['in_stock']
        quantity = product_found[0]['quantity']

        if in_stock == 0 or quantity == 0:
            raise CustomError('Product out of stock.', 400)

        statement = insert(PurchasesModel).values(
            user_id=user_id, product_id=product_id
        )

        result_statement = self.db.run_insert(statement)

        to_update = {'quantity': quantity - 1}

        if quantity == 1:
            to_update['in_stock'] = 0

        self.db.run_update(
            update(ProductModel).where(
                ProductModel.product_id == product_id
            ).values(
                **to_update
            )
        )
        status_code = 201

        return {'statusCode': status_code, 'data': result_statement}

    def get_purchase(self, event) -> dict:

        input_data = get_event_data(event)
        conditions = [PurchasesModel.active == 1]

        user_id = input_data.get('user_id', '')
        product_id = input_data.get('product_id', '')

        if user_id:
            conditions.append(PurchasesModel.user_id == user_id)

        if product_id:
            conditions.append(PurchasesModel.product_id == product_id)

        statement = select(PurchasesModel).where(
            *conditions
        )

        result_statement = self.db.run_select(statement)
        status_code = 200

        if not result_statement:
            status_code = 404
            result_statement = []

        return {'statusCode': status_code, 'data': result_statement}
