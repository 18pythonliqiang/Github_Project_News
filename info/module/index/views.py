import logging
from flask import session,current_app


from  . import index_db

# 使用蓝图
@index_db.route("/")

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