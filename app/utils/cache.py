"""
缓存管理模块
"""

import json
import pickle
import hashlib
import os
import shutil
from datetime import datetime, timedelta
from functools import wraps
from flask import current_app
import redis
from typing import Any, Optional, Union

class CacheManager:
    """缓存管理器"""

    def __init__(self, app=None):
        self.app = app
        self.redis_client = None
        self.file_cache_dir = None

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """初始化应用"""
        self.app = app

        # 配置Redis缓存
        try:
            redis_url = app.config.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            # 测试连接
            self.redis_client.ping()
            app.logger.info("Redis缓存连接成功")
        except Exception as e:
            app.logger.warning(f"Redis连接失败，将使用文件缓存: {e}")
            self.redis_client = None

        # 配置文件缓存
        self.file_cache_dir = os.path.join(app.instance_path, 'cache')
        os.makedirs(self.file_cache_dir, exist_ok=True)

    def _get_cache_key(self, key: str, prefix: str = "craftne") -> str:
        """生成缓存键"""
        return f"{prefix}:{key}"

    def _serialize_data(self, data: Any) -> str:
        """序列化数据"""
        try:
            if isinstance(data, (dict, list, str, int, float, bool)):
                return json.dumps(data, ensure_ascii=False)
            else:
                return pickle.dumps(data).hex()
        except Exception:
            return pickle.dumps(data).hex()

    def _deserialize_data(self, data: str) -> Any:
        """反序列化数据"""
        try:
            return json.loads(data)
        except (json.JSONDecodeError, ValueError):
            try:
                return pickle.loads(bytes.fromhex(data))
            except Exception:
                return data

    def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """设置缓存"""
        cache_key = self._get_cache_key(key)
        serialized_value = self._serialize_data(value)

        # 优先使用Redis
        if self.redis_client:
            try:
                return self.redis_client.setex(cache_key, expire, serialized_value)
            except Exception as e:
                current_app.logger.warning(f"Redis设置缓存失败: {e}")

        # 降级到文件缓存
        return self._set_file_cache(cache_key, serialized_value, expire)

    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        cache_key = self._get_cache_key(key)

        # 优先使用Redis
        if self.redis_client:
            try:
                value = self.redis_client.get(cache_key)
                if value is not None:
                    return self._deserialize_data(value)
            except Exception as e:
                current_app.logger.warning(f"Redis获取缓存失败: {e}")

        # 降级到文件缓存
        return self._get_file_cache(cache_key)

    def delete(self, key: str) -> bool:
        """删除缓存"""
        cache_key = self._get_cache_key(key)

        # Redis删除
        redis_deleted = False
        if self.redis_client:
            try:
                redis_deleted = bool(self.redis_client.delete(cache_key))
            except Exception as e:
                current_app.logger.warning(f"Redis删除缓存失败: {e}")

        # 文件缓存删除
        file_deleted = self._delete_file_cache(cache_key)

        return redis_deleted or file_deleted

    def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        cache_key = self._get_cache_key(key)

        # Redis检查
        if self.redis_client:
            try:
                if self.redis_client.exists(cache_key):
                    return True
            except Exception as e:
                current_app.logger.warning(f"Redis检查缓存失败: {e}")

        # 文件缓存检查
        return self._exists_file_cache(cache_key)

    def _set_file_cache(self, key: str, value: str, expire: int) -> bool:
        """设置文件缓存"""
        try:
            cache_file = os.path.join(self.file_cache_dir, f"{hashlib.md5(key.encode()).hexdigest()}.cache")
            cache_data = {
                'value': value,
                'expire_time': (datetime.now() + timedelta(seconds=expire)).timestamp()
            }

            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f)

            return True
        except Exception as e:
            current_app.logger.warning(f"文件缓存设置失败: {e}")
            return False

    def _get_file_cache(self, key: str) -> Optional[Any]:
        """获取文件缓存"""
        try:
            cache_file = os.path.join(self.file_cache_dir, f"{hashlib.md5(key.encode()).hexdigest()}.cache")

            if not os.path.exists(cache_file):
                return None

            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            # 检查是否过期
            if datetime.now().timestamp() > cache_data['expire_time']:
                os.remove(cache_file)
                return None

            return self._deserialize_data(cache_data['value'])

        except Exception as e:
            current_app.logger.warning(f"文件缓存获取失败: {e}")
            return None

    def _delete_file_cache(self, key: str) -> bool:
        """删除文件缓存"""
        try:
            cache_file = os.path.join(self.file_cache_dir, f"{hashlib.md5(key.encode()).hexdigest()}.cache")
            if os.path.exists(cache_file):
                os.remove(cache_file)
                return True
        except Exception as e:
            current_app.logger.warning(f"文件缓存删除失败: {e}")
        return False

    def _exists_file_cache(self, key: str) -> bool:
        """检查文件缓存是否存在"""
        try:
            cache_file = os.path.join(self.file_cache_dir, f"{hashlib.md5(key.encode()).hexdigest()}.cache")

            if not os.path.exists(cache_file):
                return False

            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            # 检查是否过期
            if datetime.now().timestamp() > cache_data['expire_time']:
                os.remove(cache_file)
                return False

            return True

        except Exception:
            return False

    def clear_expired(self):
        """清理过期的文件缓存"""
        try:
            for filename in os.listdir(self.file_cache_dir):
                if filename.endswith('.cache'):
                    cache_file = os.path.join(self.file_cache_dir, filename)
                    try:
                        with open(cache_file, 'r', encoding='utf-8') as f:
                            cache_data = json.load(f)

                        if datetime.now().timestamp() > cache_data['expire_time']:
                            os.remove(cache_file)
                    except Exception:
                        # 如果文件损坏，直接删除
                        os.remove(cache_file)
        except Exception as e:
            current_app.logger.warning(f"清理过期缓存失败: {e}")

    def delete_map_cache(map_id: int):
        """删除地图相关的所有缓存数据"""
        try:
            # 删除文件缓存
            cache_dir = current_app.config.get('CACHE_DIR', 'instance/cache')
            map_cache_dir = os.path.join(cache_dir, f'map_{map_id}')
            if os.path.exists(map_cache_dir):
                shutil.rmtree(map_cache_dir)
                current_app.logger.info(f"已删除地图 {map_id} 的缓存目录: {map_cache_dir}")

            # 删除Redis缓存（如果有）
            try:
                redis_url = current_app.config.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
                redis_client = redis.from_url(redis_url, decode_responses=True)

                # 删除相关的缓存键
                keys_to_delete = [
                    f"craftne:map_{map_id}:*",
                    f"craftne:blocks_{map_id}",
                    f"craftne:stats_{map_id}",
                    f"craftne:threejs_{map_id}"
                ]

                for pattern in keys_to_delete:
                    if '*' in pattern:
                        # 使用模式匹配删除
                        keys = redis_client.keys(pattern)
                        if keys:
                            redis_client.delete(*keys)
                    else:
                        redis_client.delete(pattern)

                current_app.logger.info(f"已删除地图 {map_id} 的Redis缓存")

            except Exception as e:
                current_app.logger.warning(f"删除Redis缓存失败: {str(e)}")

        except Exception as e:
            current_app.logger.error(f"删除地图缓存失败: {str(e)}")
            raise


# 全局缓存管理器实例
cache_manager = CacheManager()

def cache_result(key_func=None, expire=3600):
    """缓存结果装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # 默认使用函数名和参数生成键
                key_parts = [func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
                cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()

            # 尝试从缓存获取
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result

            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, expire)

            return result
        return wrapper
    return decorator
