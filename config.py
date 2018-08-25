from redis import StrictRedis

import logging


# 创建项目配置类父类
class Config(object):
    # 开启debug
    DEBUG = True

    # mysql数据库配置信息
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/informtion"

    # 开启数据库跟踪
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # redis数据库的配置信息
    REDIS_HOST = "127.0.0.1"

    REDIS_PORT = 6379

    REDIS_NUM = 7

    # session配置
    SECRET_KEY = "dasdasfewffdasdas"

    # 调整session存储到redis的配置信息
    # 设置储存session的数据库类型
    SESSION_TYPE = "redis"  # 指定 session 保存到 redis 中

    SESSION_REDIS = StrictRedis(host=REDIS_HOST,

                                port=REDIS_PORT,

                                db=REDIS_NUM)  # 使用 redis 的实例

    SESSION_USE_SIGNER = True  # 让 cookie 中的 session_id 被加密签名处理

    PERMANENT_SESSION_LIFETIME = 86400  # session 的有效期，单位是秒


class DevelopmentConfig(Config):
    # 开发模式
    # 开启debug模式
    DEBUG = True

    # 设置开放环境日志级别
    LOG_LEVEL = logging.DEBUG


class ProductionConfig(Config):
    # 线上模式
    # 关闭debug模式
    DEBUG = False

    # 设置开放环境日志级别
    LOG_LEVEL = logging.WARNING

    # SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@阿里云:3306/informtion"


# 接口给外界调用
# config_dict["development"] ---> DevelopmentConfig
config_dict = {

    "development": DevelopmentConfig,

    "production": ProductionConfig
}
