import os
import redis


class RedisTools:

    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST'),
            port=os.getenv('REDIS_PORT'),
            password=os.getenv('REDIS_PASSWORD'),
            username=os.getenv('REDIS_USERNAME'),
            ssl=False,
            decode_responses=True
        )

    def set_data(self, key, value, time=300):

        result = self.redis_client.setex(key, time, value)
        return result

    def get_data(self, key):
        result = self.redis_client.get(key)
        return result

    def generrate_key(
        self, product_id=0, category='', limit=0, offset=0
    ):
        key = f"products-get-{product_id}-{category}-{limit}-{offset}"
        return key

    def delete_key(self, key):

        for k in self.redis_client.scan_iter(key):
            self.redis_client.delete(k)

        return True
