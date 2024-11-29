import redis
from config import *

user_redis = redis.Redis(host=REDIS_USER_HOST, port=REDIS_USER_PORT, db=0, decode_responses=True)
booking_redis = redis.Redis(host=REDIS_BOOKING_HOST, port=REDIS_BOOKING_PORT, db=0, decode_responses=True)
inventory_redis = redis.Redis(host=REDIS_INV_HOST, port=REDIS_INV_PORT, db=0, decode_responses=True)