import random
from datetime import datetime, timedelta, timezone
from market import app, db, bcrypt, schedule
from flask import render_template, redirect, url_for, flash, session, request
from market.models import Currency, User, UserCurrency
from market.forms import RegisterForm, LoginForm, PurchaseItemForm, SellItemForm
from flask_login import login_user, logout_user, login_required, current_user


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/my_purchases")
@login_required
def my_purchases():
    sell_form = SellItemForm()
    items = UserCurrency.query.filter_by(user_id=current_user.id).all()
    if items:
        return render_template("purchases.html", items=items, sell_form=sell_form)
    else:
        items = ["You haven't bought anything yet"]
        return render_template("purchases.html", items=items, sell_form=sell_form)


@app.route("/spin", methods=["GET", "POST"])
@login_required
def spin():
    if request.method == "POST":
        time_since_last_spin = datetime.utcnow() - current_user.last_spin
        if time_since_last_spin < timedelta(minutes=1):
            flash(f"You can only spin the wheel once per minute. Please wait {60 - time_since_last_spin.seconds} seconds.", "info")
            return redirect(url_for('spin'))
        choice = int(random.uniform(100, 500))
        current_user.budget += choice
        db.session.commit()
        current_user.last_spin = datetime.utcnow()
        db.session.commit()
        flash(f"Congratulation! You've won {choice} $", "success")
        return redirect(url_for('spin'))

    return render_template("spinning_wheel.html")


@app.route("/spinning_wheel")
@login_required
def spinning_wheel():
    return render_template("spinning_wheel.html")


@schedule.task('cron', id='update_prices', minute='*/1')
def update_prices():
    with app.app_context():
        currencies = Currency.query.all()
        for currency in currencies:
            change_percent = random.uniform(-5, 5)
            change_factor = 1 + (change_percent / 100)
            new_price = currency.price * change_factor
            currency.price = round(new_price, 2)
            currency.increase = str(round(change_percent, 2)) + "%"
        db.session.commit()


@schedule.task('cron', id='update_count', minute='*/1')
def update_count():
    with app.app_context():
        currencies = Currency.query.all()
        for currency in currencies:
            if currency.quantity <= 20:
                currency.quantity += int(random.uniform(30, 50))
        db.session.commit()


@app.route("/shop")
@login_required
def shop():
    purchase_form = PurchaseItemForm()
    currencies = Currency.query.all()
    return render_template("shop.html", currencies=currencies, purchase_form=purchase_form)


@app.route('/purchase/<int:currency_id>', methods=['POST'])
@login_required
def purchase_currency(currency_id):
    purchase_form = PurchaseItemForm()
    currency = Currency.query.get(int(currency_id))
    try:
        current_user.buy_currency(currency, purchase_form.quantity.data)
        flash('Purchase successful', 'success')
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for('shop'))


@app.route("/sell/<int:currency_id>", methods=["POST"])
@login_required
def sell_currency(currency_id):
    sell_form = SellItemForm()
    currency = Currency.query.get(currency_id)
    try:
        user_currency = UserCurrency.query.filter_by(user_id=current_user.id, currency_id=currency_id).first()
        if user_currency and user_currency.quantity >= sell_form.quantity.data and not int(sell_form.quantity.data) <= 0:
            current_user.sell_currency(currency, sell_form.quantity.data)
            flash("Successfully sold currency", "success")
    except ValueError:
        flash("Wrong amount to sell", "danger")
    return redirect(url_for("my_purchases"))


@app.route("/register", methods=["GET", "POST"])
def register():
    logout_user()
    form = RegisterForm()
    if form.validate_on_submit():
        password_hashed = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user_to_add = User(username=form.username.data, email=form.email.data, password_hashed=password_hashed)
        db.session.add(user_to_add)
        db.session.commit()
        login_user(user_to_add)
        flash("Successfully registered!", "success")
        return redirect(url_for("shop"))
    if form.errors != {}:
        for error in form.errors.values():
            flash(f"{error[0]}", category="danger")
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and bcrypt.check_password_hash(attempted_user.password_hashed, form.password.data):
            login_user(attempted_user)
            return redirect(url_for("shop"))
        else:
            flash("Username or password is incorrect", "danger")

    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    flash("You've been successfully logged out!", "info")
    return redirect(url_for('home'))