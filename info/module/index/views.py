import logging
from flask import g
from flask import request, jsonify
from flask import session, current_app, render_template
from info.models import User, News, Category
from info.utlis.response_code import RET
from . import index_db
from info import constants
from info.utlis.common import login_user_data


# 127.0.0.1:5000/news_list  GET
@index_db.route('/news_list')
def get_news_list():
    """获取首页新闻列表数据"""
    """
    1.获取参数
        1.1 cid新闻分类id page当前页码（默认值：1） per_page当前页显示新闻的条数(默认值：10)
    2.校验参数
        2.1 非空判断
        2.2 数据的类型判断
    3.逻辑处理
        3.1 根据分类id查询数据，根据新闻的创建时间排序（降序）然后进行分页处理
    4.返回值处理
    """
    # 1.1 cid新闻分类id page当前页码（默认值：1） per_page当前页显示新闻的条数(默认值：10)
    params_dict = request.args
    cid = params_dict.get("cid")
    page = params_dict.get("page", 1)
    per_page = params_dict.get("per_page", constants.HOME_PAGE_MAX_NEWS)

    # 2.1 非空判断
    if not all([cid, page, per_page]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不足")
    # 2.2 数据的类型判断
    try:
        cid = int(cid)
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="数据类型错误")

    """
    等同于下面的代码：
    if cid == 1:
        paginate = News.query.filter().order_by(News.create_time.desc())\
            .paginate(page, per_page, False)
    else:
        paginate = News.query.filter(News.category_id == cid).order_by(News.create_time.desc())\
            .paginate(page, per_page, False)

    """
    # 添加查询条件的列表
    # 查询审核通过的新闻
    # News.status == 0新闻已经审核通过了
    filters = [News.status == 0]
    if cid != 1:
        # == 数据库底层已经实现了 == 函数返回的不是bool值而是查询条件
        filters.append(News.category_id == cid)

    try:
        # 3.1 根据分类id查询数据，根据新闻的创建时间排序（降序）然后进行分页处理
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()) \
            .paginate(page, per_page, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询首页新闻列表数据异常")

    # 获取当前页码的所有数据(模型对象列表)
    items = paginate.items
    # 当前页码
    current_page = paginate.page
    # 总页数
    total_page = paginate.pages
    # 将模型对象列表转换成字典对象列表
    news_dict_list = []
    # 注意：items没有数据的时候建议使用[]代替
    for news in items if items else []:
        # news.to_dict() 将新闻对象转成成字典
        news_dict_list.append(news.to_dict())

    # 组织响应数据
    data = {
        "newsList": news_dict_list,
        "current_page": current_page,
        "total_page": total_page
    }
    # 4.返回值处理
    return jsonify(errno=RET.OK, errmsg="查询新闻列表数据成功", data=data)


# ImportError: cannot import name 'redis_store' 循环导入问题
# 2.使用蓝图
@index_db.route('/')
@login_user_data
def index():
    # -------1.当用户登录成功后可以使用session对象获取里面的用户user_id -------
    user = g.user

    # -------2.查询新闻的点击排行数据 -------
    # 1.根据浏览量查询6条点击排行的新闻数据
    # [news1, news2,....] news属于News的对象
    try:
        news_model_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
        # 切记不能返回return 否则首页都渲染不了啦，只需要返回一个None的数据即可

    # 2. 将模型列表转换成字典列表
    news_dict_list = []
    for news in news_model_list if news_model_list else None:
        # 获取到new对象调用to_dict方法将对象转换成字典，再添加到news_dict_list中
        news_dict_list.append(news.to_dict())

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


# bug信息：   GET /favicon.ico 404
@index_db.route('/favicon.ico')
def favicon():
    """返回项目的图标"""
    # send_static_file 找到static文件夹下面的静态文件发送给浏览器显示
    return current_app.send_static_file("news/favicon.ico")
