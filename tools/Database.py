from decimal import Decimal
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Database:

    def __init__(self, db, host, user, password, port):

        self.db = db
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.engine = create_engine(
            f'mysql+pymysql://{user}:{password}@{host}:{port}/{db}'
        )

    def execute_statement(self, statement):

        with self.engine.connect() as connection:
            consult = connection.execute(statement)
            connection.commit()

        return consult

    def run_insert(self, statement):

        consult = self.execute_statement(statement)
        result = consult.inserted_primary_key._asdict()
        return result

    def run_select(self, statement):

        consult = self.execute_statement(statement)
        format_result = []

        for row in consult:
            format_row = {}

            for key, val in row._mapping.items():

                if isinstance(val, Decimal):
                    format_row[key] = float(val)

                elif isinstance(val, datetime):
                    format_row[key] = val.strftime("%Y-%m-%d %H:%M:%S")

                else:
                    format_row[key] = val

            format_result.append(format_row)

        return format_result

    def run_update(self, statement):

        consult = self.execute_statement(statement)
        result = consult.last_updated_params()
        return result
