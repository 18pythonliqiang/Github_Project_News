"""后台管理模块"""
from flask import Blueprint

admin_bp = Blueprint("admin",

                     __name__,

                     url_prefix="/admin")

from .views import *


@admin_bp.before_request
def before_request():
    """拦截普通用户能够进入后台管理首页"""
    # 不是去访问 /admin/login 就进入if判断进行拦截处理
    if not request.url.endswith(url_for("admin.admin_login")):
        user_id = session.get("user_id", None)
        is_admin = session.get("is_admin", None)
        # 用户没有登录或者用户不是管理员 引导到新闻首页
        if not user_id or not is_admin:
            return redirect('/')
