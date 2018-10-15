from werkzeug.security import generate_password_hash,check_password_hash
from . import db,login_manager
from flask_login import UserMixin
from datetime import datetime

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app

from markdown import markdown
import bleach


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(64),unique = True)
    users = db.relationship('User',backref = 'role',lazy = 'dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name
		
class Follow(db.Model):
	__tablename__ = 'follows'
	# 粉丝id
	follower_id = db.Column(db.Integer,db.ForeignKey('users.id'),primary_key = True)
	# 我关注的人的id
	followed_id = db.Column(db.Integer,db.ForeignKey('users.id'),primary_key = True)
	timestamp = db.Column(db.DateTime,default = datetime.now)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean,default = False)

    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(),default = datetime.now )
    last_seen = db.Column(db.DateTime(),default = datetime.now)

    posts = db.relationship('Post',backref = 'author',lazy = 'dynamic')
	
	# 我关注的人
	followed = db.relationship('Follow',
								foreign_keys = [Follow.follower_id],
								backref = db.backref('follower',lazy = 'joined'),
								lazy = 'dynamic',
								cascade = 'all,delete-orphan')
	# 追随者，粉丝
	follower = db.relationship('Follow',
								foreign_keys = [Follow.followed_id],
								backref = db.backref('followed',lazy = 'joined'),
                                lazy = 'dynamic',
                                cascade = 'all,delete-orphan')

    '''
    # 生成一个令牌，有效期为一小时
    def generate_confirmation_token(self,expiration = 3600):
        s = Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'confirm':self.id})

    # 验证令牌，如果检验通过，则把表中的confirmed属性设为True
    def confirm(self,token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        self.confirmed = True
        db.session.add(self)
        return True
    '''

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def ping(self):   # 刷新用户的最后访问时间
        self.last_seen = datetime.now()
        db.session.add(self)
		
	def follow(self,user):
        if not self.is_following(user):
            f = Follow(follower = self,followed = user)
            db.session.add(f)

    def unfollow(self,user):
        f = self.followed.filter_by(followed_id = user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self,user):
        if user.id is None:
            return False
        return self.followed.filter_by(followed_id = user.id).first() is not None

    def is_followed_by(self,user):
        if user.id is None:
            return False
        return self.followers.filter_by(follower_id = user.id).first() is not None


    def __repr__(self):
        return '<User %r>' % self.username

    '''
    @staticmethod
    def generate_fake(count = 100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(
                email = forgery_py.internet.email_address(),
                username = forgery_py.internet.user_name(),
                password = forgery_py.lorem_ipsum.word(),
                confirmed = True,
                name = forgery_py.name.full_name(),
                location = forgery_py.address.city(),
                about_me = forgery_py.lorem_ipsum.sentence(),
                member_since = forgery_py.date.date(True)
            )
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
    '''


# LoginManager初始化之后，在models中定义一个回调函数，在登录验证时，从数据库中加载用户对象
# 接收一个用户标识符，如果能找到用户，函数返回用户对象，否则返回None
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer,primary_key = True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime(),index = True,default = datetime.now)
    author_id = db.Column(db.Integer,db.ForeignKey('users.id'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

db.event.listen(Post.body, 'set', Post.on_changed_body)

'''
    @staticmethod
    def generate_fake(count = 100):
        from random import seed,randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0,user_count-1)).first()
            p = Post(body = forgery_py.lorem_ipsum.sentences(randint(1,3)),
                     timestamp = forgery_py.date.date(True),
                     author = u)
            db.session.add(p)
            db.session.commit()
'''