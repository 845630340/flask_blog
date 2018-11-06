# app/main/__init__.py 创建index和错误处理路由的蓝本

from flask import Blueprint

main = Blueprint('main',__name__) # 创建蓝本

from . import views,errors,forms  # 导入蓝本文件夹中的所有文件