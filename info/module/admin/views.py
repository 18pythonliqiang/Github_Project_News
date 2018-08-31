from flask import request,render_template,url_for,current_app,session,redirect

from . import admin_bp

from info.models import User

# /admin/login
@admin_bp.route("/login",methods = ["POST","GET"])
def admin_login():

    """后台登陆模块"""
    if request.method == "GET":

        return render_template("admin/login.html")
#POST请求登陆校验提交
# 1.获取参数
    username = request.form.get("username")

    password = request.form.get("password")
# 2.校验参数

    if not all([username,password]):

        return render_template("admin/login.html",errmsg = "参数不足")

# 3.逻辑处理

    try:

        user = User.query.filter(User.mobile == username , User.is_admin == True).first()

    except Exception as e:

        current_app.logger.error(e)

        return render_template("admin/login.html", errmsg="参数不足")

# 校验密码

    if not user.check_passowrd(password):

        return render_template("admin/login.html", errmsg="密码不正确")

# 试用sessio记录管理员登录信息

    session["user_id"] = user.id

    session["nick_name"] = user.nick_name

    session["mobile"] = user.mobile

#记录是否时管理员
    session["id_admin"] = user.is_admin #Bad Request,The CSRF token is missing.

# 4.返回值
    return redirect(url_for("admin.admin_index"))

@admin_bp.route("/index",methods = ["POST","GET"])
def admin_index():
    return render_template("admin/index.html")






