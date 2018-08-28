from info import constants

from info.models import User, News

from . import news_db

from info.utlis.common import login_user_data

from flask import render_template, session, current_app, g


# 127.0.0.1:5000/news/2

@news_db.route("/<int:news_id>")
@login_user_data
def news_detail(news_id):

    user = g.user

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
