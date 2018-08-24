from flask import Flask,session

from flask_sqlalchemy import SQLAlchemy

from redis import StrictRedis

from flask_wtf import CSRFProtect

from flask_session import Session

from flask_script import Manager

from config import config_dict

# 创建app对象
app = Flask(__name__)

# 注册配置信息到app中

# config_dict["development"]--->DevelopmentConfig
config_class = config_dict["development"]

app.config.from_object(config_class)

# 创建数据库对象
db = SQLAlchemy(app)

# 创建redis数据库对象
redis_store = StrictRedis(host=config_class.REDIS_HOST,

                          port=config_class.REDIS_PORT,

                          db=config_class.REDIS_NUM,)

# 开启flask后端csrf验证保护机制

csrf = CSRFProtect(app)

# 借助第三方session类去调整flask中的session存储位置

# flask_session的配置信息

Session(app)

# 创建manager管理类

manager = Manager(app)

@app.route("/")

def index():
    # 之前session数据存储在服务器上
    session["name"] = "liqiang"

    return "aaaa"

if __name__ == '__main__':

    manager.run()
