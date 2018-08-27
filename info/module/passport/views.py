from . import passport_bp

from flask import request, abort, make_response, json, jsonify, current_app,session

from info.utlis.captcha.captcha import captcha

from info.utlis.response_code import RET

from info import redis_store, constants,db

import re

from info.models import User

from info.lib.yuntongxun.sms import CCP

import random

from datetime import datetime


# 127.0.0.1:5000/passport/image_code

@passport_bp.route("/image_code")
def get_imgecode():
    """获取验证码图片"""

    # 1.获取参数

    # a.获取前端传上来的uuid编码，imageCodeId
    imageCodeId = request.args.get("imageCodeId", "")

    # 2.校验参数

    # a.判断uuid编码是否为空

    if not imageCodeId:
        abort(404)

    # 3.逻辑处理

    # a.获取生成验证码图片对象,获取真实的验证码

    # ('fXZJN4AFxHGoU5mIlcsdOypa', 'JGW9', '\x89PNG\r\n\x1a\n\x00\x00\x00\r...')

    name, text, image = captcha.generate_captcha()

    # b.将图片验证码真实的之使用编码存储到redis
    try:
        # eg:imagecode_uuid:dadw
        redis_store.set("imagecode_%s" % imageCodeId, text, ex=constants.IMAGE_CODE_REDIS_EXPIRES)

    except Exception as e:

        abort(500)

    # 4.返回值处理
    # a.将图片对象返回给前端展示

    # 创建响应对象
    response = make_response(image)

    # 设置响应对象中响应头内容的类型

    response.headers["Content-Type"] = "image/jpeg"

    # 返回响应对象

    return response


@passport_bp.route("/sms_code",methods = ["POST"])
def send_sms():
    """发送短信验证的接口"""

    # 1.获取参数
    # a.手机号码，用户填写的验证码，UUID随机编号

    # parem_dict = json.loads(request.data)

    parem_dict = request.json

    mobile = parem_dict.get("mobile")

    image_code = parem_dict.get("image_code")

    image_code_id = parem_dict.get("image_code_id")

    # 2.校验参数

    # a.手机号码，用户填写的验证码，UUID随机编号判断空校验

    if not all([mobile, image_code, image_code_id]):
        # 返回错误的json字符串
        return jsonify(errno=RET.PARAMERR, errmsg="参数不足")

    # b.手机格式校验

    if not re.match("1[356789][0-9]{9}", mobile):
        # 返回错误的json字符串

        return jsonify(errno=RET.PARAMERR, errmsg="手机格式错误")

    # 3.逻辑处理

    # a.根据image_code__id编号去redis中获取验证码的真实的值

    try:
        # 在redis创建的时候设置decode_response = True ,转字符串，不然是byte

        real_image_code = redis_store.get("imagecode_%s" % image_code_id)

        # b.real_image_code验证码是否有数值：删除redis在中储存的值，防止多次利用real_image_code验证

        if real_image_code:
            redis_store.delete(real_image_code)

    except Exception as e:

        current_app.logger.error(e)

        return jsonify(errno=RET.DATAERR, errmsg="查询验证码异常")

    # c.没有数值代表redis中的验证码过期-----调用前端的再次生成图片

    if not real_image_code:
        return jsonify(errno=RET.NODATA, errmsg="验证码过期")

    # d.比较用户填写的image_code和后端真是的real_image_code进行对比

    if image_code.lower() != real_image_code.lower():
        # f.验证码填写错误

        return jsonify(errno=RET.DATAERR, errmsg="验证码填写错误")

    # g.根据手机号码验证查询手机号码是否验证
    try:

        user = User.query.filter_by(mobile=mobile).first()

        if user:
            # 表示已经注册过了

            return jsonify(errno=RET.DATAEXIST, errmsg="手机号已经注册过了")

    except Exception as e:

        # current_app.logger 记录日志

        current_app.logger.error(e)

        return jsonify(errno=RET.DATAERR, errmsg="数据库查询用户对象异常")

    # h.调用云通讯的SDK发送短信验证码

    # i.生成一个6个数字的随机短信内容

    sms_code = random.randint(0, 999999)

    sms_code = "%06d" % sms_code

    result = CCP().send_template_sms(mobile, [sms_code, constants.IMAGE_CODE_REDIS_EXPIRES / 60], 1)

    # e.成功：发送短信验证

    if result != 0:
        return jsonify(errno=RET.THIRDERR, errmsg="发送短信验证码失败")

    # j.发送短信验证码成功，存储短信验证码到redis

    try:

        redis_store.set("SMS_%s" % mobile, sms_code, ex=constants.SMS_CODE_REDIS_EXPIRES)

    except Exception as e:

        current_app.logger.error(e)

        return jsonify(errno=RET.DATAERR, errmsg="保存短信验证码到数据库异常")

    # 4.返回值处理
    # a.告诉前端发送短信验证码成功，注意查收

    return jsonify(errno=RET.OK, errmsg="发送短信验证码成功")

# 127.0.0.1:5000/passport/register,POST请求方式
@passport_bp.route("/register",methods = ["POST"])
def register():

    """用户注册接口"""

#   1.获取参数
#   a.手机号码，用户填写的短信验证码，密码（没有加密）
    params_dict = request.json

    mobile = params_dict.get("mobile") #手机号码

    smscode = params_dict.get("smscode") #用户填写的短信验证码

    password = params_dict.get("password") #密码

#   2.校验参数

#   a.非空判断
    if not all([mobile,smscode,password]):

        return jsonify(errno = RET.PARAMERR , errmsg = "参数不足")

#    b.手机号码格式校验

    if not re.match("^1[356789][0-9]{9}$",mobile):

        return jsonify(errno = RET.PARAMERR , errmsg = "手机号码格式错误")

#   3.逻辑处理

#   a.根据手机号拼接SMS_13065130350这个key取货去真实的短信验证码

    try:

        real_sms_code = redis_store.get("SMS_%s"%mobile)

        if real_sms_code:

            redis_store.delete("SMS_%s"%mobile)

    except Exception as e:

        current_app.logger.error(e)

        return jsonify(errno = RET.DBERR , errmsg = "获取短信验证数据库异常")

    # 不想对此校验同一个短信验证码，当取出真实值的时候把把从数据库删除

    if not real_sms_code:

#         没有值表示过期了

        return jsonify(errno = RET.NODATA , errmsg = "短信验证已过期")

#   b.对比用户添加的短信验证号码和真实的验证码对比
    if smscode != real_sms_code:

        return jsonify(errno = RET.PARAMERR , errmsg = "短信验证填写错误")

#   c.根据User模型创建用户对象，保存到数据库

    # 创建用户对象给属性赋值
    user = User()

    user.mobile = mobile

    user.nick_name = mobile

    # TODO: 需要将密码加密后赋值给password_hash

    # user.password_hash
    # user.make_password_hash(password)

    user.password = password

    # 记录用户最后一次登录时间
    user.last_login = datetime.now()

    try:

        db.session.add(user)

        db.session.commit()

    except Exception as e:

        current_app.logger.error(e)

#         回滚
        db.session.rollback()

        return jsonify(errno=RET.DBERR, errmsg="保存用户数据到数据库异常")

#   d.用户注册成功，第一次给用户自动登录，使用session存储用户信息

        session["user_id"] = user.id

        session["mobile"] = user.mobile

        session["nick_name"] = user.nick_name

#     4.返回值处理

    return jsonify(errno=RET.OK, errmsg="注册成功")




