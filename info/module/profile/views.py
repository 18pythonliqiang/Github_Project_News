from info import db
from info.utlis.response_code import RET
from . import profile_bp

from flask import render_template, g, request, jsonify, session, current_app

from info.utlis.common import login_user_data


@profile_bp.route("/info")
@login_user_data
def user_info():
    # 返回个人首页
    user = g.user

    data = {

        "user_info": user.to_dict() if user else None,
    }

    return render_template("news/user.html", data=data)


@profile_bp.route("/base_info", methods=["POST", "GET"])
@login_user_data
def base_info():
    # 获取用户基本资料页面，修改用户基本资料页面

    user = g.user
    # 获取用户基本资料页面 GET
    if request.method == "GET":
        data = {

            "user_info": user.to_dict() if user else None,
        }

        return render_template("news/user_base_info.html", data=data)

    # 修改用户基本资料页面 POST

    params_dict = request.json

    nick_name = params_dict.get("nick_name")

    signature = params_dict.get("signature")

    gender = params_dict.get("gender")

    if not all([nick_name, signature, gender]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不足")

    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    if gender not in ["MAN", "WOMAN"]:
        return jsonify(errno=RET.PARAMERR, errmsg="action数据填写错误")

    user.nick_name = nick_name

    user.signature = signature

    user.gender = gender

    #  更新session中的nick_name数据
    session["nick_name"] = nick_name

    # 将修改操作保存回数据库

    try:
        db.session.commit()

    except Exception as e:

        current_app.logger.error(e)

        db.session.rollback()

        return jsonify(errno=RET.DBERR, errmsg="修改用户数据异常")

    return jsonify(errno=RET.OK, errmsg="修改用户数据成功")
