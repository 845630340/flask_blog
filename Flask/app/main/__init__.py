# app/main/__init__.py 创建index和错误处理路由的蓝本

from flask import Blueprint

main = Blueprint('main',__name__)

from . import views,errors,forms