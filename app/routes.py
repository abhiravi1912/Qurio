from flask import Blueprint, abort, render_template, redirect, url_for
from app.forms import RegisterForm, DoubtForm
from app.models import User, Doubt
from app import db
from flask_login import login_user, logout_user, login_required, current_user
from app.forms import LoginForm
from flask import request
import os
from werkzeug.utils import secure_filename
from flask import current_app



main = Blueprint("main", __name__)

from app.models import Answer
from flask_login import current_user
from app.models import Quiz, Submission, Question
from app.forms import QuizForm, SubmissionForm
from datetime import datetime
from app.models import Quiz, Question, Submission, QuizAnswer

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

        print("FORM SUBMITTED")

        filename = None

        if form.file.data:
            file = form.file.data
            filename = secure_filename(file.filename)

            filepath = os.path.join(
                current_app.config["UPLOAD_FOLDER"],
                filename
            )

            file.save(filepath)

        note = Note(
            title=form.title.data,
            content=form.content.data,
            file=filename,
            faculty_id=current_user.id
        )

        db.session.add(note)
        db.session.commit()

        return redirect(url_for("main.notes"))

    else:
        print("FORM FAILED")
        print(form.errors)

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



                                      ## QUIZES


from flask_login import current_user
from datetime import datetime

@main.route("/create_quiz", methods=["GET", "POST"])
@login_required
def create_quiz():

    if current_user.role != "faculty":
        abort(403)

    if request.method == "POST":

        title = request.form.get("title")
        questions = request.form.getlist("questions[]")

        quiz = Quiz(
            title=title,
            description="",
            faculty_id=current_user.id,
            created_at=datetime.utcnow()
        )

        db.session.add(quiz)
        db.session.commit()

        # Save questions
        for q in questions:
            if q.strip() != "":
                question = Question(
                    text=q,
                    quiz_id=quiz.id
                )
                db.session.add(question)

        db.session.commit()

        return redirect(url_for("main.view_quizzes"))

    return render_template("create_quiz.html")

@main.route("/quizzes")
@login_required
def view_quizzes():

    if current_user.role == "student":
        quizzes = Quiz.query.filter_by(
            faculty_id=current_user.faculty_id
        ).all()
    else:
        quizzes = Quiz.query.filter_by(
            faculty_id=current_user.id
        ).all()

    return render_template("quizzes.html", quizzes=quizzes)



@main.route("/quiz/<int:quiz_id>", methods=["GET", "POST"])
@login_required
def take_quiz(quiz_id):

    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    if request.method == "POST":

        # Create submission
        submission = Submission(
            student_id=current_user.id,
            quiz_id=quiz_id
        )

        db.session.add(submission)
        db.session.commit()

        # Save answers
        for q in questions:
            ans = request.form.get(f"question_{q.id}")

            if ans:
                answer = QuizAnswer(
                    submission_id=submission.id,
                    question_id=q.id,
                    answer_text=ans
                )
                db.session.add(answer)

        db.session.commit()

        return redirect(url_for("main.view_quizzes"))

    return render_template(
        "take_quiz.html",
        quiz=quiz,
        questions=questions
    )


@main.route("/quiz/<int:quiz_id>/submissions")
@login_required
def view_submissions(quiz_id):

    if current_user.role != "faculty":
        abort(403)

    quiz = Quiz.query.get_or_404(quiz_id)

    submissions = Submission.query.filter_by(quiz_id=quiz_id).all()

    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    # collect answers per submission
    submission_data = []

    for sub in submissions:
        answers = QuizAnswer.query.filter_by(submission_id=sub.id).all()

        submission_data.append({
            "submission": sub,
            "answers": answers
        })

    return render_template(
        "submissions.html",
        quiz=quiz,
        questions=questions,
        submission_data=submission_data
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