from flask import session, current_app, g

import functools

def do_index_class(index):
    # 根据传入的index值返回对应的class属性

    if index == 1:

        return "first"

    elif index == 2:

        return "second"

    elif index == 3:

        return "third"

    else:

        return ""

#只要调用该装饰器就能获取读对应的用户对象数据

def login_user_data(view_func):


    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):

        # 1. 获取user_id
        user_id = session.get("user_id")

        # 2. 根据user_id查询用户对象
        user = None  # type:User

        # 3.将用户对象转换成python字典

        from info.models import User

        try:

            if user_id:
                user = User.query.get(user_id)

        except Exception as e:

            current_app.logger.error(e)

        # 4.保存用户对象给被装饰的视图函数用

        g.user = user

        # 在视图函数中使用g对象获取user对象进而使用

        # 只要在本次请求放范围内（request没有结束）我们就能获取到g对象内容

        return view_func(*args, **kwargs)

    return wrapper
