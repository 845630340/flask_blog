# app/auth/views.py  认证路由:登入、登出、注册

from flask import render_template,redirect,request,url_for,flash
from . import auth

from flask_login import login_user,logout_user,login_required,current_user
from ..models import User
from .forms import LoginForm ,RegistrationForm # 引入登录表单类，用于生成实例form

from .. import db
from ..email import send_email



@auth.route('/login',methods = ['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        #提交登录表单并验证后，从数据库中查用户对象，如果数据库中有该用户并且密码正确，则登录；否则flash无效。
        user = User.query.filter_by(email = form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remember_me.data)
            #next = request.args.get('next')
            #if next is None or not next.startswith('/'):
                #next = url_for('main.index')     # 这个是当你登录之后返回的页面，可以改为url_for('main.user')
            return redirect(url_for('main.index'))

        flash('无效的用户名或者密码')
    return render_template('auth/login.html',form = form)



@auth.route('/logout')
@login_required    # 这个修饰器，是限制该url只有登录的用户才能访问。
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))




@auth.route('/register',methods = ['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        #注册表单提交并验证后，将表单里的内容字段保存到数据库中。
        user = User()
        user.email = form.email.data
        user.username = form.username.data
        user.password = form.password.data

        db.session.add(user)
        db.session.commit()
        #token = user.generate_confirmation_token()
        #send_email(user.email,'Confirm Your Account','auth/email/confirm',user = user,token = token)

        #flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html',form = form)

'''
@auth.route('/confirm/<token>')  # 确认用户账户
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('you have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))


@auth.before_app_request    # 过滤未确认的账户
def before_request():
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.endpoint \
            and request.blueprint != 'auth' \
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')  #未确认页面的路由
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')



@auth.route('/confirm')    # 重新发送邮件确认账户
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))

@auth.route('/email/comfirm')
def confirm_email():
    form = RegistrationForm()
    user = User(username = form.username.data)
    return render_template('auth/email/confirm.html',user = user)
'''


'''
@auth.before_app_first_request  #会在每次请求前运行，调用ping()函数，更新已登录用户的访问时间，
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
'''


'''
# 引入一个修饰器，为了保护路由只让用户访问；如果未认证的用户访问这个路由，Flask-Login会/
# 拦截请求，把用户发往登录页面。
@auth.route('/secret')
@login_required
def secret():
    return 'Only authenticated user are allowed!'
'''