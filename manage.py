from flask import Flask

from flask_sqlalchemy import SQLAlchemy

from redis import StrictRedis

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








# 创建app对象
app = Flask(__name__)

# 注册配置信息到app中
app.config.from_object(Config)

# 创建数据库对象
db = SQLAlchemy(app)

# 创建redis数据库对象
redis_store = StrictRedis(host=Config.REDIS_HOST,

                          port=Config.REDIS_PORT,

                          db=Config.REDIS_NUM,

                          decode_responses=True)

@app.route("/")

def index():

    return "心境资讯"

if __name__ == '__main__':

    app.run(debug=True)
