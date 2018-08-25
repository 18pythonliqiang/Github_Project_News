"""首页模块"""

from flask import Blueprint

# 1.创建蓝图对象

passport_bp = Blueprint("passport",__name__,url_prefix="/passport")

# 2.一定要让模块发现views

from .views import *