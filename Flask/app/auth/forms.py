# auth/forms.py 蓝本auth中的登录表单

from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField
from wtforms.validators import DataRequired,Length,Email,  Regexp,EqualTo    #(注册表单的）

from wtforms import ValidationError    #（这两都是新添加，用于注册新用户的）
from ..models import User


class LoginForm(FlaskForm):   # 这是个表单，用来登录的post表单
    email = StringField('Email',validators=[DataRequired(),Length(1,64),Email()])
    password = PasswordField('Password',validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Length(1,64),Email()])
    username = StringField('Username',validators=[DataRequired(),Regexp(
        '^[A-Za-z][A-Za-z0-9_.]*$', 0,
        'Usernames must have only letters, numbers, dots or '
        'underscores'
    )])
    password = PasswordField('Password',validators=[DataRequired(),EqualTo('password2',message='Passwords must match(密码必须匹配).')])
    password2 = PasswordField('Confirm password',validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_email(self,field):
        if User.query.filter_by(email = field.data).first():
            raise ValidationError('邮箱已被注册过')

    def validate_username(self,field):
        if User.query.filter_by(username = field.data).first():
            raise  ValidationError('用户名已被使用')