from flask import Blueprint

profile_bp = Blueprint("profile",__name__,url_prefix="/user")

# 切记一定要让模块发现views

from . views import *