from flask import Flask,session

from flask_script import Manager

from info import create_app

# 调用工厂方法，传入不同的配置，获取不同的app对象
app = create_app("development")

# 创建manager管理类
manager = Manager(app)

@app.route("/")

def index():
    # 之前session数据存储在服务器上
    session["name"] = "liqiang"

    return "aaaa"

if __name__ == '__main__':

    manager.run()
