"""首页模块"""

from flask import Blueprint

# 1.创建蓝图对象

news_db = Blueprint("news",__name__,url_prefix="/news")

# 2.一定要让模块发现views

from .views import *