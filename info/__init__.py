
from flask import Flask

from flask_sqlalchemy import SQLAlchemy

from redis import StrictRedis

from flask_wtf.csrf import CSRFProtect,generate_csrf

from config import config_dict

from flask_session import Session

import logging

from logging.handlers import RotatingFileHandler

from config import config_dict


# 为了解决循环导入我们需要延迟导入，我们需要蓝图导入放在真正需要注册蓝图的时候

# from info.module.index import index_db
from info.utlis.common import do_index_class


def create_log(config_name):
    """记录日志的配置信息"""

    # 设置日志的记录等级
    # config_dict[config_name].LOG_LEVEL获得日志记录等级
    logging.basicConfig(level=config_dict[config_name].LOG_LEVEL)  # 调试debug级

    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)

    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    # INFO：manager.py ：18 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')

    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)

    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


# 创建数据库对象
# 没有传入app不会真正的初始化操作，后期看需要调用app
# 把这个数据库对象放在外面给外界调用
db = SQLAlchemy()

# 申明类型
redis_store = None  # type:StrictRedis


# 工厂方法，根据传入的不同的配置信息，创建不同的app
def create_app(config_name):  # development-开发环境的app对象 production就是生产模式的appp

    # 0.调用日志方法
    create_log(config_name)

    # 创建app对象
    app = Flask(__name__)

    # 注册配置信息到app中
    # config_dict["development"]--->DevelopmentConfig
    # config_dict["producttion"]--->ProductionConfig
    config_class = config_dict[config_name]

    app.config.from_object(config_class)

    # 创建数据库对象
    # 懒加载
    db.init_app(app)

    # 延迟加载
    global redis_store

    # 创建redis数据库对象
    redis_store = StrictRedis(host=config_class.REDIS_HOST,

                              port=config_class.REDIS_PORT,

                              db=config_class.REDIS_NUM,

                              decode_responses=True)

    # 开启flask后端csrf验证保护机制

    csrf = CSRFProtect(app)

    # 借助第三方session类去调整flask中的session存储位置

    # flask_session的配置信息

    Session(app)

    @app.after_request

    def set_csrf_token(response):

        # 给前端cookie中设置csrf_token

    # 1.生成csrf_token随机字符串

        csrf_token = generate_csrf()

        # 2.借助response对象在cookie里面带上csrf_token

        response.set_cookie("csrf_token",csrf_token)

        return response

    # 注册过滤器

    app.add_template_filter(do_index_class,"do_index_class")

    # 为了解决循环导入我们需要延迟导入，我们需要蓝图导入放在真正需要注册蓝图的时候

    # 注册登录首页模块的蓝图

    from info.module.index import index_db

    app.register_blueprint(index_db)

    # 注册登录注册模块的蓝图
    from info.module.passport import passport_bp

    app.register_blueprint(passport_bp)

    # 注册新闻注册模块的蓝图

    from info.module.news import news_db

    app.register_blueprint(news_db)

    return app
