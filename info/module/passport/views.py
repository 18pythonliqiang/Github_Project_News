from . import passport_bp

from flask import request, abort,make_response

from info.utlis.captcha.captcha import captcha

from info import redis_store, constants


# 127.0.0.1:5000/passport/image_code

@passport_bp.route("/image_code")
def get_imgecode():
    """获取验证码图片"""

    # 1.获取参数

    # a.获取前端传上来的uuid编码，imageCodeId
    imageCodeId = request.args.get("imageCodeId","")

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
