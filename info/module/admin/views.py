from flask import request, render_template, url_for, current_app, session, redirect

from . import admin_bp

from info.models import User


@admin_bp.route("/index", methods=["POST", "GET"])
def admin_index():
    return render_template("admin/index.html")


# /admin/login
@admin_bp.route("/login", methods=["POST", "GET"])
def admin_login():
    """后台登陆模块"""
    if request.method == "GET":

        # 从sessi中获取管理员用户数据
        user_id = session.get("user_id", None)

        is_admin = session.get("is_admin", None)

        # 如果管理员已经登录当他访问login页面的时候直接引导到后台管理首页
        if user_id and is_admin:
            return redirect(url_for("admin.admin_index"))

        return render_template("admin/login.html")
    # POST请求登陆校验提交
    # 1.获取参数
    username = request.form.get("username")

    password = request.form.get("password")
    # 2.校验参数

    if not all([username, password]):
        return render_template("admin/login.html", errmsg="参数不足")

    # 3.逻辑处理

    try:

        user = User.query.filter(User.mobile == username, User.is_admin == True).first()
        print(user)
    except Exception as e:

        current_app.logger.error(user)

        return render_template("admin/login.html", errmsg="参数不足")

    if not user:
        return render_template("admin/login.html", errmsg="没有此用户")

    # 校验密码

    if not user.check_passowrd(password):

        return render_template("admin/login.html", errmsg="密码错误")

    # 试用sessio记录管理员登录信息

    session["user_id"] = user.id

    session["nick_name"] = user.nick_name

    session["mobile"] = user.mobile

    # 记录是否时管理员

    session["is_admin"] = user.is_admin  # Bad Request,The CSRF token is missing.

    # 4.返回值
    return redirect(url_for("admin.admin_index"))
