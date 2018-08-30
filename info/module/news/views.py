from info import constants, db

from info.models import User, News, Comment, CommentLike

from info.utlis.response_code import RET

from . import news_db

from info.utlis.common import login_user_data

from flask import render_template, session, current_app, g, abort, request, jsonify


@news_db.route("/comment_like", methods=["POST"])
@login_user_data
def comment_like():
    """评论的点赞、取消点赞"""
    # 1.获取参数
    # 用户对象，新闻id，评论id，action（点赞或者取消点赞）

    params_dict = request.json

    news_id = params_dict.get("news_id")

    comment_id = params_dict.get("comment_id")

    user = g.user

    action = params_dict.get("action")

    # 2.校验参数

    # 1.非空判断
    if not all([news_id, comment_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不足")

    #     2.是否登陆
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    if action not in ["add", "remove"]:
        return jsonify(errno=RET.PARAMERR, errmsg="action数据填写错误")

    # 3.逻辑处理
    #   1.根据评论id获取评论模型对象，（只有评论存在的时候才能去点赞，取消点赞）

    try:

        comment = Comment.query.get(comment_id)

    except Exception as e:

        current_app.logger.error(e)

        return jsonify(errno=RET.DBERR, errmsg="查询评论数据异常")

    if not comment:
        return jsonify(errno=RET.NODATA, errmsg="评论不存在")

    #     2.根据action去完成点赞或者取消点赞的功能

    if action == "add":

        #         1.点赞 根据user_id 和 comment_id 查询 CommentLike是否存在

        #         2.CommentLike存在，表示用户点过赞

        comment_like = CommentLike.query.filter(CommentLike.user_id == user.id,

                                                CommentLike.comment_id == comment_id).first()
        if not comment_like:
            #     CommentLike不存在，新建CommentLike模型对象最终保存到数据库
            comment_like = CommentLike()

            comment_like.user_id = user.id

            comment_like.comment_id = comment_id

            db.session.add(comment_like)

            comment.like_count += 1

    else:

    # 取消点赞：根据user_id 和 comment_id 查询CommentLike是否存在

    # 只有comment_like对象存在的时候才能去消除点赞

        comment_like = CommentLike.query.filter(CommentLike.user_id == user.id,

                                            CommentLike.comment_id == comment_id).first()

    # CommentLike存在才取消点赞

        if comment_like:
        #             删除数据库数据

            db.session.delete(comment_like)

        #             记录comment模型的点赞书-1

            comment.like_count -= 1

    # 将上述对于数据库模型对象的修改提交到数据库

    try:

        db.session.commit()

    except Exception as e:

        current_app.logger.error(e)

        db.session.rollback()

        return jsonify(errno=RET.DBERR, errmsg="保存数据异常")

    # 返回值处理
    return jsonify(errno=RET.OK, errmsg="OK")


@news_db.route("/news_comment", methods=['POST'])
@login_user_data
def news_comment():
    #     评论接口（主评论，子评论）

    # 1.获取参数
    #     1.用户对象，新闻id，评论内容，主评论id

    params_dict = request.json

    news_id = params_dict.get("news_id")

    comment = params_dict.get("comment")

    parent_id = params_dict.get("parent_id")

    user = g.user

    # 2.校验参数
    #      1.非空判断

    if not all([news_id, comment]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不足")

    #       2.判断用户是否登录

    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    # 3.逻辑处理

    #     1.新闻id查询该新闻（新闻存在就去评论）
    try:

        news = News.query.get(news_id)

    except Exception as e:

        current_app.logger.error(e)

        return jsonify(errno=RET.DBERR, errmsg="查询新闻对象异常")

    #      2.创建评论模型

    comment_obj = Comment()

    comment_obj.user_id = user.id

    comment_obj.news_id = news_id

    comment_obj.content = comment

    #       3.判断主评论id是否有值

    if parent_id:
        # parent_id有值表示是子评论

        comment_obj.parent_id = parent_id

    # 4.将模型对象保存到数据库

    try:

        db.session.add(comment_obj)

        db.session.commit()

    except Exception as e:

        current_app.logger.error(e)

        return jsonify(errno=RET.DBERR, errmsg="保存评论对象到数据库异常")

    # 4.返回值处理

    return jsonify(errno=RET.OK, errmsg="评论成功", data=comment_obj.to_dict())


@news_db.route("/news_collect", methods=["POST"])
@login_user_data
def news_collect():
    # 收藏和取消收藏
    # 1.获取参数
    # 1.用户对象，新闻id，action（是否收藏）
    params_dict = request.json

    news_id = params_dict.get("news_id")

    action = params_dict.get("action")

    user = g.user

    # 2.校验参数
    # 1.非空判断
    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不足")
    # 2.是否登录

    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    # 3.action状态  action  in  ["collect","cancel_collect"]

    if action not in ["collect", "cancel_collect"]:
        return jsonify(errno=RET.PARAMERR, errmsg="参数填写错误")
    # 3.逻辑处理

    # 1.还根据新闻id查询该新闻

    news = None

    try:

        news = News.query.get(news_id)

    except Exception as e:

        current_app.logger.error(e)

        return jsonify(errno=RET.DBERR, errmsg="查询新闻数据异常")

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="新闻不存在")

    if action == "collect":

        # 3.收藏，将新闻对象从收藏列表中添加
        user.collection_news.append(news)

    # 2.取消收藏，将新新闻对象从收藏列表中移出
    else:
        user.collection_news.remove(news)

    # 4.提交修改

    try:
        db.session.commit()

    except Exception as e:

        current_app.logger.error(e)

        db.session.rollback()

        return jsonify(errno=RET.DBERR, errmsg="提交数据到数据库异常")
    # 4.返回值处理
    return jsonify(errno=RET.OK, errmsg="OK")


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

    # ---------------------3.新闻详情数据----------------------------

    try:

        news = News.query.get(news_id)

    except Exception as e:

        current_app.logger.error(e)

    if not news:
        abort(404)

    #     浏览量自增

    news.clicks += 1

    # 将模型对象的修改提交到数据库
    try:

        db.session.commit()

    except Exception as e:

        current_app.logger.error(e)

        db.session.rollback()

        abort(404)

    # ---------4.查询用户是否收藏该新闻-----------------------

    # 表示用户收藏了该新闻
    is_collected = False

    if user:

        if news in user.collection_news:
            # news在用户收藏的新闻列表类

            is_collected = True

    # 查询该新闻的评论数据

    try:

        comments = Comment.query.filter(Comment.news_id == news.id).order_by(Comment.create_time.desc()).all()

    except Exception as e:

        current_app.logger.error(e)
    #     需求：查询当前用户在当前新闻的评论里具体点赞了那几条评论

    # 1.查询当前新闻所有的评论，取得所有评论的id ----list 【1,2,3,4,5,6】

    if user:

        try:

            comment_id_list = [comment.id for comment in comments]

            # 2.在通过评论点赞模型（CommentLike）查询当前用户点赞了那些评论 --【模型1，模型2，。。。】

            commentlike_model_list = CommentLike.query.filter(CommentLike.comment_id.in_(comment_id_list),

                                                            CommentLike.user_id == user.id).all()

            # 3.comment_like.comment_id 通过上一步的模型列表，获取所有点赞的评论id

            commentlike_id_list = [commentlike.comment_id for commentlike in commentlike_model_list]


        except Exception as e:

            current_app.logger.error(e)

    comment_dict_list = []

    for comment in comments if comments else []:

        comment_dict = comment.to_dict()

    #     评论点赞的标志位

        comment_dict["is_like"] = False

        if user and comment.id in commentlike_id_list:

            comment_dict["is_like"] = True

        comment_dict_list.append(comment_dict)

    data = {

        "user_info": user.to_dict() if user else None,

        "newsClicksList": news_dict_list,

        "news": news.to_dict(),

        "is_collected": is_collected,

        "comments": comment_dict_list
    }

    # 新闻详情页

    return render_template("news/detail.html", data=data)
