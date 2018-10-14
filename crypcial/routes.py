import os
import secrets
import requests
import cloudinary as cloud
from cloudinary.uploader import upload
from crypcial import app, db
from flask import render_template, flash, url_for, redirect, request, abort
from crypcial.forms import (LoginForm, RegistrationForm, UpdateAccountForm, InvestForm,
                            RedeemForm, PostForm, DiscussForm, CommentForm)
from crypcial.models import User, Post, UpvotePost, Discussion, DiscussionComment, UpvoteComment
from flask_login import login_user, current_user, logout_user, login_required


cloud.config(
    cloud_name="xmn63338",
    api_key="339766879877636",
    api_secret="xKqUg44xWNvr7lAT_h0pHtkuLgM"
    )


def usd(value):
    return "${:,.2f}".format(value)


def percent(value):
    return "{:,.2f}%".format(value)


def coins(value):
    return "{:.5f}".format(value)


def no_of_upvotes(value):
    upvotes = UpvotePost.query.filter_by(post_id=value).all()
    return len(upvotes)


def no_of_upvotes_comments(value):
    if type(value) != type(5):
        value = value.id
    upvotes = UpvoteComment.query.filter_by(discussion_comment_id=value).all()
    return len(upvotes)


app.jinja_env.filters["usd"] = usd
app.jinja_env.filters["percent"] = percent
app.jinja_env.filters["coins"] = coins
app.jinja_env.filters["no_of_upvotes"] = no_of_upvotes
app.jinja_env.filters["no_of_upvotes_comments"] = no_of_upvotes_comments


@app.route("/")
def home():
    user = current_user
    url = "http://coincap.io/front"
    coins = requests.get(url)
    coins = coins.json()
    coins = coins[:20]
    valid_coins = []
    for coin in coins:
        if coin.get('short') == 'BTC' or coin.get('short') == 'ETH' or coin.get('short') == 'EOS':
            valid_coins.append(coin)
    return render_template('home.html', coins=coins, user=user, request=request)


@app.route('/about')
def about():
    user = current_user
    url = "http://coincap.io/front"
    coins = requests.get(url)
    coins = coins.json()
    coins = coins[:20]
    valid_coins = []
    for coin in coins:
        if coin.get('short') == 'BTC' or coin.get('short') == 'ETH' or coin.get('short') == 'EOS':
            valid_coins.append(coin)
    # print(valid_coins)
    return render_template('about.html', user=user, coins=valid_coins)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check your credentials', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/account/<username>")
@login_required
def account(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('The user does not exist', 'info')
        return redirect(url_for('account', username=current_user.username))
    url = "http://coincap.io/front"
    coins = requests.get(url)
    coins = coins.json()
    coins = coins[:20]
    valid_coins = []
    for coin in coins:
        if coin.get('short') == 'BTC' or coin.get('short') == 'ETH' or coin.get('short') == 'EOS':
            valid_coins.append(coin)
    # image_file = user.image_file
    return render_template('account.html', title='Account',
                           user=user, coins=valid_coins, username=username)


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    image_object = upload(form_picture, public_id=picture_fn)
    return image_object


@app.route("/account/update", methods=['GET', 'POST'])
@login_required
def update_account():
    form = UpdateAccountForm()
    user = current_user
    url = "http://coincap.io/front"
    coins = requests.get(url)
    coins = coins.json()
    coins = coins[:20]
    valid_coins = []
    for coin in coins:
        if coin.get('short') == 'BTC' or coin.get('short') == 'ETH' or coin.get('short') == 'EOS':
            valid_coins.append(coin)
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file.get('url')
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.about = form.about.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.about.data = current_user.about
    image_file = current_user.image_file
    print(image_file)
    return render_template('update_account.html', title='Account', user=user,
                           image_file=image_file, form=form, coins=valid_coins)


@app.route('/user/invest', methods=['GET', 'POST'])
@login_required
def invest():
    form = InvestForm()
    user = current_user
    url = "http://coincap.io/front"
    coins = requests.get(url)
    coins = coins.json()
    valid_coins=[]
    crypto_coins = {}
    for coin in coins:
        if coin.get('short') == 'BTC' or coin.get('short') == 'ETH' or coin.get('short') == 'EOS':
            crypto_coins[coin.get('short')] = coin.get('price')
            valid_coins.append(coin)
    if form.validate_on_submit():
        if form.cryptocurrency.data == 'btc':
            btc = form.amount_to_invest.data / crypto_coins.get('BTC')
            user.btc = user.btc + btc
        if form.cryptocurrency.data == 'eth':
            eth = form.amount_to_invest.data / crypto_coins.get('ETH')
            user.eth = user.eth + eth
        if form.cryptocurrency.data == 'eos':
            eos = form.amount_to_invest.data / crypto_coins.get('EOS')
            user.eos = user.eos + eos
        # print(crypto_coins)
        print(crypto_coins)
        print(user.btc, user.eth, user.eos)
        user.wallet_money = user.wallet_money - form.amount_to_invest.data
        db.session.commit()
        flash('submission successful', 'success')
        return redirect(url_for('invest'))
    return render_template('invest.html', user=user, form=form, coins=valid_coins)


@app.route('/user/redeem', methods=['GET', 'POST'])
@login_required
def redeem():
    form = RedeemForm()
    user = current_user
    url = "http://coincap.io/front"
    coins = requests.get(url)
    coins = coins.json()
    crypto_coins = {}
    valid_coins = []
    for coin in coins:
        if coin.get('short') == 'BTC' or coin.get('short') == 'ETH' or coin.get('short') == 'EOS':
            crypto_coins[coin.get('short')] = coin.get('price')
            valid_coins.append(coin)
    if form.validate_on_submit():
        if form.cryptocurrency.data == 'btc':
            wallet_money = form.coins_to_redeem.data * crypto_coins.get('BTC')
            user.wallet_money = user.wallet_money + wallet_money
            user.btc = user.btc - form.coins_to_redeem.data
        if form.cryptocurrency.data == 'eth':
            wallet_money = form.coins_to_redeem.data * crypto_coins.get('ETH')
            user.wallet_money = user.wallet_money + wallet_money
            user.eth = user.eth - form.coins_to_redeem.data
        if form.cryptocurrency.data == 'eos':
            wallet_money = form.coins_to_redeem.data * crypto_coins.get('EOS')
            user.wallet_money = user.wallet_money + wallet_money
            user.eos = user.eos - form.coins_to_redeem.data
        # print(crypto_coins)
        print(crypto_coins)
        print(user.btc, user.eth, user.eos)
        print(user.wallet_money)
        # user.wallet_money = user.wallet_money + form.amount_to_invest.data
        db.session.commit()
        flash('submission successful', 'success')
        return redirect(url_for('redeem'))
    return render_template('redeem.html', user=user, form=form, coins=valid_coins)


@app.route('/leaderboard')
# @login_required
def leaderboard():
    users = User.query.order_by(User.wallet_money.desc()).all()
    url = "http://coincap.io/front"
    coins = requests.get(url)
    coins = coins.json()
    coins = coins[:20]
    valid_coins = []
    for coin in coins:
        if coin.get('short') == 'BTC' or coin.get('short') == 'ETH' or coin.get('short') == 'EOS':
            valid_coins.append(coin)
    # print(users)
    return render_template('leaderboard.html', user=current_user, users=users, coins=valid_coins)


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    url = "http://coincap.io/front"
    coins = requests.get(url)
    coins = coins.json()
    coins = coins[:20]
    valid_coins = []
    for coin in coins:
        if coin.get('short') == 'BTC' or coin.get('short') == 'ETH' or coin.get('short') == 'EOS':
            valid_coins.append(coin)
    if form.validate_on_submit():
        print(current_user)
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post',
                           form=form, coins=valid_coins)


@app.route("/blog")
def blog():
    posts = Post.query.order_by(Post.id.desc())
    url = "http://coincap.io/front"
    coins = requests.get(url)
    coins = coins.json()
    coins = coins[:20]
    valid_coins = []
    for coin in coins:
        if coin.get('short') == 'BTC' or coin.get('short') == 'ETH' or coin.get('short') == 'EOS':
            valid_coins.append(coin)
    return render_template('blog.html', posts=posts, coins=valid_coins)


@app.route("/post/<int:post_id>")
def post(post_id):
    url = "http://coincap.io/front"
    coins = requests.get(url)
    coins = coins.json()
    coins = coins[:20]
    valid_coins = []
    for coin in coins:
        if coin.get('short') == 'BTC' or coin.get('short') == 'ETH' or coin.get('short') == 'EOS':
            valid_coins.append(coin)
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post, coins=valid_coins)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    url = "http://coincap.io/front"
    coins = requests.get(url)
    coins = coins.json()
    coins = coins[:20]
    valid_coins = []
    for coin in coins:
        if coin.get('short') == 'BTC' or coin.get('short') == 'ETH' or coin.get('short') == 'EOS':
            valid_coins.append(coin)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post', coins=valid_coins)


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route('/post/<int:post_id>/<int:user_id>/upvote', methods=['POST'])
@login_required
def upvote_post(post_id, user_id):
    upvotes = UpvotePost.query.filter_by(post_id=post_id).all()
    users = []
    for upvote in upvotes:
        users.append(upvote.user_id)
    if current_user.id in users:
        flash('You have already upvoted the post', 'info')
        return redirect('blog')
    else:
        upvote = UpvotePost(user_id=user_id, post_id=post_id)
        db.session.add(upvote)
        db.session.commit()
        flash('Post Upvoted', 'success')
        return redirect('blog')


@app.route('/discuss/new', methods=['POST', 'GET'])
@login_required
def new_post_discuss():
    form = DiscussForm()
    url = "http://coincap.io/front"
    coins = requests.get(url)
    coins = coins.json()
    coins = coins[:20]
    valid_coins = []
    for coin in coins:
        if coin.get('short') == 'BTC' or coin.get('short') == 'ETH' or coin.get('short') == 'EOS':
            valid_coins.append(coin)
    if form.validate_on_submit():
        discuss = Discussion(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(discuss)
        db.session.commit()
        flash('Post is up!', 'success')
        return redirect(url_for('discussions'))
    return render_template('create_discussion.html', form=form, coins=valid_coins)


@app.route('/discuss')
def discussions():
    discussions = Discussion.query.order_by(Discussion.id.desc()).all()
    url = "http://coincap.io/front"
    coins = requests.get(url)
    coins = coins.json()
    coins = coins[:20]
    valid_coins = []
    for coin in coins:
        if coin.get('short') == 'BTC' or coin.get('short') == 'ETH' or coin.get('short') == 'EOS':
            valid_coins.append(coin)
    return render_template('discussions.html', discussions=discussions, coins=valid_coins)


@app.route('/discuss/<int:discussion_id>', methods=['POST', 'GET'])
@login_required
def discussion_post(discussion_id):
    discussion = Discussion.query.get(discussion_id)
    comments = DiscussionComment.query.filter_by(discussion_id=discussion_id).all()
    comments.sort(key=no_of_upvotes_comments, reverse=True)
    url = "http://coincap.io/front"
    coins = requests.get(url)
    coins = coins.json()
    coins = coins[:20]
    valid_coins = []
    for coin in coins:
        if coin.get('short') == 'BTC' or coin.get('short') == 'ETH' or coin.get('short') == 'EOS':
            valid_coins.append(coin)
    form = CommentForm()
    if form.validate_on_submit():
        comment = DiscussionComment(content=form.content.data, user_id=current_user.id, discussion_id=discussion_id)
        db.session.add(comment)
        db.session.commit()
        flash('comment submitted', 'success')
        return redirect(url_for('discussion_post', discussion_id=discussion_id))
    return render_template('discussion_post.html', discussion=discussion, form=form, comments=comments, coins=valid_coins)


@app.route('/discussion_post/<int:discussion_id>/<int:discussion_comment_id>/<int:user_id>', methods=['POST'])
@login_required
def upvote_comment(discussion_id, discussion_comment_id, user_id):
    upvotes = UpvoteComment.query.filter_by(discussion_comment_id=discussion_comment_id).all()
    users = []
    for upvote in upvotes:
        users.append(upvote.user_id)
    if current_user.id in users:
        flash('You have already upvoted that comment!', 'info')
        return redirect(url_for('discussion_post', discussion_id=discussion_id))
    else:
        upvote = UpvoteComment(discussion_comment_id=discussion_comment_id, user_id=user_id)
        db.session.add(upvote)
        db.session.commit()
        flash('Comment Upvoted', 'success')
        return redirect(url_for('discussion_post', discussion_id=discussion_id))