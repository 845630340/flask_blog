# 创建一个表单类

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,TextAreaField
from wtforms.validators import DataRequired,Length

from flask_pagedown.fields import PageDownField

#这个目前用不上了。。。
class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit',validators=[DataRequired()])

class EditProfileForm(FlaskForm):
    name = StringField('Real name',validators=[Length(0,64)])
    location = StringField('Location',validators=[Length(0,64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

class PostForm(FlaskForm):
    #body = TextAreaField("what's on your mind ?",validators=[DataRequired()])
    body = PageDownField("what's on your mind ?",validators=[DataRequired()])
    submit = SubmitField('Submit')