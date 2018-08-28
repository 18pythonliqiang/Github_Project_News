from info import constants
from info.models import User, News
from . import news_db

from flask import render_template, session, current_app


# 127.0.0.1:5000/news/2
@news_db.route("/<int:news_id>")

def news_detail(news_id):

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

    for news in news_model_list if news_model_list else []:

        news_dict_list.append(news.to_dict())

    data = {

        "user_info": user.to_dict() if user else None,

        "newsClicksList": news_dict_list,
    }

    # 新闻详情页

    return render_template("news/detail.html",data = data)
