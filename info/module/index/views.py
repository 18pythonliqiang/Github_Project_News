import logging

from flask import session, current_app, render_template

from . import index_db

from info import redis_store

from info import models

# ImportError: cannot import name 'redis_store' 出现循环导入

# 使用蓝图
@index_db.route("/")
def index():
    return render_template("index.html")

@index_db.route("/favicon.ico")
def favicon_ico1():
    return current_app.send_static_file("news/favicon.ico")
