import redis
from config import *

user_redis = redis.Redis(host=REDIS_USER_HOST, port=int(REDIS_USER_PORT), db=0, decode_responses=True)
booking_redis = user_redis
inventory_redis = user_redis