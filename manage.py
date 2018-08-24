from flask import Flask,session,current_app

from flask_script import Manager

from info import create_app

import logging

# 调用工厂方法，传入不同的配置，获取不同的app对象
app = create_app("development")

# 创建manager管理类
manager = Manager(app)

if __name__ == '__main__':

    manager.run()
