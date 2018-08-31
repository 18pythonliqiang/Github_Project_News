import qiniu

import logging

from flask import current_app

access_key = "W0oGRaBkAhrcppAbz6Nc8-q5EcXfL5vLRashY4SI"

secret_key = "tsYCBckepW4CqW0uHb9RdfDMXRDOTEpYecJAMItL"

def qiniu_image_store(data):

    # 将图片二进制数据上传到骑牛云

    # 构建鉴定对象

    q = qiniu.Auth(access_key, secret_key)

    # 上唇给七牛云的图片名称

    # key = 'hello'

    # 空间名字

    bucket_name = "python-ihome"

    token = q.upload_token(bucket_name)

    try:


        ret, info = qiniu.put_data(token, None, data)

        if ret is not None and info.status_code == 200:

            print('All is OK')

            # 图片名字
            return ret["key"]

        else:

            print(info) # error message in info

    except Exception as e:

        current_app.logger.error(e)

#         自己封装的工具类，异常需要抛出，不能私自解决

        raise e

if __name__ == '__main__':

    file = input("请输入文件路径：")

    with open(file,"rb") as f:

        qiniu_image_store(f.read())


