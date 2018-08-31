from info import db, constants

from info.utlis.response_code import RET

from . import profile_bp

from flask import render_template, g, request, jsonify, session, current_app

from info.utlis.common import login_user_data

from info.utlis.image_store import qiniu_image_store


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


@profile_bp.route("/pic_info", methods=["POST", "GET"])
@login_user_data
def pic_info():
    #     展示用户头像页面，修改用户接口

    # 获取用户对象
    user = g.user

    if request.method == "GET":
        return render_template("news/user_pic_info.html", data={"user_info": user.to_dict()})

    # 获取用户上传的图片二进制数据上传到七牛云
    try:
        avatar_data = request.files.get("avatar").read()

    except Exception as e:

        current_app.logger.error(e)

        return jsonify(errno=RET.PARAMERR, errmsg="读取文件出错")

    #  校验参数
    if not avatar_data:
        return jsonify(errno=RET.NODATA, errmsg="图片数据不能为空")

    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    # 逻辑处理
    try:
        # 调用封装好的方法将图片上传到七牛云
        image_name = qiniu_image_store(avatar_data)

    except Exception as e:

        current_app.logger.error(e)

        return jsonify(errno=RET.DBERR, errmsg="保存用户url失败")

    # 只将图片名称存储，乙方修改七牛云域名

    user.avatar_url = image_name

    try:

        db.session.commit()

    except Exception as e:

        current_app.logger.error(e)

        db.session.rollback()

        return jsonify(errno=RET.DBERR, errmsg="保存用户url失败")

    #     z组织响应对象
    full_url = constants.QINIU_DOMIN_PREFIX + image_name

    data = {

        "avatar_data": full_url
    }
    return jsonify(errno=RET.OK, errmsg="上传图片到七牛云成功", data=data)


@profile_bp.route("/pass_info", methods=["POST", "GET"])
@login_user_data
def pass_info():
    #     展示修改密码页面，修改密码后端逻辑
    if request.method == "GET":
        return render_template("news/user_pass_info.html")

    #     POST请求修改密码

    # 1.修改参数

    old_password = request.json.get("old_password")

    new_password = request.json.get("new_password")

    user = g.user

    #   2.校验参数

    if not all([old_password, new_password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不足")

    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    #     3.逻辑处理

    if not user.check_passowrd(old_password):
        return jsonify(errno=RET.PARAMERR, errmsg="旧密码填写错误")

    #     将新的密码赋值给password属性

    user.password = new_password

    try:

        db.session.commit()

    except Exception as e:

        current_app.logger.error(e)

        return jsonify(errno=RET.DBERR, errmsg="保存用户对象异常")

    #     返回值
    return jsonify(errno=RET.OK, errmsg="修改密码成功")


@profile_bp.route("/collection")
@login_user_data
def collection():
    # 用户收藏的列表
    # 1.获取参数
    # /user/collection?p=
    p = request.args.get("p", 1)

    user = g.user

    # 2.参数校验

    try:

        p = int(p)

    except Exception as e:

        current_app.logger.error(e)

        p = 1

    # 3.逻辑处理

    # lazy="dynamic"如果真正用到里面的值，就会给你返回一个列表数据，如果只是简单的擦讯就会返回一个查询对象给你
    news_list = []

    current_page = 1

    total_page = 1

    if user:

        try:

            paginate = user.collection_news.paginate(p, constants.USER_COLLECTION_MAX_NEWS, False)

            news_list = paginate.items

            current_page = paginate.page

            total_page = paginate.pages


        except Exception as e:

            current_app.logger.error(e)

    # 新闻对象列表转成字典对象

    news_dict_list = []

    for news in news_list if news_list else []:
        news_dict_list.append(news.to_review_dict())

    data = {

        "collections": news_dict_list,

        "current_page": current_page,

        "total_page": total_page
    }
    # 4.返回值
    return render_template("news/user_collection.html", data=data)
