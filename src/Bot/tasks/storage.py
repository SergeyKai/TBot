from redis import Redis

from Bot.config import Config

posts_storage = Redis(
    host=Config.REDIS_CONFIG.HOST,
    port=Config.REDIS_CONFIG.PORT,
    db=1,
    decode_responses=Config.REDIS_CONFIG.DECODE_RESPONSE,
)
