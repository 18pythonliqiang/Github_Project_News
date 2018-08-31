from flask import Flask, session, current_app

from flask_script import Manager

from info import create_app, db

from flask_migrate import Migrate, MigrateCommand

import logging

# 调用工厂方法，传入不同的配置，获取不同的app对象
from info.models import User

app = create_app("development")

# 创建manager管理类
manager = Manager(app)

# 创建数据库迁移对象
Migrate(app, db)

# 添加迁移指令到manager对象中
manager.add_command("db", MigrateCommand)

# python3 manage.py create_super_user -n "admin" -p"123456"
@manager.option("-n","-name",dest = "name")
@manager.option("-p","-password",dest = "password")
def create_super_user(name,password):

    """创建管理员用户"""

    if not all([name,password]):

        return "参数不足"

    user = User()

    user.is_admin = True

    user.nick_name = name

    user.mobile = name

    user.password = password

    try:

        db.session.add(user)

        db.session.commit()

    except Exception as e:

        current_app.logger.error(e)

        print("创建管理员失败")

    print("创建管理员成功")

if __name__ == '__main__':
    manager.run()
