from datetime import datetime
from crypcial import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    about = db.Column(db.String(150))
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(100), nullable=False, default='http://res.cloudinary.com/rjx00349/image/upload/v1539373398/343443856dece3fa.jpg.jpg')
    password = db.Column(db.String(60), nullable=False)
    wallet_money = db.Column(db.Float, nullable=False, default=1000)
    btc = db.Column(db.Float, nullable=False, default=0)
    eth = db.Column(db.Float, nullable=False, default=0)
    eos = db.Column(db.Float, nullable=False, default=0)
    posts = db.relationship('Post', backref='author', lazy=True)
    upvotes = db.relationship('UpvotePost', backref='user', lazy=True)
    discussion = db.relationship('Discussion', backref='author', lazy=True)
    comments = db.relationship('DiscussionComment', backref='author', lazy=True)
    upvotes_comment = db.relationship('UpvoteComment', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}', {self.wallet_money}, eos:{self.eos})"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    upvotes = db.relationship('UpvotePost', backref='post', lazy=True)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}', {self.author.username})"


class UpvotePost(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    def __repr__(self):
        return f"id:{self.id}, username:{self.user.username}"


class Discussion(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship('DiscussionComment', backref='discussion', lazy=True)

    def __repr__(self):
        return f"user:{self.author.username}, title:{self.title}"


class DiscussionComment(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    discussion_id = db.Column(db.Integer, db.ForeignKey('discussion.id'), nullable=False)
    upvotes = db.relationship('UpvoteComment', backref='discussion_comment', lazy=True)

    def __repr__(self):
        return f"content:{self.content}, user:{self.author.username}"


class UpvoteComment(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    discussion_comment_id = db.Column(db.Integer, db.ForeignKey('discussion_comment.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"id:{self.id}, username:{self.user.username}"
