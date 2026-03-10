from flask import Blueprint, abort, render_template, redirect, url_for
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



@main.route("/register", methods=["GET","POST"])
def register():

    form = RegisterForm()

    # load faculty list
    faculty_users = User.query.filter_by(role="faculty").all()
    form.faculty.choices = [(f.id, f.username) for f in faculty_users]

    if form.validate_on_submit():

        faculty_id = None

        if form.role.data == "student" and form.faculty.data:
            faculty_id = form.faculty.data

        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            role=form.role.data,
            faculty_id=faculty_id
        )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("main.login"))

    return render_template("register.html", form=form)


@main.route("/post_doubt", methods=["GET", "POST"])
def post_doubt():
    form = DoubtForm()
    if form.validate_on_submit():
        doubt = Doubt(
            title=form.title.data,
            description=form.description.data,
            category=form.category.data,
            user_id=current_user.id
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

        # Students cannot answer
        if current_user.role != "faculty":
            abort(403)

        # Only assigned faculty can answer
        if doubt.author.faculty_id != current_user.id:
            abort(403)

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



from app.forms import NoteForm
from app.models import Note
from datetime import datetime

@main.route("/upload_note", methods=["GET", "POST"])
@login_required
def upload_note():

    if current_user.role != "faculty":
        abort(403)

    form = NoteForm()

    if form.validate_on_submit():

        note = Note(
            title=form.title.data,
            content=form.content.data,
            faculty_id=current_user.id,
            created_at=datetime.utcnow()
        )

        db.session.add(note)
        db.session.commit()

        return redirect(url_for("main.home"))

    return render_template("upload_note.html", form=form)


from app.models import Note, NoteComment
from app.forms import CommentForm

@main.route("/notes")
@login_required
def notes():

    notes = Note.query.all()

    return render_template("notes.html", notes=notes)


@main.route("/note/<int:note_id>", methods=["GET","POST"])
@login_required
def note_detail(note_id):

    note = Note.query.get_or_404(note_id)

    comments = NoteComment.query.filter_by(note_id=note.id).all()

    form = CommentForm()

    if form.validate_on_submit():

        comment = NoteComment(
            content=form.content.data,
            note_id=note.id,
            user_id=current_user.id
        )

        db.session.add(comment)
        db.session.commit()

        return redirect(url_for("main.note_detail", note_id=note.id))

    return render_template(
        "note_detail.html",
        note=note,
        comments=comments,
        form=form
    )











































## temporary route to set up roles and faculty-student mapping

# @main.route("/setup_roles")
# def setup_roles():
#     faculty = User.query.filter_by(username="MR RAVI").first()

#     if faculty:
#         faculty.role = "faculty"

#         students = User.query.filter(User.username != "MR RAVI").all()
#         for s in students:
#             s.role = "student"
#             s.faculty_id = faculty.id

#         db.session.commit()

#     return "Roles updated successfully!"

    ## http://127.0.0.1:5000/setup_roles