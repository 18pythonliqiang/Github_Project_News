"""首页模块"""

from flask import Blueprint

# 1.创建蓝图对象

index_db = Blueprint("index",__name__)

# 2.一定要让模块发现views

from .views import *