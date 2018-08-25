from flask import Flask,session,current_app

from flask_script import Manager

from info import create_app,db

from flask_migrate import Migrate,MigrateCommand

import logging

# 调用工厂方法，传入不同的配置，获取不同的app对象
app = create_app("development")

# 创建manager管理类
manager = Manager(app)

# 创建数据库迁移对象
Migrate(app,db)

# 添加迁移指令到manager对象中
manager.add_command("db",MigrateCommand)

# No changes in schema detected. models.py没有进行关联

if __name__ == '__main__':

    manager.run()
