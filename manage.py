from flask import Flask,session,current_app

from flask_script import Manager

from info import create_app

import logging

# 调用工厂方法，传入不同的配置，获取不同的app对象
app = create_app("development")

# 创建manager管理类
manager = Manager(app)

@app.route("/")

def index():
    # 之前session数据存储在服务器上
    session["name"] = "liqiang"

    logging.debug("debug日志信息：")
    logging.info("debug日志信息：")
    logging.warning("debug日志信息：")
    logging.error("debug日志信息：")
    logging.critical("debug日志信息：")

    current_app.logger.debug("flask封装的debug日志")

    return "aaaa"

if __name__ == '__main__':

    manager.run()
