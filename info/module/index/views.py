import logging

from flask import session, current_app, render_template, request, jsonify

from info.models import User, News, Category

from . import index_db

from info import redis_store, constants

from info import models

from info.utlis.response_code import RET


# ImportError: cannot import name 'redis_store' 出现循环导入

# 使用蓝图

@index_db.route("/")
def index():
    # -------1.当用户登录成功后可以使用session对象获取里面的用户user_id -------

    # 1. 获取user_id
    user_id = session.get("user_id")

    # 2. 根据user_id查询用户对象

    user = None  # type:User

    # 3.将用户对象转换成python字典

    try:

        if user_id:
            user = User.query.get(user_id)

    except Exception as e:

        current_app.logger.error(e)

        # -------2.查询新闻的点击排行数据 -------
        # 1.根据浏览量查询6条点击排行的新闻数据
        # [news1, news2,....] news属于News的对象

    try:

        news_model_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)

    except Exception as e:

        current_app.logger.error(e)

    # 切记不能返回return 否则首页都渲染不了啦，只需要返回一个None的数据即可

    news_dict_list = []

    for news in news_model_list if news_model_list else None:
        news_dict_list.append(news.to_dict())

        # ----------3,查询新闻分类模块----------------

        # -------3.查询新闻的分类数据 -------
    categories = []

    try:
        categories = Category.query.all()

    except Exception as e:

        current_app.logger.error(e)

        # 模型列表转字典列表

    category_dict_list = []

    for category in categories if categories else []:

        # 将分类对象转成字典对象添加到列表

        category_dict_list.append(category.to_dict())

    data = {

        "user_info": user.to_dict() if user else None,

        "newsClicksList": news_dict_list,

        "category_dict_list": category_dict_list
    }

    return render_template("index.html", data=data)


@index_db.route("/favicon.ico")
def favicon_ico1():
    return current_app.send_static_file("news/favicon.ico")


# local variable 'news_model_list' referenced before assignment

#  赋值前引用的局部变量 "news_model_list"

@index_db.route("/news_list")
def get_news_list():
    """获取首页新闻列表数据"""

    # 1.获取参数
    #     1.cid新闻分类id，page当前页码，per_page当前显示的新闻条数

    params_dict = request.args

    cid = params_dict.get("cid")

    page = params_dict.get("page", 1)

    per_page = params_dict.get("per_page", constants.HOME_PAGE_MAX_NEWS)

    # 2.校验参数
    #     1.非空判断

    if not all([cid, page, per_page]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不足")

    #     2.数据类型判断

    try:

        cid = int(cid)

        page = int(page)

        per_page = int(per_page)

    except Exception as e:

        current_app.logger.error(e)

        return jsonify(errno=RET.PARAMERR, errmsg="数据类型错误")

    # 3.逻辑处理
    #     1.根据分类id查询数据，根据新闻的创建时间降序排序，然后进行分页处理

    filters = []

    if cid != 1:
        filters.append(News.category_id == cid)

    try:
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()) \
            .paginate(page, per_page, False)

    except Exception as e:

        current_app.logger.error(e)

        return jsonify(errno=RET.DBERR, errmsg="查询首页新闻列表数据异常")
    #    获取当前页码所有数据
    items = paginate.items

    #     当前页吗
    current_page = paginate.page

    # 总页数
    total_page = paginate.pages

    # 将模型对象转换成列表

    new_dict_list = []

    # items没有数据的时候建议用[]
    for news in items if items else []:
        # 将新问对象转换成字典
        new_dict_list.append(news.to_dict())

    # 组织响应数据
    data = {

        "newsList": new_dict_list,

        "current_page": current_page,

        "total_page": total_page
    }

    # 4.返回值处理

    return jsonify(errno=RET.OK, errmsg="查询新闻列表数据成功", data=data)
