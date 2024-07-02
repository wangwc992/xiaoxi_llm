import redis
import time

from app.common.core.config import settings  # 假设 settings 包含 Redis 配置
from app.common.utils.logging import get_logger  # 假设 get_logger 是日志记录函数

# 从配置文件加载 Redis 设置
redis_dict = settings["redis"]
logger = get_logger(__name__)

redis_client = None


# 创建 Redis 连接
def create_redis_connection():
    global redis_client
    redis_client = redis.Redis(
        host=redis_dict["host"],
        port=redis_dict["port"],
        db=redis_dict["db"],
        password=redis_dict["password"]
    )


# 装饰器：带重连机制的操作
def retry_on_failure(func):
    def wrapper(*args, **kwargs):
        for attempt in range(1, redis_dict["max_retries"] + 1):
            try:
                return func(*args, **kwargs)
            except redis.ConnectionError as e:
                logger.error(f"连接失败: {e}")
                logger.info(f"重试 {attempt}/{redis_dict['max_retries']} 次...")
                time.sleep(redis_dict["retry_delay"])
                create_redis_connection()  # 更新 Redis 连接
        raise redis.ConnectionError("达到最大重试次数，仍然无法连接到 Redis 服务器。")

    return wrapper


# 连接到 Redis
create_redis_connection()


# 字符串操作
@retry_on_failure
def set_string(key, value, expire=None):
    redis_client.set(key, value)
    if expire:
        redis_client.expire(key, expire)
    logger.info(f"已设置字符串键 {key} 的值为 {value}")


@retry_on_failure
def get_string(key):
    value = redis_client.get(key)
    return value.decode("utf-8") if value else None


@retry_on_failure
def delete_key(key):
    redis_client.delete(key)
    logger.info(f"已删除键 {key}")


# 哈希操作
@retry_on_failure
def set_hash(key, field, value, expire=None):
    redis_client.hset(key, field, value)
    if expire:
        redis_client.expire(key, expire)  # 设置哈希键的过期时间
    logger.info(f"已设置哈希键 {key} 字段 {field} 的值为 {value}，过期时间为 {expire} 秒")


@retry_on_failure
def get_hash_field(key, field):
    value = redis_client.hget(key, field)
    return value.decode("utf-8") if value else None


@retry_on_failure
def delete_hash_field(key, field):
    redis_client.hdel(key, field)
    logger.info(f"已删除哈希键 {key} 的字段 {field}")


@retry_on_failure
def get_hash_all(key):
    return redis_client.hgetall(key)


# 集合操作
@retry_on_failure
def add_to_set(key, *values, expire=None):
    redis_client.sadd(key, *values)
    if expire:
        redis_client.expire(key, expire)  # 设置集合键的过期时间
    logger.info(f"已将值 {values} 添加到集合键 {key}，过期时间为 {expire} 秒")


@retry_on_failure
def get_set_members(key):
    members = redis_client.smembers(key)
    return {m.decode("utf-8") for m in members}


@retry_on_failure
def remove_from_set(key, *values):
    redis_client.srem(key, *values)
    logger.info(f"已从集合键 {key} 中移除值 {values}")

# 示例使用
# if __name__ == "__main__":
#     try:
#         # 测试连接
#         redis_client.ping()
#         logger.info("连接成功！")
#
#         # 示例：字符串操作
#         set_string("example_key", "example_value", expire=60)
#         print(f'获取到的字符串值: {get_string("example_key")}')
#         delete_key("example_key")
#
#         # 示例：哈希操作
#         set_hash("example_hash", "field1", "value1")
#         print(f'获取到的哈希字段值: {get_hash_field("example_hash", "field1")}')
#         print(f'获取到的整个哈希: {get_hash_all("example_hash")}')
#         delete_hash_field("example_hash", "field1")
#
#         # 示例：集合操作
#         add_to_set("example_set", "value1", "value2", "value3")
#         print(f'获取到的集合成员: {get_set_members("example_set")}')
#         remove_from_set("example_set", "value1")
#
#     except redis.ConnectionError as e:
#         logger.error(f"最终连接失败: {e}")
