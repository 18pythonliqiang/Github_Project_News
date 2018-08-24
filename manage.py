from flask import Flask,session

from flask_sqlalchemy import SQLAlchemy

from redis import StrictRedis

from flask_wtf import CSRFProtect

from flask_session import Session

# 创建项目配置类

class Config(object):

    # 开启debug
    DEBUG = True

    #mysql数据库配置信息
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/informtion"

    # 开启数据库跟踪
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #redis数据库的配置信息
    REDIS_HOST = "127.0.0.1"

    REDIS_PORT = 6379

    REDIS_NUM = 7

    #session配置
    SECRET_KEY = "dasdasfewffdasdas"

    # 调整session存储到redis的配置信息
    # 设置储存session的数据库类型
    SESSION_TYPE = "redis" # 指定 session 保存到 redis 中

    SESSION_REDIS = StrictRedis(host=REDIS_HOST,

                                port=REDIS_PORT,

                                db=REDIS_NUM) # 使用 redis 的实例

    SESSION_USE_SIGNER = True # 让 cookie 中的 session_id 被加密签名处理

    PERMANENT_SESSION_LIFETIME = 86400 # session 的有效期，单位是秒


# 创建app对象
app = Flask(__name__)

# 注册配置信息到app中
app.config.from_object(Config)

# 创建数据库对象
db = SQLAlchemy(app)

# 创建redis数据库对象
redis_store = StrictRedis(host=Config.REDIS_HOST,

                          port=Config.REDIS_PORT,

                          db=Config.REDIS_NUM,)

# 开启flask后端csrf验证保护机制

csrf = CSRFProtect(app)

# 借助第三方session类去调整flask中的session存储位置

# flask_session的配置信息

Session(app)

@app.route("/")

def index():
    # 之前session数据存储在服务器上
    session["name"] = "liqiang"

    return "aaaa"

if __name__ == '__main__':

    app.run(debug=True)
