'''
from flask import render_template, session, redirect, url_for, current_app
from .. import db
from ..models import User
from ..email import send_email
from . import main
from .forms import NameForm


@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username = form.name.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
            if current_app.config['FLASKY_ADMIN']:
                send_email(current_app.config['FLASKY_ADMIN'], 'New User',
                           'mail/new_user', user=user)
        else:
            session['known'] = True
        session['name'] = form.name.data
        return redirect(url_for('.index'))
    return render_template('index.html',
                           form=form, name=session.get('name'),
                           known=session.get('known', False))
'''

#首页、用户页、编辑个人资料、博客文章单页、编辑单页文章

from flask import render_template,flash,redirect,url_for,request,abort
from flask_login import login_required,current_user
from .. import db
from .forms import EditProfileForm,PostForm
from . import main
from ..models import User,Post


@main.route('/',methods = ['GET','POST'])
def index():
    form = PostForm()
    if  form.validate_on_submit():
        post = Post(body = form.body.data,author = current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.index'))
    #posts = Post.query.order_by(Post.timestamp.desc()).all()

    # 通过request.args.get获取一个url所带的参数，这里是获取参数"paga"的值，如果不存在则返回默认值1
    page = request.args.get('page',1,type = int)
    # paginate() return per_page items from page
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page,per_page=5,error_out=False
    )
    posts = pagination.items   # items代表当前页面的项目
    return render_template('index.html',form = form , posts = posts, pagination = pagination)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username = username).first()
    if user is None:
        abort(404)
    #posts = user.posts.order_by(Post.timestamp.desc()).all()
    page = request.args.get('page',1,type = int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page,per_page=5,error_out=False
    )
    posts = pagination.items
    return render_template('user.html',user = user,posts = posts,pagination = pagination)

@main.route('/edit-profile',methods = ['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data

        db.session.add(current_user._get_current_object())
        db.session.commit()

        flash('Your profile has been updated.')
        return redirect(url_for('main.user',username = current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html',form = form)


@main.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html',posts = [post])


@main.route('/edit/<int:id>',methods = ['GET','POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author:
        abort(404)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash('The post has been updated.')
        return redirect(url_for('.post',id = post.id))
    form.body.data = post.body
    return render_template('edit_post.html',form = form)
	
@main.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username = username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('你已经关注了这个用户。')
        return redirect(url_for('main.user',username = username))
    current_user.follow(user)
    flash('you are now following %s.' % username)
    return redirect(url_for('.user',username = username))

@main.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username = username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('现在你没关注这个用户。')
        return redirect(url_for('.user',username = username))
    current_user.unfollow(user)
    flash('you are not following %s anymore.' % username)
    return redirect(url_for('.user',username = username))

@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username = username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page',1,type = int)
    pagination = user.followers.paginate(page,per_page=5,error_out=False)
    follows = [{'user':item.follower,'timestamp':item.timestamp} for item in pagination.items]
    return render_template('followers.html',user = user,title = "Followers of",
                           endpoint = '.followers',pagination = pagination,follows = follows)

@main.route('/followed-by/<username>')
def followed_by(username):
    user = User.query.filter_by(username = username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page',1,type = int)
    pagination = user.followed.paginate(page,per_page=5,error_out=False)
    follows = [{'user':item.followed,'timestamp':item.timestamp} for item in pagination.items]
    return render_template('followers.html',user = user,title = "Followed by",
                           endpoint = '.followed_by',pagination = pagination,follows = follows)


