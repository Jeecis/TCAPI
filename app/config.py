import os

# Redis Configuration
REDIS_USER_HOST = os.getenv('REDIS_USER_HOST', '127.0.0.1')
REDIS_USER_PORT = int(os.getenv('REDIS_USER_PORT', 6379))

REDIS_BOOKING_HOST = os.getenv('REDIS_BOOKING_HOST', '127.0.0.1')
REDIS_BOOKING_PORT = int(os.getenv('REDIS_BOOKING_PORT', 6380))

REDIS_INV_HOST = os.getenv('REDIS_INV_HOST', '127.0.0.1')
REDIS_INV_PORT = int(os.getenv('REDIS_INV_PORT', 6381))