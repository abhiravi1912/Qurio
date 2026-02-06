from flask import Blueprint, render_template, redirect, url_for
from app.forms import RegisterForm, DoubtForm
from app.models import User, Doubt
from app import db
from flask_login import login_user, logout_user, login_required, current_user
from app.forms import LoginForm
from flask import request



main = Blueprint("main", __name__)

from app.models import Answer
from flask_login import current_user


@main.route("/")
def home():
    query = request.args.get("q")

    if query:
        doubts = Doubt.query.filter(
            (Doubt.title.ilike(f"%{query}%")) |
            (Doubt.description.ilike(f"%{query}%"))
        ).all()
    else:
        doubts = Doubt.query.all()

    return render_template("home.html", doubts=doubts, Answer=Answer)




@main.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("main.home"))
    return render_template("register.html", form=form)

@main.route("/post_doubt", methods=["GET", "POST"])
def post_doubt():
    form = DoubtForm()
    if form.validate_on_submit():
        doubt = Doubt(
            title=form.title.data,
            description=form.description.data,
            category=form.category.data
        )
        db.session.add(doubt)
        db.session.commit()
        return redirect(url_for("main.home"))
    return render_template("post_doubt.html", form=form)

@main.route("/category/<string:category_name>")
def category_filter(category_name):
    doubts = Doubt.query.filter_by(category=category_name).all()
    return render_template("home.html", doubts=doubts)

from app.forms import AnswerForm
from app.models import Answer
from flask_login import login_required

@main.route("/doubt/<int:doubt_id>", methods=["GET", "POST"])

@login_required

def doubt_detail(doubt_id):
    doubt = Doubt.query.get_or_404(doubt_id)
    answers = Answer.query.filter_by(doubt_id=doubt.id).all()
    form = AnswerForm()

    if form.validate_on_submit():
        answer = Answer(
            content=form.content.data,
            doubt_id=doubt.id,
            user_id=current_user.id
        )
        db.session.add(answer)
        db.session.commit()
        return redirect(url_for("main.doubt_detail", doubt_id=doubt.id))

    return render_template(
        "doubt_detail.html",
        doubt=doubt,
        answers=answers,
        form=form
    )

from app.forms import LoginForm

@main.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for("main.home"))

    return render_template("login.html", form=form)



@main.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.home"))

