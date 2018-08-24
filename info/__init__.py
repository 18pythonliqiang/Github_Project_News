from flask import Flask

from flask_sqlalchemy import SQLAlchemy

from redis import StrictRedis

from flask_wtf import CSRFProtect

from config import config_dict

from flask_session import Session

# 工厂方法，根据传入的不同的配置信息，创建不同的app
def create_app(config_name): #development-开发环境的app对象 production就是生产模式的appp

    # 创建app对象
    app = Flask(__name__)

    # 注册配置信息到app中

    # config_dict["development"]--->DevelopmentConfig
    # config_dict["producttion"]--->ProductionConfig
    config_class = config_dict[config_name]

    app.config.from_object(config_class)

    # 创建数据库对象
    db = SQLAlchemy(app)

    # 创建redis数据库对象
    redis_store = StrictRedis(host=config_class.REDIS_HOST,

                              port=config_class.REDIS_PORT,

                              db=config_class.REDIS_NUM, )

    # 开启flask后端csrf验证保护机制

    csrf = CSRFProtect(app)

    # 借助第三方session类去调整flask中的session存储位置

    # flask_session的配置信息

    Session(app)

    return app
